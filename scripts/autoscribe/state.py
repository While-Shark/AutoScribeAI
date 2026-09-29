"""Atomic run state. No browser actions are executed or replayed here."""
import hashlib
import json
import os
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .preflight import probe
from .validation import ValidationError, read_json, reject_secrets, validate

STAGES = ('preflight', 'analyze', 'explore', 'write', 'export', 'verify')
TRANSITIONS = {
    'pending': {'running', 'blocked', 'skipped'},
    'running': {'completed', 'blocked', 'failed'},
    'blocked': {'running', 'skipped'},
    'failed': {'running', 'skipped'},
    'completed': set(), 'skipped': set(),
}


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def atomic_json(path, data):
    reject_secrets(data)
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix='.autoscribe-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def locked(run):
    lock = Path(run) / '.state.lock'
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValidationError('任务正在被写入；若进程已退出，请先确认无写入进程再移除 .state.lock') from None
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink()


def checkpoint(state):
    incomplete = [name for name in STAGES if state['stages'][name]['status'] not in ('completed', 'skipped')]
    return {'schemaVersion': '0.1', 'runId': state['runId'], 'revision': state['revision'],
            'nextStage': incomplete[0] if incomplete else None,
            'completed': [k for k in STAGES if state['stages'][k]['status'] == 'completed'],
            'blocked': [k for k in STAGES if state['stages'][k]['status'] == 'blocked'],
            'replayActions': False}


def save(run, state):
    validate(state, 'manifest')
    # Commit manifest first. If interrupted between writes, resume rebuilds projection.
    atomic_json(Path(run) / 'manifest.json', state)
    projection = validate(checkpoint(state), 'checkpoint')
    atomic_json(Path(run) / 'checkpoint.json', projection)


def initialize(config_path, run, host=None):
    config_path, run = Path(config_path), Path(run)
    config = validate(read_json(config_path), 'project')
    if host is not None:
        validate(host, 'host')
    # Resolve source path once; a different cwd must not silently select another project.
    if 'path' in config['source']:
        config['source']['path'] = str((config_path.parent / config['source']['path']).resolve())
    run.mkdir(parents=True, exist_ok=False)
    capabilities = probe(config, config_path.parent, run, host)
    timestamp = now()
    state = {'schemaVersion': '0.1', 'runId': 'run-' + uuid.uuid4().hex,
             'revision': 0, 'createdAt': timestamp, 'updatedAt': timestamp,
             'configHash': digest(config), 'config': config, 'capabilities': capabilities,
             'stages': {k: {'status': 'pending'} for k in STAGES}, 'events': []}
    state['stages']['preflight'] = {'status': 'completed' if capabilities['mode'] != 'blocked' and capabilities['files'] else 'blocked'}
    if state['stages']['preflight']['status'] == 'blocked':
        state['stages']['preflight']['reason'] = '输入或宿主能力不足，请查看 capabilities'
    with locked(run):
        save(run, state)
    return state


def load(run):
    state = validate(read_json(Path(run) / 'manifest.json'), 'manifest')
    if digest(state['config']) != state['configHash']:
        raise ValidationError('配置摘要不一致；请新建运行并复核旧证据')
    return state


def transition(run, stage, target, reason=None):
    with locked(run):
        state = load(run)
        if stage not in STAGES:
            raise ValidationError('未知阶段')
        current = state['stages'][stage]['status']
        if target not in TRANSITIONS[current]:
            raise ValidationError('不允许此状态跳转；完成的阶段不可重复执行')
        if target in ('blocked', 'failed', 'skipped') and not reason:
            raise ValidationError('阻塞、失败和跳过必须填写原因')
        previous = STAGES[:STAGES.index(stage)]
        if target == 'running' and any(state['stages'][k]['status'] not in ('completed', 'skipped') for k in previous):
            raise ValidationError('前置阶段尚未完成')
        if stage == 'explore' and target == 'running' and not state['capabilities']['canExplore']:
            raise ValidationError('浏览器探索能力不足；更新宿主声明并 resume，或注明原因跳过')
        record = {'status': target}
        event = {'stage': stage, 'from': current, 'to': target, 'at': now()}
        if reason:
            record['reason'] = event['reason'] = reason
        state['stages'][stage] = record
        state['events'].append(event)
        state['revision'] += 1
        state['updatedAt'] = now()
        save(run, state)
        return checkpoint(state)


def resume(run, config_path=None, host=None):
    with locked(run):
        state = load(run)
        if config_path:
            path = Path(config_path)
            config = validate(read_json(path), 'project')
            if 'path' in config['source']:
                config['source']['path'] = str((path.parent / config['source']['path']).resolve())
            if digest(config) != state['configHash']:
                raise ValidationError('输入、范围或项目版本发生变化；请创建新任务并复核旧证据')
        # Never assume browser sessions survive an interrupted host conversation.
        state['capabilities'] = probe(state['config'], '.', run, host)
        for name, item in state['stages'].items():
            if item['status'] == 'running':
                reason = '上次运行中断；核对目标状态与已有结果后才可继续，不自动重放动作'
                item.update(status='blocked', reason=reason)
                state['events'].append({'stage': name, 'from': 'running', 'to': 'blocked', 'at': now(), 'reason': reason})
        state['revision'] += 1
        state['updatedAt'] = now()
        save(run, state)
        return {'checkpoint': checkpoint(state), 'capabilities': state['capabilities'],
                'reviewRequired': ['核对目标版本', '核对登录及角色', '核对截图有效性', '核对已有副作用结果']}
