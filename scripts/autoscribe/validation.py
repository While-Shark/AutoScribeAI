"""Schema, provenance, reference and local-asset validation."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator, FormatChecker

SCHEMAS = Path(__file__).resolve().parents[2] / 'schemas'
SECRET_KEY = re.compile(r'password|passwd|secret|token|cookie|authorization|api[-_]?key', re.I)
SECRET_VALUE = re.compile(r'(?i)(?:bearer\s+\S+|(?:password|passwd|token|secret|api[_-]?key|cookie)\s*[:=]\s*\S+)')


class ValidationError(ValueError):
    """A safe diagnostic that never includes the offending input value."""


def reject_secrets(value):
    # Heuristic defense, not a substitute for reviewing screenshots and prose.
    if isinstance(value, dict):
        for key, child in value.items():
            if SECRET_KEY.search(key):
                raise ValidationError('检测到敏感字段；请使用宿主安全登录，不要保存凭据')
            reject_secrets(child)
    elif isinstance(value, list):
        for child in value:
            reject_secrets(child)
    elif isinstance(value, str):
        if SECRET_VALUE.search(value):
            raise ValidationError('检测到疑似敏感值；请脱敏后重试')
        if value.startswith(('https://', 'http://')):
            url = urlsplit(value)
            if url.username or url.password or url.query or url.fragment:
                raise ValidationError('URL 不允许携带凭据、查询参数或片段；请使用脱敏入口 URL')


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except (UnicodeError, json.JSONDecodeError):
        raise ValidationError('无法读取 JSON：请检查 UTF-8 编码和语法') from None


def validate(data, kind):
    reject_secrets(data)
    schema = read_json(SCHEMAS / f'{kind}.schema.json')
    error = next(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(data), None)
    if error:
        # jsonschema.message can echo secrets; only report schema-defined path/rule.
        path = '/'.join(str(p) for p in error.schema_path)
        raise ValidationError(f'{kind} 不符合结构规则：{path}')
    if kind == 'project' and 'url' in data['source']:
        url = urlsplit(data['source']['url'])
        if url.scheme not in ('http', 'https') or not url.hostname:
            raise ValidationError('项目 URL 必须是有效的 HTTP(S) 地址')
    return data


def asset_path(root, relative):
    if '\\' in relative or ':' in relative:
        raise ValidationError('资源路径须为 POSIX 相对路径')
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts:
        raise ValidationError('资源路径不得越过任务目录')
    target = (Path(root) / path).resolve()
    if not target.is_relative_to(Path(root).resolve()):
        raise ValidationError('资源链接不得越过任务目录')
    return target


def validate_manual(data, root):
    validate(data, 'manual')
    maps = {}
    seen = set()
    for group in ('modules', 'features', 'workflows', 'steps', 'evidence', 'chapters'):
        maps[group] = {}
        for item in data[group]:
            if item['id'] in seen:
                raise ValidationError('内容 ID 必须全局唯一')
            seen.add(item['id'])
            maps[group][item['id']] = item

    def get(group, ident):
        if ident not in maps[group]:
            raise ValidationError(f'{group} 存在悬空引用')
        return maps[group][ident]

    for feature in data['features']:
        get('modules', feature['moduleId'])
        if not set(feature['roles']) <= set(data['roles']):
            raise ValidationError('功能角色未在手册中声明')
    for workflow in data['workflows']:
        feature = get('features', workflow['featureId'])
        if workflow['role'] not in feature['roles']:
            raise ValidationError('流程角色不属于功能的适用角色')
        if workflow['status'] in ('blocked', 'unverified') and not workflow.get('reason'):
            raise ValidationError('阻塞/未验证流程必须给出原因')
        steps = [get('steps', ident) for ident in workflow['stepIds']]
        if [s['order'] for s in steps] != list(range(1, len(steps) + 1)):
            raise ValidationError('流程步骤序号必须从 1 连续递增')
        if any(s['workflowId'] != workflow['id'] for s in steps):
            raise ValidationError('流程与步骤的双向引用不一致')
        if workflow['status'] == 'verified':
            if not steps or any(s['source'] != 'observed' or not s.get('actualResult') or not s['evidenceIds'] for s in steps):
                raise ValidationError('已验证流程必须包含实际观察结果及每步截图证据')
    for step in data['steps']:
        workflow = get('workflows', step['workflowId'])
        if step['id'] not in workflow['stepIds']:
            raise ValidationError('存在未归入流程的步骤')
        for ident in step['evidenceIds']:
            if step['id'] not in get('evidence', ident)['stepIds']:
                raise ValidationError('步骤与证据的双向引用不一致')
    for evidence in data['evidence']:
        for ident in evidence['stepIds']:
            if evidence['id'] not in get('steps', ident)['evidenceIds']:
                raise ValidationError('证据与步骤的双向引用不一致')
        path = asset_path(root, evidence['path'])
        if not path.is_file():
            raise ValidationError('截图资源不存在')
        raw = path.read_bytes()
        is_png = raw.startswith(b'\x89PNG\r\n\x1a\n')
        is_jpeg = raw.startswith(b'\xff\xd8\xff')
        if not (is_png or is_jpeg):
            raise ValidationError('首期截图仅支持 PNG/JPEG')
        if hashlib.sha256(raw).hexdigest() != evidence['sha256']:
            raise ValidationError('截图摘要不匹配，需复核证据')
    for chapter in data['chapters']:
        get('modules', chapter['moduleId'])
        for ident in chapter['workflowIds']:
            workflow = get('workflows', ident)
            if get('features', workflow['featureId'])['moduleId'] != chapter['moduleId']:
                raise ValidationError('章节与流程所属模块不一致')
    return data
