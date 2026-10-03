#!/usr/bin/env python3
"""Create a portable AutoScribeAI bundle with Skills and their local runtime."""
import argparse
import os
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = 'AutoScribeAI'
TOP_LEVEL_FILES = ('README.md', 'requirements.txt')
TOP_LEVEL_DIRS = ('docs', 'examples', 'references', 'schemas', 'scripts', 'skills')
ALLOWED_SUFFIXES = {'.md', '.py', '.json', '.yaml'}
EXCLUDED_DIRS = {'.git', '__pycache__', 'runs', 'dist', '.venv', 'venv'}


def package_files(root=ROOT):
    """Return the reviewed source files required to run the bundled Skills."""
    root = Path(root).resolve()
    paths = [root / name for name in TOP_LEVEL_FILES]
    for directory in TOP_LEVEL_DIRS:
        paths.extend(
            path for path in (root / directory).rglob('*')
            if path.is_file()
            and not path.is_symlink()
            and path.suffix.lower() in ALLOWED_SUFFIXES
            and not any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts)
        )
    return sorted({path for path in paths if path.is_file()}, key=lambda path: path.relative_to(root).as_posix())


def build_bundle(output, root=ROOT):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output.exists() or output.is_symlink():
        raise FileExistsError('输出文件已存在；请指定新的 ZIP 路径')
    files = package_files(root)
    required = {'README.md', 'requirements.txt', 'docs/INSTALLATION.md',
                'scripts/autoscribe_cli.py', 'skills/autoscribe/SKILL.md'}
    included = {path.relative_to(root).as_posix() for path in files}
    missing = sorted(required - included)
    if missing:
        raise ValueError('技能包缺少必要文件：' + ', '.join(missing))
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix='.autoscribe-bundle-', suffix='.zip', dir=output.parent)
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in files:
                relative = path.relative_to(root).as_posix()
                info = zipfile.ZipInfo(f'{PACKAGE_ROOT}/{relative}', date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes())
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    return {'path': output.name, 'files': len(files), 'bytes': output.stat().st_size}


def main():
    parser = argparse.ArgumentParser(description='打包 AutoScribeAI Skills 和本地运行依赖')
    parser.add_argument('--output', type=Path, default=ROOT / 'dist/autoscribeai-skills.zip')
    args = parser.parse_args()
    try:
        import json
        print(json.dumps(build_bundle(args.output), ensure_ascii=False, indent=2))
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
