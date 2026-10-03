"""Exercise interruption, change review and package integrity on real artifacts."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from autoscribe.actions import test_data_report as cleanup_report
from autoscribe.audit import audit_package
from autoscribe.diff import compare_manuals
from autoscribe.html_renderer import render_html
from autoscribe.inventory import create_coverage_plan, coverage_report, inventory_to_manual
from autoscribe.progress import read_progress, update_progress
from autoscribe.role_view import for_role
from autoscribe.locale_check import compare_locales
from autoscribe.docx_renderer import render_docx
from autoscribe.markdown_renderer import render_markdown_zip
from autoscribe.state import atomic_json, initialize, resume, transition
from autoscribe.validation import ValidationError, read_json, validate_manual


class ImprovementTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = read_json(ROOT / 'examples/project.json')
        self.config['source']['path'] = str(ROOT)
        self.config_path = self.root / 'project.json'
        atomic_json(self.config_path, self.config)
        self.inventory_path = self.root / 'inventory.json'
        atomic_json(self.inventory_path, read_json(ROOT / 'examples/inventory.json'))

    def test_workflow_resume_blocks_in_flight_and_keeps_completed(self):
        run = self.root / 'run'
        self.config['source']['url'] = 'https://example.org'
        atomic_json(self.config_path, self.config)
        initialize(self.config_path, run, {'browser': {'status': 'available', 'provider': 'test', 'screenshot': True}})
        create_coverage_plan(self.inventory_path, self.config_path, run / 'coverage-plan.json')
        transition(run, 'analyze', 'running')
        transition(run, 'analyze', 'completed')
        transition(run, 'explore', 'running')
        with self.assertRaises(ValidationError):
            update_progress(run, 'not-in-plan', 'running', 'check')
        update_progress(run, 'w-readme', 'running', 'page opened')
        update_progress(run, 'w-validate', 'running', 'form observed')
        update_progress(run, 'w-validate', 'completed', 'result checked')
        restored = resume(run, self.config_path)
        items = restored['workflowProgress']['workflows']
        self.assertEqual(items['w-readme']['status'], 'blocked')
        self.assertEqual(items['w-validate']['status'], 'completed')
        self.assertEqual(read_progress(run)['workflows'], items)
        self.assertFalse(restored['checkpoint']['replayActions'])

    def test_version_diff_requires_review_even_with_stable_ids(self):
        old = inventory_to_manual(read_json(self.inventory_path), self.config)
        old_path, new_path = self.root / 'old.json', self.root / 'new.json'
        atomic_json(old_path, old)
        new = copy.deepcopy(old)
        new['project']['version'] = 'demo-v2'
        new['workflows'][0]['goal'] = 'Changed goal'
        atomic_json(new_path, new)
        result = compare_manuals(old_path, new_path)
        self.assertEqual(result['changed'], ['w-readme'])
        self.assertEqual(set(result['reviewRequired']), {w['id'] for w in old['workflows']})

    def test_locale_check_flags_stale_structure(self):
        source = inventory_to_manual(read_json(self.inventory_path), self.config)
        translated = copy.deepcopy(source)
        translated['project']['language'] = 'ja-JP'
        source_path, translated_path = self.root / 'source.json', self.root / 'ja.json'
        atomic_json(source_path, source)
        atomic_json(translated_path, translated)
        self.assertTrue(compare_locales(source_path, translated_path)['aligned'])
        translated['workflows'][0]['status'] = 'blocked'
        translated['workflows'][0]['reason'] = 'Unable to access the page'
        atomic_json(translated_path, translated)
        self.assertIn('workflows/w-readme', compare_locales(source_path, translated_path)['differences'])

    def test_audit_detects_broken_package_link(self):
        manual = inventory_to_manual(read_json(self.inventory_path), self.config)
        manual_path = self.root / 'manual.json'
        atomic_json(manual_path, manual)
        plan_path, coverage_path = self.root / 'plan.json', self.root / 'coverage.json'
        create_coverage_plan(self.inventory_path, self.config_path, plan_path)
        coverage_report(plan_path, self.inventory_path, self.config_path, manual_path, coverage_path)
        package = self.root / 'package'
        render_html(manual_path, coverage_path, package)
        good = audit_package(manual_path, coverage_path, package, self.root / 'audit.json')
        self.assertTrue(good['mechanicalChecksPassed'])
        page = package / 'index.html'
        page.write_text(page.read_text() + '<a href="missing.html">broken</a>')
        bad = audit_package(manual_path, coverage_path, package, self.root / 'audit.json')
        self.assertIn('broken-link', {item['code'] for item in bad['findings']})
        page.write_bytes(b'\xff\xfe')
        corrupt = audit_package(manual_path, coverage_path, package, self.root / 'audit.json')
        self.assertIn('invalid-html', {item['code'] for item in corrupt['findings']})

    def test_audit_detects_changed_evidence_and_missing_content(self):
        manual = inventory_to_manual(read_json(self.inventory_path), self.config)
        image_path = self.root / 'evidence' / 'screen.png'
        image_path.parent.mkdir()
        Image.new('RGB', (96, 64), (220, 230, 240)).save(image_path)
        workflow = manual['workflows'][0]
        workflow.update(status='verified', stepIds=['step-screen'])
        manual['steps'] = [{'id': 'step-screen', 'workflowId': workflow['id'], 'order': 1,
                            'action': 'Open the page', 'location': 'Menu', 'expectedResult': 'Page opens',
                            'actualResult': 'Page opened', 'source': 'observed', 'evidenceIds': ['ev-screen']}]
        manual['evidence'] = [{'id': 'ev-screen', 'stepIds': ['step-screen'], 'path': 'evidence/screen.png',
                               'capturedAt': '2026-10-03T00:00:00Z', 'page': 'Example page',
                               'viewport': {'width': 96, 'height': 64}, 'source': 'observed',
                               'sha256': hashlib.sha256(image_path.read_bytes()).hexdigest(), 'redacted': False}]
        manual_path = self.root / 'manual.json'
        atomic_json(manual_path, manual)
        plan, coverage, package = self.root / 'plan.json', self.root / 'coverage.json', self.root / 'html'
        create_coverage_plan(self.inventory_path, self.config_path, plan)
        coverage_report(plan, self.inventory_path, self.config_path, manual_path, coverage)
        render_html(manual_path, coverage, package)

        copied = package / 'evidence' / 'ev-screen.png'
        Image.new('RGB', (96, 64), (10, 20, 30)).save(copied)
        html = package / 'index.html'
        html.write_text(html.read_text().replace(workflow['goal'], 'Removed heading'))
        (package / 'manual.json').write_text('{}')
        quality = read_json(package / 'quality-report.json')
        quality['manualSha256'] = '0' * 64
        atomic_json(package / 'quality-report.json', quality)
        from docx import Document
        docx = package / 'manual.docx'
        document = Document(docx)
        for paragraph in document.paragraphs:
            if workflow['goal'] == paragraph.text:
                paragraph.text = 'Removed heading'
        document.save(docx)
        markdown_zip = package / 'manual-markdown.zip'
        with zipfile.ZipFile(markdown_zip) as archive:
            contents = {name: archive.read(name) for name in archive.namelist()}
        contents['README.md'] = contents['README.md'].replace(workflow['goal'].encode(), b'Removed heading')
        contents['assets/ev-screen.png'] = b'changed image'
        with zipfile.ZipFile(markdown_zip, 'w') as archive:
            for name, data in contents.items():
                archive.writestr(name, data)
        result = audit_package(manual_path, coverage, package, self.root / 'audit.json')
        codes = {item['code'] for item in result['findings']}
        self.assertFalse(result['mechanicalChecksPassed'])
        self.assertTrue({'changed-copied-evidence', 'changed-package-file', 'stale-quality-report',
                         'missing-html-content', 'missing-docx-content', 'missing-markdown-content',
                         'changed-markdown-evidence'} <= codes)

    def test_cleanup_report_only_counts_confirmed_deletes(self):
        run = self.root / 'run'
        run.mkdir()
        atomic_json(run / 'actions.json', {'schemaVersion': '0.1', 'actions': [
            {'id': 'act-' + 'a' * 32, 'workflowId': 'w-readme', 'stepId': 's-1', 'operation': 'create-test-data', 'targetRef': 'test-monitor', 'status': 'completed', 'attempts': 1, 'firstStartedAt': '2026-10-01T00:00:00Z', 'lastStartedAt': '2026-10-01T00:00:00Z', 'completedAt': '2026-10-01T00:00:01Z'},
        ], 'events': []})
        self.assertEqual(cleanup_report(run)['remaining'], ['test-monitor'])

    def test_role_export_projection_only_contains_selected_workflow(self):
        manual = inventory_to_manual(read_json(self.inventory_path), self.config)
        manual['roles'].append('admin')
        manual['features'][0]['roles'].append('admin')
        manual['workflows'][0]['role'] = 'admin'
        manual['chapters'][0]['faqs'] = [
            {'question': 'General question', 'answer': 'For all roles', 'source': 'human'},
            {'question': 'Admin question', 'answer': 'Admin answer', 'source': 'human', 'workflowIds': ['w-readme']},
        ]
        projected = for_role(manual, 'admin')
        validate_manual(projected, self.root)
        self.assertEqual(projected['roles'], ['admin'])
        self.assertEqual([w['id'] for w in projected['workflows']], ['w-readme'])
        self.assertEqual(len(projected['features']), 1)
        self.assertEqual(len(projected['chapters'][0]['faqs']), 2)
        path = self.root / 'manual.json'
        atomic_json(path, manual)
        render_docx(path, self.root / 'admin.docx', role='admin')
        render_markdown_zip(path, self.root / 'admin.zip', role='admin')
        from docx import Document
        from zipfile import ZipFile
        text = '\n'.join(p.text for p in Document(self.root / 'admin.docx').paragraphs)
        self.assertIn(manual['workflows'][0]['goal'], text)
        self.assertIn('General question', text)
        self.assertNotIn(manual['workflows'][1]['goal'], text)
        with ZipFile(self.root / 'admin.zip') as archive:
            markdown = archive.read('README.md').decode()
        self.assertIn(manual['workflows'][0]['goal'], markdown)
        self.assertIn('General question', markdown)
        self.assertNotIn(manual['workflows'][1]['goal'], markdown)

    def test_html_marks_faq_workflow_scope_for_role_filter(self):
        manual = inventory_to_manual(read_json(self.inventory_path), self.config)
        manual['chapters'][0]['faqs'] = [
            {'question': 'General question', 'answer': 'For all roles', 'source': 'human'},
            {'question': 'Related question', 'answer': 'Only this workflow', 'source': 'human', 'workflowIds': ['w-readme']},
        ]
        manual_path = self.root / 'manual.json'
        atomic_json(manual_path, manual)
        plan, coverage, package = self.root / 'plan.json', self.root / 'coverage.json', self.root / 'html'
        create_coverage_plan(self.inventory_path, self.config_path, plan)
        coverage_report(plan, self.inventory_path, self.config_path, manual_path, coverage)
        render_html(manual_path, coverage, package)
        html = (package / 'index.html').read_text()
        self.assertIn('data-workflows="w-readme"', html)
        self.assertIn('data-workflows=""', html)
        self.assertIn("refs.every(id=>document.getElementById('workflow-'+id)?.dataset.role===role.value)", html)


if __name__ == '__main__':
    unittest.main()
