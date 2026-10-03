"""Compare stable manual IDs without trusting old observations as current proof."""
import hashlib
import json
from pathlib import Path

from .validation import ValidationError, read_json, validate_manual


def _fingerprint(workflow, manual):
    steps = {item['id']: item for item in manual['steps']}
    evidence = {item['id']: item for item in manual['evidence']}
    details = []
    for ident in workflow['stepIds']:
        step = steps[ident]
        details.append({**step, 'evidence': [evidence[eid]['sha256'] for eid in step['evidenceIds']]})
    content = {key: workflow.get(key) for key in ('featureId', 'role', 'goal', 'preconditions', 'successCriteria', 'location', 'status', 'reason')}
    content['steps'] = details
    return hashlib.sha256(json.dumps(content, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def compare_manuals(old_path, new_path):
    old_path, new_path = Path(old_path), Path(new_path)
    old = validate_manual(read_json(old_path), old_path.parent)
    new = validate_manual(read_json(new_path), new_path.parent)
    if old['project']['id'] != new['project']['id']:
        raise ValidationError('只能比较同一项目的手册')
    before = {item['id']: _fingerprint(item, old) for item in old['workflows']}
    after = {item['id']: _fingerprint(item, new) for item in new['workflows']}
    added = sorted(after.keys() - before.keys())
    removed = sorted(before.keys() - after.keys())
    changed = sorted(key for key in before.keys() & after.keys() if before[key] != after[key])
    version_changed = old['project'].get('version') != new['project'].get('version')
    # A version change demands review even when the visible workflow data is identical.
    review = sorted(set(added + changed + (list(after) if version_changed else [])))
    return {
        'projectId': old['project']['id'], 'oldVersion': old['project'].get('version', ''),
        'newVersion': new['project'].get('version', ''), 'versionChanged': version_changed,
        'added': added, 'removed': removed, 'changed': changed,
        'unchanged': sorted((before.keys() & after.keys()) - set(changed)),
        'reviewRequired': review,
        'note': '版本或内容变化需要重新核对实际界面；旧截图和验证结果不会自动沿用。',
    }
