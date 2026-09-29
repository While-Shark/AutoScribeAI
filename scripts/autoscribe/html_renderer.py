"""Render a validated manual and its local evidence as an offline HTML folder."""
import html
import os
import shutil
import tempfile
from collections import Counter
from pathlib import Path

from .inventory import file_hash
from .state import atomic_json
from .validation import ValidationError, asset_path, read_json, validate, validate_manual

CSS = r'''
:root{color-scheme:light;--ink:#202b3c;--muted:#627089;--line:#e4eaf1;--paper:#fff;--wash:#f5f7fb;--accent:#2457d6;--good:#16734a;--warn:#98620b;--bad:#a33c39;font:16px/1.65 Inter,-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans SC",sans-serif}*{box-sizing:border-box}body{margin:0;background:var(--wash);color:var(--ink)}a{color:var(--accent)}.shell{min-height:100vh;display:grid;grid-template-columns:290px minmax(0,1fr)}aside{height:100vh;position:sticky;top:0;overflow:auto;background:#111d31;color:#eaf0fb;padding:26px 20px}aside h2{font-size:15px;letter-spacing:.04em;margin:0 0 18px}.brand{font-size:12px;color:#a9bddf;letter-spacing:.12em;text-transform:uppercase}.search{width:100%;margin:16px 0;padding:11px 12px;border-radius:9px;border:1px solid #46546a;background:#1d2b43;color:white;font:inherit}.search::placeholder{color:#adbad0}nav a{display:block;color:#cbd6e8;text-decoration:none;padding:7px 9px;border-radius:7px;font-size:14px}nav a:hover{background:#263650;color:#fff}.side-note{margin-top:25px;color:#a9b7ce;font-size:12px}main{width:min(100%,1120px);padding:42px clamp(20px,5vw,72px) 72px}.hero,.panel,.module,.workflow{background:var(--paper);border:1px solid var(--line);border-radius:16px;box-shadow:0 8px 25px #20314b08}.hero{padding:36px;margin-bottom:20px;background:linear-gradient(135deg,#fff,#f4f7ff)}.eyebrow{font-size:12px;text-transform:uppercase;letter-spacing:.1em;color:var(--accent);font-weight:700}.hero h1{line-height:1.2;font-size:clamp(30px,4vw,45px);margin:8px 0 12px}.meta,.muted{color:var(--muted);font-size:14px}.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:18px 0}.stat{padding:16px;background:#fff;border:1px solid var(--line);border-radius:12px}.stat b{font-size:23px;display:block}.panel{padding:22px 26px;margin:18px 0}.panel h2,.module h2{margin-top:0}.notice{border-left:4px solid #d49b2f;background:#fff9e9;padding:13px 16px;border-radius:4px;margin:12px 0}.notice.danger{border-color:#c25050;background:#fff3f2}.module{padding:26px;margin:28px 0}.module>header{border-bottom:1px solid var(--line);padding-bottom:14px;margin-bottom:20px}.feature{margin:24px 0}.feature h3{font-size:18px}.workflow{padding:21px;margin:15px 0;box-shadow:none}.workflow h4{margin:0;font-size:18px}.badge{display:inline-flex;padding:3px 9px;border-radius:99px;font-size:12px;font-weight:700;background:#eef2f7;color:#49576c}.badge.verified{background:#e6f5ed;color:var(--good)}.badge.blocked{background:#fff2dc;color:var(--warn)}.badge.unverified,.badge.pending{background:#edf1f7;color:#56657c}.goal{font-size:14px;color:var(--muted);margin:6px 0 12px}ol.steps{list-style:none;padding:0;counter-reset:step}ol.steps>li{counter-increment:step;position:relative;border-top:1px solid var(--line);padding:16px 0 16px 42px}ol.steps>li:before{content:counter(step);position:absolute;left:0;top:16px;background:#eaf0ff;color:var(--accent);font-weight:700;border-radius:50%;width:28px;height:28px;text-align:center;line-height:28px}.step-title{font-weight:700}.result{padding:10px 12px;background:#f6f8fb;border-radius:8px;margin:9px 0}.evidence{margin:14px 0 4px}.evidence button{border:0;background:transparent;padding:0;cursor:zoom-in;text-align:left;max-width:100%}.evidence img{display:block;max-width:min(100%,780px);max-height:560px;object-fit:contain;border:1px solid var(--line);border-radius:10px}.evidence figcaption{color:var(--muted);font-size:13px;margin-top:6px}.empty{padding:18px;color:var(--muted);border:1px dashed #cad3e0;border-radius:10px}.table-wrap{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;padding:10px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--muted)}footer{padding:28px 4px;color:var(--muted);font-size:13px}.zoom{border:0;border-radius:14px;padding:0;max-width:min(96vw,1400px);max-height:92vh;background:#111d31}.zoom::backdrop{background:#101828d9}.zoom img{display:block;max-width:94vw;max-height:84vh;object-fit:contain}.zoom p{color:white;margin:4px 12px 10px;font-size:13px}button:focus-visible,a:focus-visible,input:focus-visible{outline:3px solid #82a9ff;outline-offset:2px}.hidden{display:none!important}@media(max-width:850px){.shell{display:block}aside{height:auto;position:relative;padding:16px 18px}aside h2{margin-bottom:0}nav{display:flex;gap:5px;overflow:auto}nav a{white-space:nowrap}.side-note{display:none}main{padding:22px 15px 45px}.hero{padding:25px}.stats{grid-template-columns:repeat(2,minmax(0,1fr))}.module{padding:19px}.panel{padding:18px}}@media print{body{background:white}.shell{display:block}aside,.search,.zoom{display:none!important}main{width:100%;padding:0}.hero,.panel,.module,.workflow{box-shadow:none;break-inside:avoid}.module{break-before:page}.evidence img{max-height:460px}}
'''
SCRIPT = r'''
const search=document.querySelector('#manual-search');
search.addEventListener('input',()=>{const q=search.value.trim().toLocaleLowerCase();document.querySelectorAll('[data-search]').forEach(el=>el.classList.toggle('hidden',q&&!el.dataset.search.toLocaleLowerCase().includes(q)));});
document.querySelectorAll('[data-zoom]').forEach(button=>button.addEventListener('click',()=>{const dialog=document.querySelector('#image-dialog');const image=button.querySelector('img');dialog.querySelector('img').src=image.src;dialog.querySelector('img').alt=image.alt;dialog.querySelector('p').textContent=button.dataset.caption;dialog.showModal();}));
document.querySelector('#image-dialog').addEventListener('click',event=>{if(event.target===event.currentTarget)event.currentTarget.close();});
'''


