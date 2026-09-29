import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from autoscribe.evidence_images import prepare_screenshot
from autoscribe.validation import ValidationError


class EvidenceImageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'capture.png'
        self.output = self.root / 'evidence' / 'processed.png'
        Image.new('RGB', (96, 80), (240, 240, 240)).save(self.source)
        self.source_hash = hashlib.sha256(self.source.read_bytes()).hexdigest()

    def test_masks_region_and_marks_target_in_derivative(self):
        result = prepare_screenshot(self.source, self.output, [(0.1, 0.1, 0.2, 0.2)], [(0.7, 0.5)], self.root)
        with Image.open(self.output) as processed:
            self.assertEqual(processed.size, (96, 80))
            self.assertEqual(processed.getpixel((15, 15)), (24, 24, 27))
            self.assertEqual(processed.getpixel((40, 15)), (240, 240, 240))
        self.assertEqual(result['path'], 'evidence/processed.png')
        self.assertTrue(result['redacted'])
        self.assertEqual(result['redactionCount'], 1)
        self.assertEqual(result['calloutCount'], 1)
        self.assertEqual(result['sha256'], hashlib.sha256(self.output.read_bytes()).hexdigest())

    def test_crop_preserves_redaction_and_transforms_markers(self):
        result = prepare_screenshot(self.source, self.output, [(0.2, 0.2, 0.1, 0.1)], [(0.7, 0.5)], self.root, (0.1, 0.1, 0.8, 0.8))
        with Image.open(self.output) as image:
            self.assertEqual(image.size, (77, 64))
            self.assertEqual(image.getpixel((15, 12)), (24, 24, 27))
        self.assertTrue(result['redacted'])

    def test_marker_outside_crop_is_rejected(self):
        with self.assertRaises(ValidationError):
            prepare_screenshot(self.source, self.output, callouts=[(0.95, 0.95)], evidence_root=self.root, crop=(0, 0, 0.5, 0.5))

    def test_source_is_not_modified(self):
        prepare_screenshot(self.source, self.output, [(0.1, 0.1, 0.2, 0.2)])
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(), self.source_hash)

    def test_output_must_stay_inside_evidence_root(self):
        outside = Path(self.temp.name) / 'outside.png'
        with self.assertRaisesRegex(ValidationError, '证据根目录'):
            prepare_screenshot(self.source, outside, evidence_root=self.root / 'evidence')

    def test_output_cannot_overwrite_source(self):
        with self.assertRaisesRegex(ValidationError, '另存'):
            prepare_screenshot(self.source, self.source)

    def test_out_of_bounds_redaction_rejected(self):
        for box in [(-0.1, 0.1, 0.2, 0.2), (0.9, 0.9, 0.2, 0.2), (0, 0, 0, 1)]:
            with self.subTest(box=box), self.assertRaises(ValidationError):
                prepare_screenshot(self.source, self.output, [box])

    def test_out_of_bounds_marker_rejected(self):
        for point in [(-0.1, 0.2), (0.5, 1.1), (0.3,)]:
            with self.subTest(point=point), self.assertRaises(ValidationError):
                prepare_screenshot(self.source, self.output, callouts=[point])

    def test_small_or_malformed_image_rejected(self):
        tiny = self.root / 'tiny.png'
        Image.new('RGB', (16, 16)).save(tiny)
        with self.assertRaisesRegex(ValidationError, '32'):
            prepare_screenshot(tiny, self.output)
        broken = self.root / 'broken.png'
        broken.write_bytes(b'not image')
        with self.assertRaises(ValidationError):
            prepare_screenshot(broken, self.output)

    def test_jpeg_input_is_converted_to_png(self):
        source = self.root / 'capture.jpg'
        Image.new('RGB', (96, 80), (80, 120, 160)).save(source)
        result = prepare_screenshot(source, self.output)
        self.assertEqual(result['format'], 'PNG')
        self.assertFalse(result['redacted'])
        with Image.open(self.output) as image:
            self.assertEqual(image.format, 'PNG')


if __name__ == '__main__':
    unittest.main()
