"""Check translated manuals preserve the source manual's verified structure."""
from pathlib import Path

from .validation import ValidationError, read_json, validate_manual


def compare_locales(source_path, translation_path):
    source_path, translation_path = Path(source_path), Path(translation_path)
    source = validate_manual(read_json(source_path), source_path.parent)
    translated = validate_manual(read_json(translation_path), translation_path.parent)
    if source['project']['id'] != translated['project']['id']:
        raise ValidationError('多语言手册必须属于同一项目')
    differences = []
    if source['project'].get('version') != translated['project'].get('version'):
        differences.append('project-version')
    if source['project'].get('language', 'en-US') == translated['project'].get('language', 'en-US'):
        differences.append('same-language')
    if set(source['roles']) != set(translated['roles']):
        differences.append('roles')
    for group in ('modules', 'features', 'workflows', 'steps', 'chapters'):
        originals = {item['id']: item for item in source[group]}
        translations = {item['id']: item for item in translated[group]}
        if originals.keys() != translations.keys():
            differences.append(f'{group}-ids')
        for ident in originals.keys() & translations.keys():
            first, second = originals[ident], translations[ident]
            fields = {
                'features': ('moduleId', 'roles'), 'workflows': ('featureId', 'role', 'status', 'stepIds'),
                'steps': ('workflowId', 'order', 'source'), 'chapters': ('moduleId', 'workflowIds'),
            }.get(group, ())
            if any(first.get(key) != second.get(key) for key in fields):
                differences.append(f'{group}/{ident}')
    # A translated screenshot may be different; require the evidence relationships
    # to remain explicit instead of reusing an unrelated source language image.
    source_steps = {item['id']: item for item in source['steps']}
    target_steps = {item['id']: item for item in translated['steps']}
    for ident in source_steps.keys() & target_steps.keys():
        if bool(source_steps[ident]['evidenceIds']) != bool(target_steps[ident]['evidenceIds']):
            differences.append(f'evidence/{ident}')
    return {
        'projectId': source['project']['id'],
        'sourceLanguage': source['project'].get('language', 'en-US'),
        'translationLanguage': translated['project'].get('language', 'en-US'),
        'aligned': not differences, 'differences': sorted(set(differences)),
        'humanReviewRequired': '核对译文术语、界面语言与每张截图；结构一致不代表翻译准确。',
    }