def esc(value):
    return html.escape(str(value), quote=True)


def verify_coverage(manual, manual_path, coverage_path):
    coverage = validate(read_json(coverage_path), 'coverage')
    if coverage['manualSha256'] != file_hash(manual_path):
        raise ValidationError('覆盖报告与当前手册不匹配；请重新生成覆盖报告')
    if coverage['projectId'] != manual['project']['id'] or coverage['projectVersion'] != manual['project'].get('version', ''):
        raise ValidationError('覆盖报告与手册的项目版本不一致')
    statuses = Counter(workflow['status'] for workflow in manual['workflows'])
    if coverage['planned'] != len(manual['workflows']):
        raise ValidationError('覆盖报告的计划流程数与手册不一致')
    for status in ('verified', 'blocked', 'unverified', 'pending'):
        if coverage[status] != statuses[status]:
            raise ValidationError('覆盖报告流程状态与手册不一致')
    manual_module_ids = {module['id'] for module in manual['modules']}
    if {module['id'] for module in coverage['modules']} != manual_module_ids:
        raise ValidationError('覆盖报告模块与手册不一致')
    return coverage


def render_html(manual_path, coverage_path, out_dir):
    manual_path, coverage_path, out_dir = map(Path, (manual_path, coverage_path, out_dir))
    manual = validate_manual(read_json(manual_path), manual_path.parent)
    coverage = verify_coverage(manual, manual_path, coverage_path)
    if out_dir.exists() or out_dir.is_symlink():
        raise ValidationError('HTML 输出目录已存在；请使用新的空目录，避免覆盖用户文件')
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix='.autoscribe-html-', dir=out_dir.parent))
    images = {item['id']: item for item in manual['evidence']}
    chapters = {chapter['moduleId']: chapter for chapter in manual['chapters']}
    features_by_module = {module['id']: [] for module in manual['modules']}
    for feature in manual['features']:
        features_by_module[feature['moduleId']].append(feature)
    workflows_by_feature = {feature['id']: [] for feature in manual['features']}
    for workflow in manual['workflows']:
        workflows_by_feature[workflow['featureId']].append(workflow)
    workflows = {workflow['id']: workflow for workflow in manual['workflows']}
    steps_by_workflow = {workflow['id']: [] for workflow in manual['workflows']}
    for step in manual['steps']:
        steps_by_workflow[step['workflowId']].append(step)
    status_labels = {'verified':'已验证', 'blocked':'受阻', 'unverified':'未验证', 'pending':'待处理'}
    status_counts = {key: coverage[key] for key in status_labels}
    warnings = [
        f"{count} 条流程{status_labels[key]}" for key, count in status_counts.items() if count
    ]
    warnings.extend(manual['limitations'])
    verified_all = coverage['planned'] > 0 and coverage['verified'] == coverage['planned'] and not coverage['blocked'] and not coverage['unverified'] and not coverage['pending'] and not manual['limitations']
    readiness = '范围内流程已验证' if verified_all else '草稿：仍有待核验项'
    try:
        (temporary / 'evidence').mkdir()
        (temporary / 'index.html').write_text('', encoding='utf-8')
        shutil.copyfile(manual_path, temporary / 'manual.json')
        shutil.copyfile(coverage_path, temporary / 'coverage.json')
        for evidence in manual['evidence']:
            source = asset_path(manual_path.parent, evidence['path'])
            suffix = source.suffix.lower()
            target = temporary / 'evidence' / f"{evidence['id']}{suffix}"
            shutil.copyfile(source, target)
        from .docx_renderer import render_docx
        from .markdown_renderer import render_markdown_zip
        render_docx(manual_path, temporary / 'manual.docx')
        render_markdown_zip(manual_path, temporary / 'manual-markdown.zip')
        contents = []
        nav = []
        for module in manual['modules']:
            module_anchor = 'module-' + module['id']
            nav.append(f'<a class="nav-link" href="#{esc(module_anchor)}">{esc(module["name"])}</a>')
            features = features_by_module[module['id']]
            feature_html = []
            for feature in features:
                flows_html = []
                for workflow in workflows_by_feature[feature['id']]:
                    wid = workflow['id']
                    badge = status_labels[workflow['status']]
                    preconditions = ''.join(f'<li>{esc(item)}</li>' for item in workflow['preconditions'])
                    details = f'<details><summary>适用角色与前置条件</summary><p>角色：{esc(workflow["role"])}</p><ul>{preconditions}</ul></details>'
                    if workflow['status'] in ('blocked', 'unverified'):
                        details += f'<div class="notice">{esc(workflow.get("reason", "尚未验证"))}</div>'
                    steps = []
                    for step in sorted(steps_by_workflow[wid], key=lambda item: item['order']):
                        media = []
                        for ident in step['evidenceIds']:
                            item = images[ident]
                            suffix = Path(item['path']).suffix.lower()
                            rel = f"evidence/{ident}{suffix}"
                            caption = f"步骤 {step['order']} · {item['page']} · {ident}"
                            media.append(f'<figure class="evidence"><button type="button" data-zoom data-caption="{esc(caption)}"><img src="{esc(rel)}" alt="{esc(caption)}" loading="lazy"></button><figcaption>{esc(caption)}</figcaption></figure>')
                        steps.append(f'<li><div class="step-title">{esc(step["action"])}</div><div class="muted">操作位置：{esc(step["location"])}</div><div class="result"><b>预期：</b>{esc(step["expectedResult"])}' + (f'<br><b>实际：</b>{esc(step["actualResult"])}' if step.get('actualResult') else '') + '</div>' + ''.join(media) + '</li>')
                    step_markup = '<ol class="steps">' + ''.join(steps) + '</ol>' if steps else '<div class="empty">尚无实际操作步骤。源码或说明中的候选流程不能替代真实界面验证。</div>'
                    searchable = ' '.join([workflow['goal'], workflow['role'], workflow['successCriteria'], *workflow['preconditions']])
                    location = f'<div class="muted">流程位置：{esc(workflow["location"])}</div>' if workflow.get('location') else ''
                    flows_html.append(f'<article class="workflow" id="workflow-{esc(wid)}" data-search="{esc(searchable)}"><h4>{esc(workflow["goal"])} <span class="badge {esc(workflow["status"])}">{esc(badge)}</span></h4><p class="goal">成功标准：{esc(workflow["successCriteria"])}</p>{location}{details}{step_markup}</article>')
                feature_html.append(f'<section class="feature" data-search="{esc(feature["name"])}"><h3>{esc(feature["name"])}</h3><p class="muted">入口：{esc(feature["location"])} · 来源：{esc(feature["source"])}</p>' + (''.join(flows_html) or '<p class="empty">此功能暂无候选操作流程。</p>') + '</section>')
            module_workflows = [workflow for feature in features for workflow in workflows_by_feature[feature['id']]]
            module_verified = sum(w['status'] == 'verified' for w in module_workflows)
            chapter = chapters.get(module['id'], {})
            chapter_title = chapter.get('title', module['name'])
            chapter_purpose = f'<p>{esc(chapter["purpose"])}</p>' if chapter else ''
            faq_items = []
            for faq in chapter.get('faqs', []):
                searchable = f"{faq['question']} {faq['answer']}"
                source_labels = {'observed': '实际观察', 'source': '源码说明', 'human': '人工补充'}
                refs = [workflows[ident]['goal'] for ident in faq.get('workflowIds', [])]
                source_note = f'<p class="muted">依据：{esc(source_labels[faq["source"]])}'
                if refs:
                    source_note += f' · 相关流程：{esc("、".join(refs))}'
                source_note += '</p>'
                faq_items.append(f'<details class="faq" data-search="{esc(searchable)}"><summary>{esc(faq["question"])}</summary><p>{esc(faq["answer"])}</p>{source_note}</details>')
            faq_html = f'<section class="faqs"><h3>常见问题</h3>{"".join(faq_items)}</section>' if faq_items else ''
            contents.append(f'<section class="module" id="{esc(module_anchor)}" data-search="{esc(module["name"])}"><header><div class="eyebrow">模块 · {module_verified}/{len(module_workflows)} 已验证</div><h2>{esc(chapter_title)}</h2>{chapter_purpose}<p class="muted">入口：{esc(module["location"])} · 来源：{esc(module["source"])}</p></header>' + (''.join(feature_html) or '<p class="empty">此模块暂无已发现功能。</p>') + faq_html + '</section>')
        notices = ''.join(f'<div class="notice">{esc(item)}</div>' for item in warnings)
        scope_rows = ''.join(f'<tr><td>{esc(item["scope"])}</td><td>{item["planned"]}</td><td>{item["verified"]}</td><td>{item["blocked"]}</td><td>{item["unverified"] + item["pending"]}</td><td>{esc(item["coverageDisplay"])}</td></tr>' for item in coverage['scopeItems'])
        module_rows = ''.join(f'<tr><td>{esc(item["name"])}</td><td>{item["planned"]}</td><td>{item["verified"]}</td><td>{item["blocked"]}</td><td>{item["unverified"] + item["pending"]}</td><td>{esc(item["coverageDisplay"])}</td></tr>' for item in coverage['modules'])
        scope_table = f'<div class="table-wrap"><table><thead><tr><th>范围</th><th>计划</th><th>已验证</th><th>受阻</th><th>待核验</th><th>覆盖率</th></tr></thead><tbody>{scope_rows}</tbody></table></div>'
        module_table = f'<div class="table-wrap"><table><thead><tr><th>模块</th><th>计划</th><th>已验证</th><th>受阻</th><th>待核验</th><th>覆盖率</th></tr></thead><tbody>{module_rows}</tbody></table></div>'
        title = manual['title']
        downloads = '<section class="panel downloads"><h2>下载其他格式</h2><p><a href="manual.docx" download>Word 文档（DOCX）</a> · <a href="manual-markdown.zip" download>Markdown 文件包（ZIP）</a></p></section>'
        html_doc = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{esc(title)}"><title>{esc(title)}</title><style>{CSS}</style></head><body><div class="shell"><aside><div class="brand">AutoScribeAI · 操作手册</div><h2>目录</h2><label class="muted" for="manual-search">搜索模块与流程</label><input class="search" id="manual-search" type="search" placeholder="输入关键词…" autocomplete="off"><nav>{''.join(nav)}<a href="#coverage">覆盖与限制</a></nav><p class="side-note">离线手册 · 版本 {esc(manual['project'].get('version', '未注明'))}<br>完整资源见本目录下的 evidence/ 文件夹。</p></aside><main><header class="hero"><div class="eyebrow">{esc(manual['project']['name'])} · {esc(manual['project'].get('environment', ''))}</div><h1>{esc(title)}</h1><div class="meta">适用角色：{esc('、'.join(manual['roles']))} · 项目版本：{esc(manual['project'].get('version', '未注明'))}</div><p><span class="badge {'verified' if verified_all else 'unverified'}">{readiness}</span></p></header>{downloads}<section class="stats"><div class="stat"><b>{coverage['planned']}</b><span class="muted">计划流程</span></div><div class="stat"><b>{coverage['verified']}</b><span class="muted">已验证</span></div><div class="stat"><b>{coverage['blocked']}</b><span class="muted">受阻</span></div><div class="stat"><b>{esc(coverage['coverageDisplay'])}</b><span class="muted">覆盖率</span></div></section><section id="coverage" class="panel"><h2>覆盖范围与使用限制</h2><p>覆盖率只统计附有真实操作步骤、实际结果和截图证据的已验证流程。源码推断保留为候选项。</p>{notices or '<p>未报告已知阻塞。</p>'}<h3>按原始范围</h3>{scope_table}<h3>按模块</h3>{module_table}<p><a href="coverage.json">查看机器可读覆盖报告</a> · <a href="manual.json">查看统一内容模型</a></p></section>{''.join(contents)}<footer>由 AutoScribeAI 生成 · 此页面及证据图片可在本地离线阅读。</footer></main></div><dialog class="zoom" id="image-dialog"><img alt=""><p></p></dialog><script>{SCRIPT}</script></body></html>'''
        (temporary / 'index.html').write_text(html_doc, encoding='utf-8')
        quality = {
            'schemaVersion': '0.1', 'projectId': manual['project']['id'],
            'projectVersion': manual['project'].get('version', ''),
            'manualSha256': file_hash(manual_path), 'coverageSha256': file_hash(coverage_path),
            'workflowCount': len(manual['workflows']), 'verified': coverage['verified'],
            'blocked': coverage['blocked'], 'unverified': coverage['unverified'],
            'pending': coverage['pending'], 'evidenceCount': len(manual['evidence']),
            'copiedEvidenceCount': len(images), 'ready': verified_all,
            'issues': warnings,
        }
        validate(quality, 'quality-report')
        atomic_json(temporary / 'quality-report.json', quality)
        os.replace(temporary, out_dir)
        return quality
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
