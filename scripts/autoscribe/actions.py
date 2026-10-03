"""Write-action journal that requires explicit result checks before retry."""
import hashlib
import os
from contextlib import contextmanager
from pathlib import Path

from .state import atomic_json, now
from .validation import ValidationError, read_json, reject_secrets, validate

WRITE_ACTIONS = frozenset({
    'create-test-data', 'update-test-data', 'delete-test-data',
    'publish', 'send', 'change-permissions', 'pay',
})


@contextmanager
def action_lock(run):
    lock = Path(run) / '.actions.lock'
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValidationError('写操作日志正在更新；若进程已退出，核实无写入后再移除 .actions.lock') from None
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink()


def action_id(workflow_id, step_id, operation, target_ref):
    stable = '\0'.join((workflow_id, step_id, operation, target_ref))
    return 'act-' + hashlib.sha256(stable.encode('utf-8')).hexdigest()[:32]


def load_actions(run):
    path = Path(run) / 'actions.json'
    if not path.exists():
        return {'schemaVersion': '0.1', 'actions': [], 'events': []}
    return validate(read_json(path), 'actions')


def begin_action(run, workflow_id, step_id, operation, target_ref):
    """Journal an action immediately before a browser write; never invokes a browser."""
    from .state import load
    with action_lock(run):
        manifest = load(run)
        if operation not in WRITE_ACTIONS:
            raise ValidationError('此日志仅管理可能产生副作用的写操作')
        if operation not in manifest['config']['allowedActions']:
            raise ValidationError('该操作不在项目运行配置的明确授权范围内')
        reject_secrets(target_ref)
        ident = action_id(workflow_id, step_id, operation, target_ref)
        ledger = load_actions(run)
        entry = next((item for item in ledger['actions'] if item['id'] == ident), None)
        if entry and entry['status'] != 'retryable':
            raise ValidationError('该操作已有执行记录；先核对目标结果，并显式标记“确认未执行”后才能重试')
        if manifest['stages']['explore']['status'] != 'running':
            raise ValidationError('只有探索阶段运行时才可登记浏览器动作')
        timestamp = now()
        if entry:
            entry['attempts'] += 1
            entry['status'] = 'begun'
            entry['lastStartedAt'] = timestamp
        else:
            entry = {'id': ident, 'workflowId': workflow_id, 'stepId': step_id,
                     'operation': operation, 'targetRef': target_ref, 'status': 'begun',
                     'attempts': 1, 'firstStartedAt': timestamp, 'lastStartedAt': timestamp}
            ledger['actions'].append(entry)
        ledger['events'].append({'actionId': ident, 'status': 'begun', 'at': timestamp})
        atomic_json(Path(run) / 'actions.json', ledger)
        return {'actionId': ident, 'status': 'begun', 'attempt': entry['attempts'],
                'instruction': '现在执行一次获授权的操作；完成后立即记录结果。恢复时不得重放。'}


def resolve_action(run, ident, resolution, reason=None):
    allowed = {'completed', 'not-applied', 'uncertain'}
    if resolution not in allowed:
        raise ValidationError('结果必须是 completed、not-applied 或 uncertain')
    if resolution != 'completed' and not reason:
        raise ValidationError('未执行或结果不确定时必须记录核查结论')
    with action_lock(run):
        ledger = load_actions(run)
        entry = next((item for item in ledger['actions'] if item['id'] == ident), None)
        if not entry or entry['status'] not in ('begun', 'blocked'):
            raise ValidationError('找不到进行中或中断的操作，不能覆盖历史结果')
        if resolution == 'completed':
            if entry['status'] == 'blocked' and not reason:
                raise ValidationError('恢复后的完成结果必须记录目标系统核查依据')
            entry.update(status='completed', completedAt=now())
            if reason:
                entry['reason'] = reason
            event = {'actionId': ident, 'status': 'completed', 'at': entry['completedAt']}
            if reason:
                event['reason'] = reason
        elif resolution == 'not-applied':
            entry.update(status='retryable', checkedAt=now(), reason=reason)
            event = {'actionId': ident, 'status': 'retryable', 'at': entry['checkedAt'], 'reason': reason}
        else:
            entry.update(status='blocked', checkedAt=now(), reason=reason)
            event = {'actionId': ident, 'status': 'blocked', 'at': entry['checkedAt'], 'reason': reason}
        ledger['events'].append(event)
        atomic_json(Path(run) / 'actions.json', ledger)
        return {'actionId': ident, 'status': entry['status'], 'attempts': entry['attempts']}


def recover_actions(run):
    """Convert work that was in flight during interruption into blocked records."""
    with action_lock(run):
        ledger = load_actions(run)
        changed = False
        for entry in ledger['actions']:
            if entry['status'] == 'begun':
                entry.update(status='blocked', reason='上次任务中断；须核查目标系统状态后再决定')
                timestamp = now()
                entry['checkedAt'] = timestamp
                ledger['events'].append({'actionId': entry['id'], 'status': 'blocked', 'at': timestamp,
                                         'reason': entry['reason']})
                changed = True
        if changed:
            atomic_json(Path(run) / 'actions.json', ledger)
        return ledger
