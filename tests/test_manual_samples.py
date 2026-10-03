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
    def test_three_multilingual_samples_report_only_screenshot_backed_observations(self):
        samples = sorted(p for p in (ROOT / 'tests/manual_samples').iterdir() if p.is_dir())
        self.assertEqual({p.name for p in samples}, {'uptime-kuma', 'changedetection', 'it-tools'})
        expected_languages = {'uptime-kuma': 'zh-CN', 'changedetection': 'ja-JP', 'it-tools': 'ko-KR'}
        expected_verified = {'uptime-kuma': 3, 'changedetection': 0, 'it-tools': 1}
        expected_evidence = {'uptime-kuma': 6, 'changedetection': 1, 'it-tools': 1}
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
                validate_manual(manual, run)
                validate(coverage, 'coverage')
                validate(quality, 'quality-report')
                self.assertEqual(config['language'], expected_languages[sample.name])
                self.assertEqual(manual['project']['language'], config['language'])
                self.assertEqual(manual['project']['version'], inventory['projectVersion'])
                self.assertEqual(len(manual['workflows']), 3)
                self.assertEqual(len(manual['steps']), 9)
                self.assertEqual(len(manual['evidence']), expected_evidence[sample.name])
                self.assertEqual(coverage['verified'], expected_verified[sample.name])
                self.assertEqual(coverage['unverified'], 3 - expected_verified[sample.name])
                self.assertFalse(quality['ready'])
                self.assertEqual(quality['evidenceCount'], expected_evidence[sample.name])
                self.assertEqual(quality['copiedEvidenceCount'], expected_evidence[sample.name])
                self.assertEqual(manifest['stages']['explore']['status'], 'completed' if sample.name == 'uptime-kuma' else 'skipped')
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
                    image_assets = [name for name in archive.namelist() if name.startswith('assets/')]
                    self.assertEqual(len(image_assets), expected_evidence[sample.name])

                from docx import Document
                doc = Document(output / 'manual.docx')
                doc_text = '\n'.join(p.text for p in doc.paragraphs)
                self.assertIn(manual['title'], doc_text)
                self.assertTrue(all(w['goal'] in doc_text for w in manual['workflows']))
                self.assertEqual(len(doc.inline_shapes), sum(len(step['evidenceIds']) for step in manual['steps']))

                for evidence in manual['evidence']:
                    path = sample / 'run' / evidence['path']
                    self.assertTrue(path.is_file())
                    exported = output / 'evidence' / f"{evidence['id']}{path.suffix}"
                    self.assertTrue(exported.is_file())
                    self.assertIn(f'src="evidence/{evidence["id"]}{path.suffix}"', html)
                    self.assertIn(evidence['id'], '\n'.join(image_assets))

        uptime = ROOT / 'tests/manual_samples/uptime-kuma'
        kuma_manual = read_json(uptime / 'run/manual.json')
        self.assertEqual([w['status'] for w in kuma_manual['workflows']], ['verified', 'verified', 'verified'])
        self.assertTrue(all(step['source'] == 'observed' and step.get('actualResult') and step['evidenceIds'] for step in kuma_manual['steps']))
        self.assertTrue(any('example.invalid' in item for item in kuma_manual['limitations']))

        it_tools = ROOT / 'tests/manual_samples/it-tools'
        it_manual = read_json(it_tools / 'run/manual.json')
        self.assertEqual([w['status'] for w in it_manual['workflows']], ['verified', 'unverified', 'unverified'])
        self.assertTrue(all(s['source'] == 'observed' and s.get('actualResult') and s['evidenceIds'] for s in it_manual['steps'][:3]))
        self.assertTrue(all(s['source'] == 'source' and not s['evidenceIds'] and 'actualResult' not in s for s in it_manual['steps'][3:]))

        changedetection = ROOT / 'tests/manual_samples/changedetection'
        cd_manual = read_json(changedetection / 'run/manual.json')
        observed = cd_manual['steps'][0]
        self.assertEqual(observed['source'], 'observed')
        self.assertTrue(observed['actualResult'])
        self.assertEqual(cd_manual['workflows'][0]['status'], 'unverified')
        self.assertEqual(cd_manual['evidence'][0]['page'], 'https://changedetection.io/')

        samples_readme = (ROOT / 'tests/manual_samples/README.md').read_text(encoding='utf-8')
        self.assertIn('uptime-kuma/screenshots/monitor-created-dashboard.jpg', samples_readme)
        self.assertIn('changedetection/screenshots/changedetection-public-homepage.jpg', samples_readme)
        self.assertIn('it-tools/output/evidence/ev-it-tools-json-yaml.jpg', samples_readme)


if __name__ == '__main__':
    unittest.main()
