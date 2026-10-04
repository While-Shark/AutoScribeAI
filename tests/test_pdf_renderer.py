"""Exercise optional PDF conversion with a real, screenshot-backed manual."""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from autoscribe.pdf_renderer import render_pdf
from autoscribe.validation import ValidationError


class PdfRendererTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name) / 'manual.pdf'
        self.manual = ROOT / 'tests/manual_samples/it-tools/run/manual.json'

    def test_missing_converter_and_existing_output_do_not_modify_files(self):
        with self.assertRaisesRegex(ValidationError, 'LibreOffice'):
            render_pdf(self.manual, self.out, soffice='/missing/autoscribe-soffice')
        self.assertFalse(self.out.exists())
        self.out.write_bytes(b'keep existing file')
        with self.assertRaisesRegex(ValidationError, '已存在'):
            render_pdf(self.manual, self.out)
        self.assertEqual(self.out.read_bytes(), b'keep existing file')

    @unittest.skipUnless(shutil.which('soffice'), 'LibreOffice is optional')
    def test_real_sample_converts_to_valid_pdf(self):
        result = render_pdf(self.manual, self.out)
        self.assertEqual(result['path'], 'manual.pdf')
        self.assertEqual(result['bytes'], self.out.stat().st_size)
        self.assertGreater(result['bytes'], 1000)
        with self.out.open('rb') as stream:
            self.assertEqual(stream.read(5), b'%PDF-')


if __name__ == '__main__':
    unittest.main()
