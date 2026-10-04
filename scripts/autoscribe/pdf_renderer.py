"""Convert a validated manual to PDF through the optional LibreOffice CLI."""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .docx_renderer import render_docx
from .validation import ValidationError


def render_pdf(manual_path, output_path, soffice=None, role=None):
    output_path = Path(output_path)
    if output_path.exists() or output_path.is_symlink():
        raise ValidationError('PDF 输出文件已存在；请使用新的路径，避免覆盖用户文件')
    converter = shutil.which(soffice or 'soffice')
    if not converter:
        raise ValidationError('PDF 导出需要 LibreOffice soffice；请安装并加入 PATH，或指定 --soffice')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.autoscribe-pdf-', dir=output_path.parent) as directory:
        directory = Path(directory)
        docx = directory / 'manual.docx'
        render_docx(manual_path, docx, role)
        profile = directory / 'lo-profile'
        command = [converter, f'-env:UserInstallation={profile.as_uri()}', '--headless',
                   '--convert-to', 'pdf:writer_pdf_Export', '--outdir', str(directory), str(docx)]
        environment = os.environ.copy()
        environment['HOME'] = str(directory)
        environment['XDG_CONFIG_HOME'] = str(directory / 'xdg-config')
        environment['XDG_CACHE_HOME'] = str(directory / 'xdg-cache')
        try:
            result = subprocess.run(command, env=environment, capture_output=True, text=True, timeout=120, check=False)
        except subprocess.TimeoutExpired:
            raise ValidationError('LibreOffice PDF 转换超时；请检查转换器或缩小手册') from None
        except OSError:
            raise ValidationError('无法启动 LibreOffice PDF 转换器') from None
        converted = directory / 'manual.pdf'
        if result.returncode or not converted.is_file():
            raise ValidationError('LibreOffice 未生成有效 PDF；请检查字体和转换器安装')
        with converted.open('rb') as stream:
            if stream.read(5) != b'%PDF-':
                raise ValidationError('LibreOffice 未生成有效 PDF；请检查字体和转换器安装')
        size = converted.stat().st_size
        os.replace(converted, output_path)
    return {'path': output_path.name, 'bytes': size}
