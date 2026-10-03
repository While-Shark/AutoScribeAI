import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from autoscribe.inventory import create_coverage_plan, coverage_report, inventory_to_manual
from autoscribe.validation import ValidationError, read_json, validate
from autoscribe.state import atomic_json


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = read_json(ROOT / 'examples/project.json')
        self.inventory = read_json(ROOT / 'examples/inventory.json')
        self.config_path = self.root / 'project.json'
        self.inventory_path = self.root / 'inventory.json'
        self.manual_path = self.root / 'manual.json'
        self.plan_path = self.root / 'coverage-plan.json'
        self.report_path = self.root / 'coverage.json'
        self.config_path.write_text(json.dumps(self.config))
        self.inventory_path.write_text(json.dumps(self.inventory))

    def prepare(self):
        manual = inventory_to_manual(self.inventory, self.config)
        atomic_json(self.manual_path, manual)
        create_coverage_plan(self.inventory_path, self.config_path, self.plan_path)
        return manual

    def report(self):
        return coverage_report(self.plan_path, self.inventory_path, self.config_path, self.manual_path, self.report_path)

    def test_schema_definitions(self):
        for kind in ('inventory', 'coverage-plan', 'coverage'):
            from jsonschema import Draft202012Validator
            Draft202012Validator.check_schema(read_json(ROOT / 'schemas' / f'{kind}.schema.json'))

    def test_inventory_import_keeps_all_workflows_unverified(self):
        manual = inventory_to_manual(self.inventory, self.config)
        self.assertEqual(len(manual['workflows']), 3)
        self.assertTrue(all(w['status'] == 'unverified' and w['stepIds'] == [] for w in manual['workflows']))
        self.assertEqual({m['id'] for m in manual['modules']}, {'m-overview', 'm-automation'})

    def test_coverage_uses_original_plan_and_module_breakdown(self):
        manual = self.prepare()
        manual['workflows'][0]['status'] = 'blocked'
        manual['workflows'][0]['reason'] = '没有在线环境'
        atomic_json(self.manual_path, manual)
        report = self.report()
        self.assertEqual((report['planned'], report['verified'], report['blocked'], report['unverified']), (3, 0, 1, 2))
        self.assertEqual(report['coverage'], 0)
        modules = {m['id']: m for m in report['modules']}
        self.assertEqual(modules['m-overview']['blocked'], 1)
        self.assertEqual(modules['m-automation']['planned'], 2)

    def test_only_evidence_backed_verified_workflow_counts(self):
        manual = self.prepare()
        image = b'\xff\xd8\xff\xd9'
        (self.root / 'evidence').mkdir()
        (self.root / 'evidence' / 'step.jpg').write_bytes(image)
        manual['workflows'][0]['status'] = 'verified'
        manual['workflows'][0]['stepIds'] = ['step-readme']
        manual['steps'] = [{
            'id': 'step-readme', 'workflowId': 'w-readme', 'order': 1,
            'action': '打开项目文档', 'location': 'README',
            'expectedResult': '显示项目功能说明', 'actualResult': '显示项目功能说明',
            'source': 'observed', 'evidenceIds': ['evidence-readme'],
        }]
        manual['evidence'] = [{
            'id': 'evidence-readme', 'stepIds': ['step-readme'],
            'path': 'evidence/step.jpg', 'capturedAt': '2026-09-29T08:00:00Z',
            'page': 'README', 'viewport': {'width': 800, 'height': 600},
            'source': 'observed', 'sha256': hashlib.sha256(image).hexdigest(), 'redacted': True,
        }]
        atomic_json(self.manual_path, manual)
        report = self.report()
        self.assertEqual((report['verified'], report['planned'], report['coverageDisplay']), (1, 3, '1/3'))
        self.assertEqual(report['scopeItems'][0]['coverageDisplay'], '1/3')

    def test_zero_workflow_denominator_is_not_applicable(self):
        self.inventory['workflows'] = []
        self.inventory['scopeItems'] = [{'scope': self.inventory['scope'][0], 'workflowIds': [], 'reason': '源码盘点未发现可覆盖流程'}]
        self.inventory_path.write_text(json.dumps(self.inventory))
        self.prepare()
        report = self.report()
        self.assertIsNone(report['coverage'])
        self.assertEqual(report['coverageDisplay'], '不适用（无计划流程）')

    def test_omitted_planned_flow_is_rejected(self):
        manual = self.prepare()
        manual['workflows'].pop()
        self.manual_path.write_text(json.dumps(manual))
        with self.assertRaisesRegex(ValidationError, '原计划'):
            self.report()

    def test_added_unplanned_flow_is_rejected(self):
        manual = self.prepare()
        extra = copy.deepcopy(manual['workflows'][0])
        extra['id'] = 'w-extra'
        manual['workflows'].append(extra)
        self.manual_path.write_text(json.dumps(manual))
        with self.assertRaisesRegex(ValidationError, '原计划'):
            self.report()

    def test_inventory_change_requires_replanning(self):
        self.prepare()
        self.inventory['workflows'].pop()
        self.inventory_path.write_text(json.dumps(self.inventory))
        with self.assertRaisesRegex(ValidationError, '清单.*变化'):
            self.report()

    def test_scope_change_requires_new_plan(self):
        self.prepare()
        self.config['scope'] = ['其他范围']
        self.config_path.write_text(json.dumps(self.config))
        with self.assertRaisesRegex(ValidationError, '运行范围'):
            self.report()

    def test_wrong_project_version_is_rejected(self):
        self.inventory['projectVersion'] = 'other-version'
        with self.assertRaisesRegex(ValidationError, '项目版本'):
            inventory_to_manual(self.inventory, self.config)

    def test_scope_item_cannot_be_silently_dropped(self):
        self.inventory['scopeItems'] = []
        with self.assertRaisesRegex(ValidationError, '全部范围'):
            inventory_to_manual(self.inventory, self.config)

    def test_workflow_must_be_counted_under_scope(self):
        self.inventory['scopeItems'][0]['workflowIds'].pop()
        with self.assertRaisesRegex(ValidationError, '归入至少'):
            inventory_to_manual(self.inventory, self.config)

    def test_feature_cannot_claim_undeclared_role(self):
        self.inventory['features'][0]['roles'] = ['admin']
        with self.assertRaisesRegex(ValidationError, '运行配置'):
            inventory_to_manual(self.inventory, self.config)

    def test_workflow_must_map_to_feature_and_role(self):
        self.inventory['workflows'][0]['featureId'] = 'missing-feature'
        with self.assertRaises(ValidationError):
            inventory_to_manual(self.inventory, self.config)
        self.inventory['workflows'][0]['featureId'] = 'f-purpose'
        self.inventory['workflows'][0]['role'] = 'admin'
        with self.assertRaisesRegex(ValidationError, '角色'):
            inventory_to_manual(self.inventory, self.config)

    def test_missing_language_defaults_to_english(self):
        config = copy.deepcopy(self.config)
        config.pop('language')
        validate(config, 'project')
        manual = inventory_to_manual(self.inventory, config)
        self.assertEqual(manual['project']['language'], 'en-US')
        self.assertEqual(manual['title'], 'Example Project User Manual')
        self.assertIn('Not yet executed and verified', manual['workflows'][0]['reason'])

    def test_cli_end_to_end(self):
        subprocess = __import__('subprocess')
        import sys
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/autoscribe_cli.py'), 'analyze', '--config', str(ROOT / 'examples/project.json'), '--inventory', str(ROOT / 'examples/inventory.json'), '--manual-out', str(self.manual_path), '--plan-out', str(self.plan_path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(read_json(self.manual_path)['workflows']), 3)
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/autoscribe_cli.py'), 'coverage', '--plan', str(self.plan_path), '--inventory', str(ROOT / 'examples/inventory.json'), '--config', str(ROOT / 'examples/project.json'), '--manual', str(self.manual_path), '--out', str(self.report_path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(read_json(self.report_path)['coverage'], 0)


if __name__ == '__main__':
    unittest.main()
