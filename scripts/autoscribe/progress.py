"""Durable workflow checkpoints; browser actions are never replayed here."""
from pathlib import Path

from .state import atomic_json, digest, load, locked, now
from .validation import ValidationError, read_json, validate


def _path(run):
    return Path(run) / 'workflow-progress.json'


def _planned(run):
    plan = validate(read_json(Path(run) / 'coverage-plan.json'), 'coverage-plan')
    state = load(run)
    if plan['projectId'] != state['config']['project']['id'] or plan['scopeHash'] != digest(state['config']['scope']):
        raise ValidationError('流程进度与任务范围不一致')
    return state, {workflow['id'] for workflow in plan['workflows']}


def read_progress(run):
    state, planned = _planned(run)
    path = _path(run)
    data = validate(read_json(path), 'workflow-progress') if path.exists() else {
        'schemaVersion': '0.1', 'runId': state['runId'], 'workflows': {},
    }
    if data['runId'] != state['runId'] or not set(data['workflows']) <= planned:
        raise ValidationError('流程进度与当前任务不一致')
    return data


def update_progress(run, workflow_id, status, note):
    if not note or not note.strip():
        raise ValidationError('流程进度必须记录核查说明')
    with locked(run):
        state, planned = _planned(run)
        if workflow_id not in planned:
            raise ValidationError('流程不属于当前覆盖计划')
        if state['stages']['explore']['status'] not in ('running', 'blocked', 'completed'):
            raise ValidationError('只有进入探索阶段后才能更新流程进度')
        data = read_progress(run)
        previous = data['workflows'].get(workflow_id, {}).get('status', 'pending')
        allowed = {
            'pending': {'running', 'blocked'}, 'running': {'completed', 'blocked'},
            'blocked': {'running', 'completed'}, 'completed': set(),
        }
        if status not in allowed[previous]:
            raise ValidationError('流程进度状态跳转无效；已完成的流程需在新任务中复核')
        data['workflows'][workflow_id] = {'status': status, 'note': note.strip(), 'updatedAt': now()}
        validate(data, 'workflow-progress')
        atomic_json(_path(run), data)
        return data


def recover_progress(run):
    """Caller holds the run state lock; mark in-flight work blocked."""
    data = read_progress(run)
    changed = False
    for item in data['workflows'].values():
        if item['status'] == 'running':
            item.update(status='blocked', note='上次流程中断；先核对已执行操作和证据', updatedAt=now())
            changed = True
    if changed:
        atomic_json(_path(run), data)
    return data
