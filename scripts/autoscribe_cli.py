#!/usr/bin/env python3
"""Repository entry point. Run from any cwd using the absolute script path."""
import argparse
import json
import sys
from pathlib import Path

from autoscribe.state import STAGES, initialize, load, resume, transition
from autoscribe.validation import ValidationError, read_json, validate, validate_manual


def main():
    parser = argparse.ArgumentParser(description='AutoScribeAI 无服务运行基础工具')
    commands = parser.add_subparsers(dest='command', required=True)
    check = commands.add_parser('validate')
    check.add_argument('kind', choices=('project', 'manual', 'host', 'manifest', 'checkpoint'))
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
