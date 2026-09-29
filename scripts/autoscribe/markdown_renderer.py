"""Export a validated manual as a relocatable Markdown ZIP package."""
import tempfile
import zipfile
from pathlib import Path

from .i18n import locale_for, t
from .validation import ValidationError, asset_path, read_json, validate_manual


def render_markdown(manual, asset_prefix="assets"):
    """Return Markdown whose image links resolve beneath ``asset_prefix``."""
    language = manual.get('project', {}).get('language') or manual.get('language')
    colon = ':' if locale_for(language) == 'en-US' else '：'
    text_space = ' ' if locale_for(language) == 'en-US' else ''
    note_separator = '; ' if locale_for(language) == 'en-US' else '；'
    modules = {item['id']: item for item in manual['modules']}
    features = {item['id']: item for item in manual['features']}
    chapters = {item['moduleId']: item for item in manual['chapters']}
    workflows_by_feature = {ident: [] for ident in features}
    for workflow in manual['workflows']:
        workflows_by_feature[workflow['featureId']].append(workflow)
    steps_by_workflow = {item['id']: [] for item in manual['workflows']}
    for step in manual['steps']:
        steps_by_workflow[step['workflowId']].append(step)
    evidence = {item['id']: item for item in manual['evidence']}

    lines = [f"# {manual['title']}", "", f"**{t(language, 'project')}{colon}** {manual['project']['name']}",
             f"**{t(language, 'project_version')}{colon}** {manual['project'].get('version', 'N/A')}",
             f"**{t(language, 'environment')}{colon}** {manual['project'].get('environment', 'N/A')}",
             f"**{t(language, 'roles')}{colon}** {', '.join(manual['roles'])}", ""]
    status_labels = {key: t(language, key) for key in ('verified', 'blocked', 'unverified', 'pending')}
    for module in manual['modules']:
        chapter = chapters.get(module['id'], {})
        lines.extend([f"## {chapter.get('title', module['name'])}", ""])
        if chapter.get('purpose'):
            lines.extend([chapter['purpose'], ""])
        source_labels = {'observed': t(language, 'source_observed'), 'source': t(language, 'source_code'), 'human': t(language, 'source_human')}
        lines.extend([f"**{t(language, 'module_entry')}{colon}** {module['location']}  ", f"**{t(language, 'source')}{colon}** {source_labels[module['source']]}", ""])
        if chapter.get('faqs'):
            lines.extend([f"### {t(language, 'faqs')}", ""])
            workflow_labels = {item['id']: item['goal'] for item in manual['workflows']}
            for faq in chapter['faqs']:
                lines.extend([f"**{t(language, 'faq_question')}{colon}{text_space}{faq['question']}**", "", f"{t(language, 'faq_answer')}{colon}{text_space}{faq['answer']}"])
                references = [workflow_labels[ident] for ident in faq.get('workflowIds', [])]
                note = f"{t(language, 'basis')}{colon}{text_space}{source_labels[faq['source']]}"
                if references:
                    note += f"{note_separator}{t(language, 'related_workflows')}{colon}{text_space}{', '.join(references)}"
                lines.extend(["", f"_{note}_", ""])
        for feature in (item for item in manual['features'] if item['moduleId'] == module['id']):
            lines.extend([f"### {feature['name']}", "", f"{t(language, 'feature_entry')}{colon} {feature['location']}", ""])
            workflows = workflows_by_feature[feature['id']]
            if not workflows:
                lines.extend([t(language, 'no_feature_workflows'), ""])
            for workflow in workflows:
                lines.extend([f"#### {workflow['goal']}", "",
                              f"**{t(language, 'workflow_status')}{colon}** {status_labels[workflow['status']]}",
                              f"**{t(language, 'role')}{colon}** {workflow['role']}",
                              f"**{t(language, 'success_criteria')}{colon}** {workflow['successCriteria']}"])
                if workflow.get('location'):
                    lines.append(f"**{t(language, 'workflow_location')}{colon}** {workflow['location']}")
                if workflow['preconditions']:
                    lines.extend(["", f"{t(language, 'preconditions')}{colon}", *[f"- {item}" for item in workflow['preconditions']]])
                if workflow['status'] in ('blocked', 'unverified'):
                    lines.extend(["", f"**{t(language, 'explanation')}{colon}** {workflow.get('reason', t(language, 'not_validated'))}"])
                lines.append("")
                steps = sorted(steps_by_workflow[workflow['id']], key=lambda item: item['order'])
                if not steps:
                    lines.extend([t(language, 'no_steps_doc'), ""])
                for step in steps:
                    lines.extend([f"{step['order']}. **{step['action']}**",
                                  f"   - {t(language, 'action_location')}{colon} {step['location']}",
                                  f"   - {t(language, 'expected')}{colon} {step['expectedResult']}"])
                    if step.get('actualResult'):
                        lines.append(f"   - {t(language, 'actual')}{colon} {step['actualResult']}")
                    for ident in step['evidenceIds']:
                        item = evidence[ident]
                        suffix = Path(item['path']).suffix.lower()
                        caption = t(language, 'markdown_step_caption', order=step['order'], page=item['page'])
                        figure = t(language, 'figure', order=step['order'], page=item['page'])
                        lines.extend(["", f"   ![{caption}]({asset_prefix}/{ident}{suffix})",
                                      f"   *{figure} · {ident}*", ""])
                    lines.append("")

    lines.extend([f"## {t(language, 'coverage_limitations')}", ""])
    if manual['limitations']:
        lines.extend([*[f"- {item}" for item in manual['limitations']], ""])
    else:
        lines.extend([t(language, 'no_extra_limitations'), ""])
    lines.extend([t(language, 'verified_meaning'), ""])
    return "\n".join(lines)


def render_markdown_zip(manual_path, out_zip):
    manual_path, out_zip = Path(manual_path), Path(out_zip)
    manual = validate_manual(read_json(manual_path), manual_path.parent)
    if out_zip.exists() or out_zip.is_symlink():
        raise ValidationError('Markdown ZIP 输出文件已存在；请使用新的路径，避免覆盖用户文件')
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix='.autoscribe-md-', dir=out_zip.parent))
    staged_zip = temp_dir / 'manual-markdown.zip'
    try:
        with zipfile.ZipFile(staged_zip, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('README.md', render_markdown(manual))
            for item in manual['evidence']:
                source = asset_path(manual_path.parent, item['path'])
                suffix = source.suffix.lower()
                archive.write(source, f'assets/{item["id"]}{suffix}')
        # Publish only a fully built archive and never replace a prior deliverable.
        staged_zip.replace(out_zip)
    finally:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    return {'path': out_zip.name, 'evidenceCount': len(manual['evidence'])}
