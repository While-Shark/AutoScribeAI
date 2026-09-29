"""Project inventory import and immutable planned-coverage accounting."""
import hashlib
import json
from collections import Counter
from pathlib import Path

from .state import atomic_json, digest
from .validation import ValidationError, read_json, validate, validate_manual


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_inventory(data, config):
    validate(data, 'inventory')
    if data['projectId'] != config['project']['id']:
        raise ValidationError('清单项目 ID 与运行配置不一致')
    if data['projectVersion'] != config['project'].get('version', ''):
        raise ValidationError('清单项目版本与运行配置不一致')
    if data['scope'] != config['scope']:
        raise ValidationError('清单范围必须保留运行配置中的原始范围')
    roles = set(config['roles'])
    modules = {m['id']: m for m in data['modules']}
    features = {f['id']: f for f in data['features']}
    if len(modules) != len(data['modules']) or len(features) != len(data['features']):
        raise ValidationError('模块和功能 ID 必须唯一')
    for feature in features.values():
        if feature['moduleId'] not in modules:
            raise ValidationError('功能必须归属于已声明模块')
        if not set(feature['roles']) <= roles:
            raise ValidationError('功能只能使用运行配置中声明的角色')
    ids = set(modules) | set(features)
    if len(ids) != len(modules) + len(features):
        raise ValidationError('模块与功能之间也必须使用不同 ID')
    workflow_ids = set()
    for workflow in data['workflows']:
        if workflow['id'] in ids or workflow['id'] in workflow_ids:
            raise ValidationError('模块、功能和流程 ID 必须全局唯一')
        workflow_ids.add(workflow['id'])
        feature = features.get(workflow['featureId'])
        if feature is None:
            raise ValidationError('候选流程必须归属于已声明功能')
        if workflow['role'] not in feature['roles']:
            raise ValidationError('候选流程角色不属于功能适用角色')
    scope_labels = [item['scope'] for item in data['scopeItems']]
    if len(scope_labels) != len(set(scope_labels)) or set(scope_labels) != set(config['scope']):
        raise ValidationError('清单必须逐项映射运行配置中的全部范围')
    mapped_workflows = set()
    for item in data['scopeItems']:
        if not item['workflowIds'] and not item.get('reason'):
            raise ValidationError('暂无候选流程的范围项必须记录原因')
        if not set(item['workflowIds']) <= workflow_ids:
            raise ValidationError('范围映射引用了不存在的候选流程')
        mapped_workflows.update(item['workflowIds'])
    if workflow_ids - mapped_workflows:
        raise ValidationError('每条候选流程必须归入至少一项用户范围')
    return modules, features


def inventory_to_manual(inventory, config):
    modules, features = validate_inventory(inventory, config)
    timestamp = inventory.get('discoveredAt', '')
    workflows = []
    for candidate in inventory['workflows']:
        workflows.append({
            'id': candidate['id'], 'featureId': candidate['featureId'],
            'role': candidate['role'], 'goal': candidate['goal'],
            'preconditions': candidate['preconditions'],
            'successCriteria': candidate['successCriteria'],
            'status': 'unverified', 'reason': '尚未在目标环境中实际执行并核验', 'stepIds': [],
        })
    chapters = []
    for module in inventory['modules']:
        ids = [w['id'] for w in workflows if features[w['featureId']]['moduleId'] == module['id']]
        if ids:
            chapters.append({'id': 'chapter-' + module['id'], 'moduleId': module['id'],
                             'title': module['name'], 'purpose': '待根据实际界面观察补充', 'workflowIds': ids})
    return {
        'schemaVersion': '0.1',
        'project': {**config['project'], 'version': inventory['projectVersion']},
        'title': config['project']['name'] + ' 操作手册', 'roles': config['roles'],
        'modules': inventory['modules'], 'features': inventory['features'],
        'workflows': workflows, 'steps': [], 'evidence': [], 'chapters': chapters,
        'limitations': ['当前内容来自项目清单；所有流程均未验证。'] if workflows else ['清单内未发现候选流程。'],
    }


def create_coverage_plan(inventory_path, config_path, plan_path):
    inventory_path, config_path, plan_path = map(Path, (inventory_path, config_path, plan_path))
    inventory = read_json(inventory_path)
    config = validate(read_json(config_path), 'project')
    modules, features = validate_inventory(inventory, config)
    plan = {
        'schemaVersion': '0.1', 'projectId': config['project']['id'],
        'projectVersion': inventory['projectVersion'],
        'scopeHash': digest(config['scope']), 'scope': config['scope'],
        'scopeItems': inventory['scopeItems'],
        'inventorySha256': file_hash(inventory_path),
        'modules': [{'id': item['id'], 'name': item['name']} for item in inventory['modules']],
        'features': [{'id': item['id'], 'moduleId': item['moduleId']} for item in inventory['features']],
        'workflows': [{'id': item['id'], 'featureId': item['featureId'], 'role': item['role'],
                       'goal': item['goal'], 'source': item['source']} for item in inventory['workflows']],
    }
    validate(plan, 'coverage-plan')
    atomic_json(plan_path, plan)
    return plan


