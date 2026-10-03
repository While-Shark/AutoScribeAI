"""Prepare a real screenshot copy with explicit redaction boxes and step markers."""
import hashlib
import os
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from .validation import ValidationError


def normalized_box(spec, width, height):
    if len(spec) != 4 or any(not 0 <= value <= 1 for value in spec):
        raise ValidationError('打码区域须用 0 到 1 之间的 x,y,width,height 比例坐标')
    x, y, w, h = spec
    if w <= 0 or h <= 0:
        raise ValidationError('打码区域的宽度和高度必须大于零')
    left, top = int(x * width), int(y * height)
    right, bottom = int((x + w) * width), int((y + h) * height)
    if right <= left or bottom <= top or right > width or bottom > height:
        raise ValidationError('打码区域必须完全落在截图内，且至少覆盖一个像素')
    return left, top, right, bottom


def normalized_point(spec):
    if len(spec) != 2 or any(not 0 <= value <= 1 for value in spec):
        raise ValidationError('标注坐标须用 0 到 1 之间的 x,y 比例坐标')
    return spec


def prepare_screenshot(source, output, redactions=(), callouts=(), evidence_root=None, crop=None):
    """Write a PNG derivative; keep the source untouched and return evidence metadata."""
    source, output = Path(source), Path(output)
    if source.resolve() == output.resolve():
        raise ValidationError('处理后的截图必须另存为新文件，原始截图保持不变')
    root = Path(evidence_root).resolve() if evidence_root else output.parent.resolve()
    try:
        relative_output = output.resolve().relative_to(root)
    except ValueError:
        raise ValidationError('处理后的截图必须保存在手册证据根目录内') from None
    try:
        with Image.open(source) as incoming:
            if incoming.format not in ('PNG', 'JPEG'):
                raise ValidationError('截图仅支持 PNG/JPEG')
            if incoming.width * incoming.height > 40_000_000:
                raise ValidationError('截图超过 4000 万像素，请先使用宿主安全缩放')
            image = ImageOps.exif_transpose(incoming).convert('RGB')
    except ValidationError:
        raise
    except (OSError, ValueError, Image.DecompressionBombError):
        raise ValidationError('无法解码截图，请检查文件格式') from None

    width, height = image.size
    if width < 32 or height < 32:
        raise ValidationError('截图尺寸至少为 32×32 像素')
    boxes = [normalized_box(box, width, height) for box in redactions]
    points = [normalized_point(point) for point in callouts]
    crop_box = normalized_box(crop, width, height) if crop else (0, 0, width, height)

    # Cover explicitly selected regions with opaque pixels; reversible blur can leak secrets.
    draw = ImageDraw.Draw(image)
    for left, top, right, bottom in boxes:
        draw.rectangle((left, top, right - 1, bottom - 1), fill=(24, 24, 27))

    image = image.crop(crop_box)
    crop_left, crop_top, crop_right, crop_bottom = crop_box
    crop_width, crop_height = image.size
    points = [((x * width - crop_left) / crop_width, (y * height - crop_top) / crop_height) for x, y in points]
    for point in points:
        normalized_point(point)

    width, height = image.size
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    radius = max(12, min(width, height) // 48)
    line = max(2, radius // 5)
    for index, (x, y) in enumerate(points, start=1):
        tx, ty = round(x * (width - 1)), round(y * (height - 1))
        # Place the numbered badge near the target, clamped within the image.
        bx = min(max(tx + radius * 2, radius + 2), width - radius - 2)
        by = min(max(ty - radius * 2, radius + 2), height - radius - 2)
        draw.line((bx, by, tx, ty), fill=(255, 64, 56), width=line)
        draw.ellipse((tx - radius, ty - radius, tx + radius, ty + radius), outline=(255, 64, 56), width=line)
        draw.ellipse((bx - radius, by - radius, bx + radius, by + radius), fill=(255, 64, 56), outline='white', width=line)
        label = str(index)
        bounds = draw.textbbox((0, 0), label, font=font)
        draw.text((bx - (bounds[2] - bounds[0]) / 2, by - (bounds[3] - bounds[1]) / 2), label, fill='white', font=font)

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix='.autoscribe-image-', suffix='.png', dir=output.parent, delete=False) as stream:
            temporary = Path(stream.name)
        image.save(temporary, format='PNG', optimize=True)
        os.replace(temporary, output)
    except OSError:
        raise ValidationError('无法保存处理后的截图；请检查输出目录权限和剩余空间') from None
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
    return {
        'path': relative_output.as_posix(), 'format': 'PNG', 'width': width, 'height': height,
        'redacted': bool(boxes), 'redactionCount': len(boxes),
        'calloutCount': len(points), 'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
    }
