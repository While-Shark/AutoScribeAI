"""M0 contract tests: validate failure modes, not only happy-path snapshots."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from autoscribe.state import atomic_json, initialize, load, locked, resume, transition
from autoscribe.validation import ValidationError, asset_path, read_json, validate, validate_manual
from jsonschema import Draft202012Validator


class FoundationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = read_json(ROOT / 'examples/project.json')
        self.config['source']['path'] = str(ROOT)
        self.config_path = self.root / 'project.json'
        self.config_path.write_text(json.dumps(self.config))
        self.run = self.root / 'run'

    def start(self):
        return initialize(self.config_path, self.run)

    def test_all_schemas_are_valid(self):
        for path in (ROOT / 'schemas').glob('*.json'):
            Draft202012Validator.check_schema(read_json(path))

    def test_invalid_config_and_no_input(self):
        for key in ('roles', 'scope', 'source'):
            data = copy.deepcopy(self.config)
            data.pop(key)
            with self.subTest(key=key), self.assertRaises(ValidationError):
                validate(data, 'project')
        self.config['source'] = {}
        with self.assertRaises(ValidationError):
            validate(self.config, 'project')

    def test_unknown_field_and_version_rejected(self):
        for key, value in [('unexpected', True), ('schemaVersion', '2')]:
            data = {**self.config, key: value}
            with self.assertRaises(ValidationError):
                validate(data, 'project')

    def test_secret_values_not_echoed(self):
        for change in ({'password': 'sensitive-example'}, {'testDataPolicy': 'token=sensitive-example'}):
            with self.assertRaises(ValidationError) as caught:
                validate({**self.config, **change}, 'project')
            self.assertNotIn('sensitive-example', str(caught.exception))

    def test_url_credentials_and_queries(self):
        for url in ('https://user:pass@example.org', 'https://example.org?token=x', 'file:///tmp', 'https://example.org#secret'):
            data = {**self.config, 'source': {'url': url}}
            with self.subTest(url=url), self.assertRaises(ValidationError):
                validate(data, 'project')

    def test_relative_source_and_source_only(self):
        self.config['source']['path'] = '.'
        self.config_path.write_text(json.dumps(self.config))
        state = self.start()
        self.assertEqual(state['config']['source']['path'], str(self.root))
        self.assertEqual(state['capabilities']['mode'], 'source-only')
        self.assertFalse(state['capabilities']['canExplore'])
        transition(self.run, 'analyze', 'running')
        transition(self.run, 'analyze', 'completed')
        with self.assertRaises(ValidationError):
            transition(self.run, 'explore', 'running')

    def test_no_source_blocks_preflight(self):
        self.config['source'] = {'url': 'https://example.org'}
        self.config_path.write_text(json.dumps(self.config))
        state = self.start()
        self.assertEqual(state['stages']['preflight']['status'], 'blocked')
        with self.assertRaises(ValidationError):
            transition(self.run, 'analyze', 'running')

    def test_declared_browser_and_fresh_resume(self):
        self.config['source']['url'] = 'https://example.org'
        self.config_path.write_text(json.dumps(self.config))
        host = {'browser': {'status': 'available', 'provider': 'test-host', 'screenshot': True}}
        state = initialize(self.config_path, self.run, host)
        self.assertTrue(state['capabilities']['canExplore'])
        resumed = resume(self.run)
        self.assertFalse(resumed['capabilities']['canExplore'])
        self.assertEqual(resumed['capabilities']['browser']['status'], 'unknown')

    def test_stage_dependencies_and_terminal_states(self):
        self.start()
        with self.assertRaises(ValidationError):
            transition(self.run, 'write', 'running')
        with self.assertRaises(ValidationError):
            transition(self.run, 'analyze', 'completed')
        transition(self.run, 'analyze', 'running')
        transition(self.run, 'analyze', 'completed')
        with self.assertRaises(ValidationError):
            transition(self.run, 'analyze', 'running')

    def test_required_reason(self):
        self.start()
        for status in ('blocked', 'skipped'):
            with self.assertRaises(ValidationError):
                transition(self.run, 'analyze', status)
        transition(self.run, 'analyze', 'skipped', 'scope excludes source analysis')

    def test_interrupt_resume_and_checkpoint_repair(self):
        self.start()
        transition(self.run, 'analyze', 'running')
        (self.run / 'checkpoint.json').write_text('{incomplete')
        restored = resume(self.run, self.config_path)
        self.assertFalse(restored['checkpoint']['replayActions'])
        self.assertEqual(restored['checkpoint']['nextStage'], 'analyze')
        self.assertEqual(load(self.run)['stages']['analyze']['status'], 'blocked')
        self.assertEqual(read_json(self.run / 'checkpoint.json'), restored['checkpoint'])
        transition(self.run, 'analyze', 'running')

    def test_config_change_does_not_mutate_state(self):
        self.start()
        original = (self.run / 'manifest.json').read_bytes()
        self.config['project']['version'] = 'v2'
        self.config_path.write_text(json.dumps(self.config))
        with self.assertRaises(ValidationError):
            resume(self.run, self.config_path)
        self.assertEqual((self.run / 'manifest.json').read_bytes(), original)

    def test_tampered_config(self):
        state = self.start()
        state['config']['scope'] = ['changed']
        (self.run / 'manifest.json').write_text(json.dumps(state))
        with self.assertRaises(ValidationError):
            load(self.run)

    def test_no_overwrite_and_writer_lock(self):
        self.start()
        with self.assertRaises(FileExistsError):
            self.start()
        with locked(self.run):
            with self.assertRaises(ValidationError):
                resume(self.run)
        self.assertFalse((self.run / '.state.lock').exists())

    def test_atomic_write_preserves_previous_on_failure(self):
        target = self.root / 'state.json'
        atomic_json(target, {'value': 1})
        with patch('autoscribe.state.os.replace', side_effect=OSError('failure')):
            with self.assertRaises(OSError):
                atomic_json(target, {'value': 2})
        self.assertEqual(read_json(target), {'value': 1})
        self.assertFalse(list(self.root.glob('.autoscribe-*')))

    def test_rejects_unsafe_paths(self):
        for path in ('../escape.png', '/tmp/escape.png', r'C:\escape.png'):
            with self.assertRaises(ValidationError):
                asset_path(self.root, path)
        (self.root / 'link').symlink_to('/tmp', target_is_directory=True)
        with self.assertRaises(ValidationError):
            asset_path(self.root, 'link/escape.png')

    def test_cli_json_error_without_raw_secret(self):
        self.config['password'] = 'sensitive-example'
        self.config_path.write_text(json.dumps(self.config))
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/autoscribe_cli.py'), 'validate', 'project', str(self.config_path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('error', json.loads(result.stderr))
        self.assertNotIn('sensitive-example', result.stderr + result.stdout)


class ManualTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # Synthetic signature fixture tests byte/hash rules, never a screenshot claim.
        raw = b'\x89PNG\r\n\x1a\nfixture'
        (self.root / 'test.png').write_bytes(raw)
        self.data = {
            'schemaVersion': '0.1', 'project': {'id': 'demo', 'name': 'Demo', 'environment': 'test'},
            'title': 'Fixture', 'roles': ['viewer'], 'limitations': ['Synthetic unit-test data only'],
            'modules': [{'id': 'm1', 'name': 'Module', 'source': 'source', 'location': 'src/routes'}],
            'features': [{'id': 'f1', 'moduleId': 'm1', 'name': 'Feature', 'roles': ['viewer'], 'source': 'source', 'location': '/list'}],
            'workflows': [{'id': 'w1', 'featureId': 'f1', 'role': 'viewer', 'goal': 'View', 'preconditions': [], 'successCriteria': 'List visible', 'status': 'verified', 'stepIds': ['s1']}],
            'steps': [{'id': 's1', 'workflowId': 'w1', 'order': 1, 'action': 'Open list', 'location': 'Menu', 'expectedResult': 'List', 'actualResult': 'List', 'source': 'observed', 'evidenceIds': ['e1']}],
            'evidence': [{'id': 'e1', 'stepIds': ['s1'], 'path': 'test.png', 'capturedAt': '2026-09-29T00:00:00Z', 'page': 'List', 'viewport': {'width': 800, 'height': 600}, 'source': 'observed', 'sha256': hashlib.sha256(raw).hexdigest(), 'redacted': False}],
            'chapters': [{'id': 'c1', 'moduleId': 'm1', 'title': 'Module', 'purpose': 'View lists', 'workflowIds': ['w1']}],
        }

    def check(self):
        return validate_manual(self.data, self.root)

    def test_valid_contract(self):
        self.check()

    def test_duplicate_id(self):
        self.data['steps'][0]['id'] = 'm1'
        with self.assertRaises(ValidationError): self.check()

    def test_missing_reference(self):
        self.data['features'][0]['moduleId'] = 'missing'
        with self.assertRaises(ValidationError): self.check()

    def test_wrong_role(self):
        self.data['workflows'][0]['role'] = 'admin'
        with self.assertRaises(ValidationError): self.check()

    def test_source_inference_is_not_verified(self):
        self.data['steps'][0]['source'] = 'source'
        with self.assertRaises(ValidationError): self.check()

    def test_verified_requires_actual_result(self):
        del self.data['steps'][0]['actualResult']
        with self.assertRaises(ValidationError): self.check()

    def test_verified_requires_evidence(self):
        self.data['steps'][0]['evidenceIds'] = []
        with self.assertRaises(ValidationError): self.check()

    def test_reverse_link(self):
        self.data['evidence'][0]['stepIds'] = ['other']
        with self.assertRaises(ValidationError): self.check()

    def test_step_order(self):
        self.data['steps'][0]['order'] = 2
        with self.assertRaises(ValidationError): self.check()

    def test_blocked_requires_reason(self):
        self.data['workflows'][0]['status'] = 'blocked'
        with self.assertRaises(ValidationError): self.check()

    def test_missing_image(self):
        (self.root / 'test.png').unlink()
        with self.assertRaises(ValidationError): self.check()

    def test_image_hash_mismatch(self):
        self.data['evidence'][0]['sha256'] = '0' * 64
        with self.assertRaises(ValidationError): self.check()

    def test_not_an_image(self):
        (self.root / 'test.png').write_bytes(b'not image')
        with self.assertRaises(ValidationError): self.check()


if __name__ == '__main__':
    unittest.main()
