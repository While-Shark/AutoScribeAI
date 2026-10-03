"""Mechanical checks of a rendered manual; human visual review stays explicit."""
import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from PIL import Image, UnidentifiedImageError

from .html_renderer import verify_coverage
from .state import atomic_json
from .validation import ValidationError, asset_path, read_json, validate_manual


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links = set(), []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])


def audit_package(manual_path, coverage_path, package_dir, output_path):
    manual_path, coverage_path, package_dir, output_path = map(Path, (manual_path, coverage_path, package_dir, output_path))
    manual = validate_manual(read_json(manual_path), manual_path.parent)
    coverage = verify_coverage(manual, manual_path, coverage_path)
    if output_path.resolve().is_relative_to(package_dir.resolve()):
        raise ValidationError('检查报告必须保存在交付包之外，避免修改已发布包')
    findings = []

    def issue(code, detail):
        findings.append({'code': code, 'detail': detail})

    for evidence in manual['evidence']:
        try:
            with Image.open(asset_path(manual_path.parent, evidence['path'])) as image:
                image.verify()
            with Image.open(asset_path(manual_path.parent, evidence['path'])) as image:
                if image.width < 32 or image.height < 32:
                    issue('small-image', evidence['id'])
        except (OSError, UnidentifiedImageError, ValueError, Image.DecompressionBombError):
            issue('invalid-image', evidence['id'])

    html_file = package_dir / 'index.html'
    if not html_file.is_file():
        issue('missing-html', 'index.html')
    else:
        links = Links()
        try:
            html_text = html_file.read_text(encoding='utf-8')
            links.feed(html_text)
            if '<html' not in html_text.lower() or '</html>' not in html_text.lower():
                issue('invalid-html', 'index.html')
        except (UnicodeError, OSError, ValueError):
            issue('invalid-html', 'index.html')
        for link in links.links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc:
                if parsed.scheme not in ('http', 'https', 'mailto'):
                    issue('unsafe-link', 'unsupported URL scheme')
                continue  # External URLs cannot be tested offline.
            if parsed.path:
                path = unquote(parsed.path)
                try:
                    target = asset_path(package_dir, path)
                    if not target.is_file():
                        issue('broken-link', path)
                except ValidationError:
                    issue('unsafe-link', path)
            if parsed.fragment and unquote(parsed.fragment) not in links.ids:
                issue('broken-anchor', unquote(parsed.fragment))

    for name, required in (('manual.docx', ('[Content_Types].xml', 'word/document.xml')),
                           ('manual-markdown.zip', ('README.md',))):
        path = package_dir / name
        if not path.is_file():
            issue('missing-export', name)
            continue
        try:
            with zipfile.ZipFile(path) as archive:
                names = set(archive.namelist())
                if archive.testzip() is not None or not set(required) <= names:
                    issue('invalid-export', name)
                    continue
                if name.endswith('.docx') and manual['evidence']:
                    if not any(item.startswith('word/media/') for item in names):
                        issue('missing-docx-images', name)
                if name.endswith('.zip'):
                    markdown = archive.read('README.md').decode('utf-8')
                    for path_ref in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', markdown):
                        if path_ref not in names:
                            issue('broken-markdown-image', path_ref)
        except (OSError, zipfile.BadZipFile, UnicodeDecodeError):
            issue('invalid-export', name)

    for evidence in manual['evidence']:
        name = f"evidence/{evidence['id']}{Path(evidence['path']).suffix.lower()}"
        if not (package_dir / name).is_file():
            issue('missing-copied-evidence', evidence['id'])
    for name in ('manual.json', 'coverage.json', 'quality-report.json'):
        if not (package_dir / name).is_file():
            issue('missing-package-file', name)

    result = {
        'projectId': manual['project']['id'], 'version': manual['project'].get('version', ''),
        'planned': coverage['planned'], 'verified': coverage['verified'],
        'mechanicalChecksPassed': not findings, 'findings': findings,
        'humanReviewRequired': ['截图内容与步骤是否对应', '打码是否完整且无敏感文本', 'DOCX 逐页版式和手机端 HTML 阅读效果'],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_json(output_path, result)
    return result
