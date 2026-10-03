"""Probe local capabilities; browser availability must come from host observation."""
import importlib.util
import tempfile
from pathlib import Path

from .validation import validate


def probe(config, base, workspace, host=None):
    if host is not None:
        validate(host, 'host')
    browser = (host or {}).get('browser', {
        'status': 'unknown', 'provider': 'not-probed', 'screenshot': False,
        'reason': '宿主尚未验证浏览器能力，不能宣称已验证界面',
    })
    source = config['source']
    source_ok = 'path' in source and (Path(base) / source['path']).is_dir()
    try:
        with tempfile.TemporaryFile(dir=workspace):
            pass
        writable = True
    except OSError:
        writable = False
    interactive = bool(source.get('url')) and browser['status'] == 'available' and browser['screenshot']
    reasons = []
    if 'path' in source and not source_ok:
        reasons.append('源码目录不可访问')
    if not interactive:
        reasons.append('不能验证界面：缺少目标 URL 或宿主确认的浏览器/截图能力')
    if not writable:
        reasons.append('工作目录不可写')
    return {
        'terminal': True, 'files': writable, 'sourceReadable': source_ok,
        'browser': browser, 'canExplore': interactive,
        'mode': 'interactive' if interactive else ('source-only' if source_ok else 'blocked'),
        'docxDependency': importlib.util.find_spec('docx') is not None,
        'exportersImplemented': True,
        'limitations': reasons,
    }
