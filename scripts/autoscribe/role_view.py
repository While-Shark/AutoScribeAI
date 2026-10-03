"""Project a validated manual into one reader role for portable exports."""
from copy import deepcopy

from .validation import ValidationError


def for_role(manual, role):
    if role not in manual['roles']:
        raise ValidationError('指定角色不在手册适用角色中')
    result = deepcopy(manual)
    result['roles'] = [role]
    result['workflows'] = [item for item in manual['workflows'] if item['role'] == role]
    workflow_ids = {item['id'] for item in result['workflows']}
    result['steps'] = [item for item in manual['steps'] if item['workflowId'] in workflow_ids]
    step_ids = {item['id'] for item in result['steps']}
    result['evidence'] = [
        {**item, 'stepIds': [ident for ident in item['stepIds'] if ident in step_ids]}
        for item in manual['evidence'] if any(ident in step_ids for ident in item['stepIds'])
    ]
    evidence_ids = {item['id'] for item in result['evidence']}
    for step in result['steps']:
        step['evidenceIds'] = [ident for ident in step['evidenceIds'] if ident in evidence_ids]
    feature_ids = {item['featureId'] for item in result['workflows']}
    result['features'] = [{**item, 'roles': [role]} for item in manual['features'] if item['id'] in feature_ids]
    module_ids = {item['moduleId'] for item in result['features']}
    result['modules'] = [item for item in manual['modules'] if item['id'] in module_ids]
    result['chapters'] = []
    for chapter in manual['chapters']:
        relevant = [ident for ident in chapter['workflowIds'] if ident in workflow_ids]
        if not relevant:
            continue
        item = deepcopy(chapter)
        item['workflowIds'] = relevant
        item['faqs'] = [deepcopy(faq) for faq in chapter.get('faqs', [])
                        if not faq.get('workflowIds') or set(faq['workflowIds']) <= workflow_ids]
        result['chapters'].append(item)
    result['title'] = f"{manual['title']} · {role}"
    return result
