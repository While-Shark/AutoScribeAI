"""Export a self-contained HTML manual with embedded evidence images."""
import base64
import os
import re
import tempfile
from html.parser import HTMLParser
from pathlib import Path

from .html_renderer import esc, render_html
from .validation import ValidationError, read_json


class _LocalResources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.invalid = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == 'href' and not value.startswith('#'):
                self.invalid.append(value)
            if key == 'src' and not (tag == 'img' and value.startswith(('data:image/png;base64,', 'data:image/jpeg;base64,'))):
                self.invalid.append(value)


def export_standalone_html(manual_path, coverage_path, output_path):
    """Reuse the validated folder renderer, then embed images in one movable file."""
    manual_path, coverage_path, output_path = map(Path, (manual_path, coverage_path, output_path))
    if output_path.exists() or output_path.is_symlink():
        raise ValidationError('单文件 HTML 输出已存在；请使用新路径，避免覆盖用户文件')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.autoscribe-single-', dir=output_path.parent) as directory:
        package = Path(directory) / 'package'
        render_html(manual_path, coverage_path, package)
        manual = read_json(package / 'manual.json')
        page = (package / 'index.html').read_text(encoding='utf-8')

        page, downloads = re.subn(r'<section class="panel downloads">.*?</section>', '', page, count=1, flags=re.S)
        page, data_links = re.subn(r'<p><a href="coverage.json">.*?</a> · <a href="manual.json">.*?</a></p>', '', page, count=1)
        if downloads != 1 or data_links != 1:
            raise ValidationError('无法定位目录包的下载入口，单文件 HTML 未生成')

        for item in manual['evidence']:
            source = Path(item['path'])
            relative = f"evidence/{item['id']}{source.suffix.lower()}"
            raw = (package / relative).read_bytes()
            mime = 'image/png' if raw.startswith(b'\x89PNG\r\n\x1a\n') else 'image/jpeg'
            old = f'src="{esc(relative)}"'
            replacement = f'src="data:{mime};base64,{base64.b64encode(raw).decode("ascii")}"'
            if old not in page:
                raise ValidationError('截图未出现在 HTML 中，单文件 HTML 未生成')
            page = page.replace(old, replacement)

        resources = _LocalResources()
        resources.feed(page)
        if resources.invalid:
            raise ValidationError('单文件 HTML 仍引用外部资源')

        staged = Path(directory) / 'manual.html'
        staged.write_text(page, encoding='utf-8')
        os.replace(staged, output_path)
    return {'path': output_path.name, 'evidenceCount': len(manual['evidence']), 'bytes': output_path.stat().st_size}