def coverage_report(plan_path, inventory_path, config_path, manual_path, output_path):
    plan_path, inventory_path, config_path, manual_path, output_path = map(Path, (plan_path, inventory_path, config_path, manual_path, output_path))
    plan = validate(read_json(plan_path), 'coverage-plan')
    config = validate(read_json(config_path), 'project')
    inventory = read_json(inventory_path)
    if file_hash(inventory_path) != plan['inventorySha256']:
        raise ValidationError('项目清单在计划创建后发生变化；需复核并显式创建新覆盖计划')
    if digest(config['scope']) != plan['scopeHash'] or config['scope'] != plan['scope']:
        raise ValidationError('运行范围已变化；请创建新运行并重新确认覆盖计划')
    if (config['project']['id'], config['project'].get('version', '')) != (plan['projectId'], plan['projectVersion']):
        raise ValidationError('项目或版本与覆盖计划不一致')
    validate_inventory(inventory, config)
    manual = read_json(manual_path)
    if manual.get('project', {}).get('id') != plan['projectId'] or manual.get('project', {}).get('version', '') != plan['projectVersion']:
        raise ValidationError('手册项目版本与覆盖计划不一致')
    expected = {w['id'] for w in plan['workflows']}
    actual = {w['id'] for w in manual.get('workflows', []) if isinstance(w, dict) and isinstance(w.get('id'), str)}
    if expected != actual:
        raise ValidationError('手册流程必须与原计划完全对应；不可静默删除、遗漏或新增流程')
    if {m['id'] for m in manual.get('modules', []) if isinstance(m, dict) and 'id' in m} != {m['id'] for m in plan['modules']}:
        raise ValidationError('手册模块必须与原始清单一致')
    if {f['id'] for f in manual.get('features', []) if isinstance(f, dict) and 'id' in f} != {f['id'] for f in plan['features']}:
        raise ValidationError('手册功能必须与原始清单一致')
    manual = validate_manual(manual, manual_path.parent)
    statuses = {w['id']: w['status'] for w in manual['workflows']}
    totals = Counter(statuses.values())
    denominator = len(expected)
    report = {
        'schemaVersion': '0.1', 'projectId': plan['projectId'], 'projectVersion': plan['projectVersion'],
        'scope': plan['scope'], 'scopeItems': [], 'inventorySha256': plan['inventorySha256'],
        'planned': denominator, 'verified': totals['verified'],
        'blocked': totals['blocked'], 'unverified': totals['unverified'], 'pending': totals['pending'],
        'coverage': totals['verified'] / denominator if denominator else None,
        'coverageDisplay': f"{totals['verified']}/{denominator}" if denominator else '不适用（无计划流程）',
        'modules': [],
    }
    for scope_item in plan['scopeItems']:
        counts = Counter(statuses[wid] for wid in scope_item['workflowIds'])
        count = len(scope_item['workflowIds'])
        report['scopeItems'].append({
            'scope': scope_item['scope'], 'planned': count, 'verified': counts['verified'],
            'blocked': counts['blocked'], 'unverified': counts['unverified'], 'pending': counts['pending'],
            'coverage': counts['verified'] / count if count else None,
            'coverageDisplay': f"{counts['verified']}/{count}" if count else '不适用（无计划流程）',
        })
    module_names = {m['id']: m['name'] for m in plan['modules']}
    feature_modules = {f['id']: f['moduleId'] for f in plan['features']}
    workflow_features = {w['id']: w['featureId'] for w in plan['workflows']}
    for module in plan['modules']:
        ids = [wid for wid, fid in workflow_features.items() if feature_modules[fid] == module['id']]
        counts = Counter(statuses[i] for i in ids)
        report['modules'].append({
            'id': module['id'], 'name': module_names[module['id']], 'planned': len(ids),
            'verified': counts['verified'], 'blocked': counts['blocked'],
            'unverified': counts['unverified'], 'pending': counts['pending'],
            'coverage': counts['verified'] / len(ids) if ids else None,
            'coverageDisplay': f"{counts['verified']}/{len(ids)}" if ids else '不适用（无计划流程）',
        })
    atomic_json(output_path, report)
    return report
