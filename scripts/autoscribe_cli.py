#!/usr/bin/env python3
"""Repository entry point. Run from any cwd using the absolute script path."""
import argparse
import json
import sys
from pathlib import Path

from autoscribe.state import STAGES, initialize, load, resume, transition
from autoscribe.inventory import create_coverage_plan, coverage_report, inventory_to_manual, plan_summary
from autoscribe.evidence_images import prepare_screenshot
from autoscribe.actions import begin_action, load_actions, resolve_action, test_data_report
from autoscribe.progress import read_progress, update_progress
from autoscribe.diff import compare_manuals
from autoscribe.audit import audit_package
from autoscribe.locale_check import compare_locales
from autoscribe.html_renderer import render_html
from autoscribe.standalone_html import export_standalone_html
from autoscribe.docx_renderer import render_docx
from autoscribe.markdown_renderer import render_markdown_zip
from autoscribe.validation import ValidationError, read_json, validate, validate_manual


def main():
    parser = argparse.ArgumentParser(description='AutoScribeAI 无服务运行基础工具')
    commands = parser.add_subparsers(dest='command', required=True)
    check = commands.add_parser('validate')
    check.add_argument('kind', choices=('project', 'manual', 'host', 'manifest', 'checkpoint', 'inventory', 'coverage-plan', 'coverage', 'actions', 'quality-report', 'workflow-progress'))
    check.add_argument('file', type=Path)
    check.add_argument('--root', type=Path, help='手册资源根目录，默认为 JSON 所在目录')
    init = commands.add_parser('init')
    init.add_argument('config', type=Path)
    init.add_argument('--run-dir', required=True, type=Path)
    init.add_argument('--host', type=Path)
    again = commands.add_parser('resume')
    again.add_argument('run_dir', type=Path)
    again.add_argument('--config', type=Path)
    again.add_argument('--host', type=Path)
    status = commands.add_parser('status')
    status.add_argument('run_dir', type=Path)
    move = commands.add_parser('stage')
    move.add_argument('run_dir', type=Path)
    move.add_argument('stage', choices=STAGES)
    move.add_argument('status', choices=('running', 'completed', 'blocked', 'failed', 'skipped'))
    move.add_argument('--reason')
    analyze = commands.add_parser('analyze')
    analyze.add_argument('--config', required=True, type=Path)
    analyze.add_argument('--inventory', required=True, type=Path)
    analyze.add_argument('--manual-out', required=True, type=Path)
    analyze.add_argument('--plan-out', required=True, type=Path)
    coverage = commands.add_parser('coverage')
    coverage.add_argument('--plan', required=True, type=Path)
    coverage.add_argument('--inventory', required=True, type=Path)
    coverage.add_argument('--config', required=True, type=Path)
    coverage.add_argument('--manual', required=True, type=Path)
    coverage.add_argument('--out', required=True, type=Path)
    preview = commands.add_parser('plan-summary')
    preview.add_argument('plan', type=Path)
    image = commands.add_parser('prepare-image')
    image.add_argument('source', type=Path)
    image.add_argument('output', type=Path)
    image.add_argument('--crop', metavar='X,Y,W,H', help='归一化裁剪区域')
    image.add_argument('--root', type=Path, help='证据路径的相对根目录，必须包含输出文件')
    image.add_argument('--redact', action='append', default=[], metavar='X,Y,W,H', help='归一化打码框，可重复')
    image.add_argument('--callout', action='append', default=[], metavar='X,Y', help='归一化目标标记，可重复，按参数顺序编号')
    render = commands.add_parser('render-html')
    render.add_argument('--manual', required=True, type=Path)
    render.add_argument('--coverage', required=True, type=Path)
    render.add_argument('--out-dir', required=True, type=Path)
    single = commands.add_parser('export-html')
    single.add_argument('--manual', required=True, type=Path)
    single.add_argument('--coverage', required=True, type=Path)
    single.add_argument('--out', required=True, type=Path)
    docx = commands.add_parser('export-docx')
    docx.add_argument('--manual', required=True, type=Path)
    docx.add_argument('--out', required=True, type=Path)
    docx.add_argument('--role', help='只导出指定角色的流程')
    markdown = commands.add_parser('export-markdown')
    markdown.add_argument('--manual', required=True, type=Path)
    markdown.add_argument('--out-zip', required=True, type=Path)
    markdown.add_argument('--role', help='只导出指定角色的流程')
    action = commands.add_parser('action-begin')
    action.add_argument('run_dir', type=Path)
    action.add_argument('--workflow', required=True)
    action.add_argument('--step', required=True)
    action.add_argument('--operation', required=True)
    action.add_argument('--target', required=True, help='非敏感目标引用；不写账号或业务载荷')
    action_status = commands.add_parser('action-status')
    action_status.add_argument('run_dir', type=Path)
    cleanup = commands.add_parser('test-data-report')
    cleanup.add_argument('run_dir', type=Path)
    resolve = commands.add_parser('action-resolve')
    resolve.add_argument('run_dir', type=Path)
    resolve.add_argument('action_id')
    resolve.add_argument('--result', required=True, choices=('completed', 'not-applied', 'uncertain'))
    resolve.add_argument('--reason')
    progress = commands.add_parser('workflow-progress')
    progress.add_argument('run_dir', type=Path)
    progress.add_argument('--workflow')
    progress.add_argument('--status', choices=('running', 'blocked', 'completed'))
    progress.add_argument('--note')
    compare = commands.add_parser('diff-manuals')
    compare.add_argument('old', type=Path)
    compare.add_argument('new', type=Path)
    audit = commands.add_parser('audit')
    audit.add_argument('--manual', required=True, type=Path)
    audit.add_argument('--coverage', required=True, type=Path)
    audit.add_argument('--package', required=True, type=Path)
    audit.add_argument('--out', required=True, type=Path)
    locales = commands.add_parser('check-locales')
    locales.add_argument('source', type=Path)
    locales.add_argument('translation', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'validate':
            data = read_json(args.file)
            if args.kind == 'manual':
                validate_manual(data, args.root or args.file.parent)
            else:
                validate(data, args.kind)
            result = {'valid': True, 'kind': args.kind}
        elif args.command == 'init':
            result = initialize(args.config, args.run_dir, read_json(args.host) if args.host else None)
        elif args.command == 'render-html':
            result = render_html(args.manual, args.coverage, args.out_dir)
        elif args.command == 'export-html':
            result = export_standalone_html(args.manual, args.coverage, args.out)
        elif args.command == 'export-docx':
            result = render_docx(args.manual, args.out, args.role)
        elif args.command == 'export-markdown':
            result = render_markdown_zip(args.manual, args.out_zip, args.role)
        elif args.command == 'action-begin':
            result = begin_action(args.run_dir, args.workflow, args.step, args.operation, args.target)
        elif args.command == 'action-status':
            result = load_actions(args.run_dir)
        elif args.command == 'test-data-report':
            result = test_data_report(args.run_dir)
        elif args.command == 'action-resolve':
            result = resolve_action(args.run_dir, args.action_id, args.result, args.reason)
        elif args.command == 'workflow-progress':
            if bool(args.workflow) != bool(args.status) or (args.workflow and not args.note):
                raise ValidationError('更新流程进度须同时提供 --workflow、--status 和 --note')
            result = update_progress(args.run_dir, args.workflow, args.status, args.note) if args.workflow else read_progress(args.run_dir)
        elif args.command == 'diff-manuals':
            result = compare_manuals(args.old, args.new)
        elif args.command == 'audit':
            result = audit_package(args.manual, args.coverage, args.package, args.out)
        elif args.command == 'check-locales':
            result = compare_locales(args.source, args.translation)
        elif args.command == 'prepare-image':
            def coordinates(value, count):
                try:
                    parts = [float(part.strip()) for part in value.split(',')]
                except ValueError:
                    raise ValidationError('坐标须为逗号分隔的数字') from None
                if len(parts) != count:
                    raise ValidationError(f'该坐标需要 {count} 个数字')
                return parts
            result = prepare_screenshot(args.source, args.output,
                [coordinates(value, 4) for value in args.redact],
                [coordinates(value, 2) for value in args.callout], args.root,
                coordinates(args.crop, 4) if args.crop else None)
        elif args.command == 'analyze':
            config = validate(read_json(args.config), 'project')
            inventory = read_json(args.inventory)
            validate(inventory, 'inventory')
            manual = inventory_to_manual(inventory, config)
            validate_manual(manual, args.manual_out.parent)
            args.manual_out.parent.mkdir(parents=True, exist_ok=True)
            args.plan_out.parent.mkdir(parents=True, exist_ok=True)
            from autoscribe.state import atomic_json
            atomic_json(args.manual_out, manual)
            plan = create_coverage_plan(args.inventory, args.config, args.plan_out)
            result = {'manual': str(args.manual_out), 'coveragePlan': str(args.plan_out), 'plannedWorkflows': len(plan['workflows']), 'verified': 0}
        elif args.command == 'coverage':
            result = coverage_report(args.plan, args.inventory, args.config, args.manual, args.out)
        elif args.command == 'plan-summary':
            result = plan_summary(args.plan)
        elif args.command == 'resume':
            result = resume(args.run_dir, args.config, read_json(args.host) if args.host else None)
        elif args.command == 'stage':
            result = transition(args.run_dir, args.stage, args.status, args.reason)
        else:
            result = load(args.run_dir)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValidationError, OSError) as error:
        # OSError filenames may contain sensitive input. Do not echo them.
        message = str(error) if isinstance(error, ValidationError) else f'文件操作失败（{type(error).__name__}）；检查路径、权限或任务目录是否已存在'
        print(json.dumps({'error': message}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
