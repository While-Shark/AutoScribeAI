import json
import sys
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from autoscribe.validation import read_json, validate, validate_manual


class ManualSampleTests(unittest.TestCase):
    def test_three_source_only_multilingual_exports_are_consistent(self):
        samples = sorted(p for p in (ROOT / 'tests/manual_samples').iterdir() if p.is_dir())
        self.assertEqual({p.name for p in samples}, {'uptime-kuma', 'changedetection', 'it-tools'})
        expected_languages = {'uptime-kuma': 'zh-CN', 'changedetection': 'ja-JP', 'it-tools': 'ko-KR'}
        for sample in samples:
            with self.subTest(sample=sample.name):
                config = read_json(sample / 'project.json')
                inventory = read_json(sample / 'inventory.json')
                run = sample / 'run'
                output = sample / 'output'
                manual = read_json(run / 'manual.json')
                coverage = read_json(run / 'coverage.json')
                quality = read_json(output / 'quality-report.json')
                manifest = read_json(run / 'manifest.json')

                validate(config, 'project')
                validate(inventory, 'inventory')
                validate_manual(manual, sample)
                validate(coverage, 'coverage')
                validate(quality, 'quality-report')
                self.assertEqual(config['language'], expected_languages[sample.name])
                self.assertEqual(manual['project']['language'], config['language'])
                self.assertEqual(manual['project']['version'], inventory['projectVersion'])
                self.assertEqual(len(manual['workflows']), 3)
                self.assertEqual(len(manual['steps']), 9)
                self.assertEqual(manual['evidence'], [])
                self.assertTrue(all(w['status'] == 'unverified' for w in manual['workflows']))
                self.assertTrue(all(s['source'] == 'source' and not s['evidenceIds'] and 'actualResult' not in s for s in manual['steps']))
                self.assertEqual(coverage['verified'], 0)
                self.assertEqual(coverage['unverified'], 3)
                self.assertFalse(quality['ready'])
                self.assertEqual(quality['evidenceCount'], 0)
                self.assertEqual(manifest['stages']['explore']['status'], 'skipped')
                self.assertEqual(manifest['stages']['export']['status'], 'completed')
                self.assertEqual(manifest['stages']['verify']['status'], 'completed')

                for filename in ('index.html', 'manual.docx', 'manual-markdown.zip', 'manual.json', 'coverage.json', 'quality-report.json'):
                    self.assertTrue((output / filename).is_file(), filename)
                html = (output / 'index.html').read_text(encoding='utf-8')
                self.assertIn(f'<html lang="{config["language"]}">', html)
                self.assertIn(manual['title'], html)
                self.assertEqual(read_json(output / 'manual.json'), manual)
                self.assertEqual(read_json(output / 'coverage.json'), coverage)

                with zipfile.ZipFile(output / 'manual-markdown.zip') as archive:
                    markdown = archive.read('README.md').decode('utf-8')
                    self.assertTrue(all(w['goal'] in markdown for w in manual['workflows']))
                    self.assertTrue(all(f['question'] in markdown for c in manual['chapters'] for f in c.get('faqs', [])))
                    self.assertEqual(archive.namelist(), ['README.md'])

                from docx import Document
                doc = Document(output / 'manual.docx')
                doc_text = '\n'.join(p.text for p in doc.paragraphs)
                self.assertIn(manual['title'], doc_text)
                self.assertTrue(all(w['goal'] in doc_text for w in manual['workflows']))
                with zipfile.ZipFile(output / 'manual.docx') as archive:
                    media = [name for name in archive.namelist() if name.startswith('word/media/')]
                    self.assertEqual(media, [])


if __name__ == '__main__':
    unittest.main()
