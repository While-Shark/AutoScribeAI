"""Export a validated manual as a relocatable Markdown ZIP package."""
import tempfile
import zipfile
from pathlib import Path

from .validation import ValidationError, asset_path, read_json, validate_manual


def render_markdown(manual, asset_prefix="assets"):
    """Return Markdown whose image links resolve beneath ``asset_prefix``."""
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

    lines = [f"# {manual['title']}", "", f"**项目：** {manual['project']['name']}",
             f"**版本：** {manual['project'].get('version', '未注明')}",
             f"**环境：** {manual['project'].get('environment', '未注明')}",
             f"**适用角色：** {', '.join(manual['roles'])}", ""]
    status_labels = {'verified': '已验证', 'blocked': '受阻', 'unverified': '未验证', 'pending': '待处理'}
    for module in manual['modules']:
        chapter = chapters.get(module['id'], {})
        lines.extend([f"## {chapter.get('title', module['name'])}", ""])
        if chapter.get('purpose'):
            lines.extend([chapter['purpose'], ""])
        lines.extend([f"**入口：** {module['location']}  ", f"**来源：** {module['source']}", ""])
        if chapter.get('faqs'):
            lines.extend(["### 常见问题", ""])
            source_labels = {'observed': '实际观察', 'source': '源码说明', 'human': '人工补充'}
            workflow_labels = {item['id']: item['goal'] for item in manual['workflows']}
            for faq in chapter['faqs']:
                lines.extend([f"**问：{faq['question']}**", "", f"答：{faq['answer']}"])
                references = [workflow_labels[ident] for ident in faq.get('workflowIds', [])]
                note = f"依据：{source_labels[faq['source']]}"
                if references:
                    note += f"；相关流程：{'、'.join(references)}"
                lines.extend(["", f"_{note}_", ""])
        for feature in (item for item in manual['features'] if item['moduleId'] == module['id']):
            lines.extend([f"### {feature['name']}", "", f"入口：{feature['location']}", ""])
            workflows = workflows_by_feature[feature['id']]
            if not workflows:
                lines.extend(["此功能暂无候选操作流程。", ""])
            for workflow in workflows:
                lines.extend([f"#### {workflow['goal']}", "",
                              f"**状态：** {status_labels[workflow['status']]}",
                              f"**角色：** {workflow['role']}",
                              f"**成功标准：** {workflow['successCriteria']}"])
                if workflow.get('location'):
                    lines.append(f"**流程位置：** {workflow['location']}")
                if workflow['preconditions']:
                    lines.extend(["", "前置条件：", *[f"- {item}" for item in workflow['preconditions']]])
                if workflow['status'] in ('blocked', 'unverified'):
                    lines.extend(["", f"**说明：** {workflow.get('reason', '尚未验证')}"])
                lines.append("")
                steps = sorted(steps_by_workflow[workflow['id']], key=lambda item: item['order'])
                if not steps:
                    lines.extend(["尚无实际操作步骤。源码或说明中的候选流程不能替代真实界面验证。", ""])
                for step in steps:
                    lines.extend([f"{step['order']}. **{step['action']}**",
                                  f"   - 操作位置：{step['location']}",
                                  f"   - 预期结果：{step['expectedResult']}"])
                    if step.get('actualResult'):
                        lines.append(f"   - 实际结果：{step['actualResult']}")
                    for ident in step['evidenceIds']:
                        item = evidence[ident]
                        suffix = Path(item['path']).suffix.lower()
                        lines.extend(["", f"   ![步骤 {step['order']} · {item['page']}]({asset_prefix}/{ident}{suffix})",
                                      f"   *图：步骤 {step['order']} · {item['page']} · {ident}*", ""])
                    lines.append("")

    lines.extend(["## 覆盖范围与限制", ""])
    if manual['limitations']:
        lines.extend([*[f"- {item}" for item in manual['limitations']], ""])
    else:
        lines.extend(["没有额外限制说明。", ""])
    lines.extend(["本文中的已验证状态仅表示步骤关联了实际观察记录与证据；未验证或受阻内容不会被表述为已完成。", ""])
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
