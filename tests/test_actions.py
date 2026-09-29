import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from autoscribe.actions import begin_action, load_actions, resolve_action
from autoscribe.state import initialize, resume, transition
from autoscribe.validation import ValidationError, read_json


class ActionJournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        config = read_json(ROOT / 'examples/project.json')
        config['source'] = {'url': 'https://example.invalid'}
        config['allowedActions'] = ['read', 'publish']
        self.config_path = self.root / 'project.json'
        self.config_path.write_text(json.dumps(config))
        self.run = self.root / 'run'
        host = {'browser': {'status': 'available', 'provider': 'fixture-host', 'screenshot': True}}
        initialize(self.config_path, self.run, host)
        transition(self.run, 'analyze', 'running')
        transition(self.run, 'analyze', 'completed')
        transition(self.run, 'explore', 'running')

    def begin(self):
        return begin_action(self.run, 'w-publish', 's-submit', 'publish', 'draft-alpha')

    def test_requires_explicitly_allowed_operation(self):
        with self.assertRaisesRegex(ValidationError, '授权范围'):
            begin_action(self.run, 'w-send', 's-send', 'send', 'test-notification')

    def test_deduplicates_unresolved_and_completed_action(self):
        first = self.begin()
        with self.assertRaisesRegex(ValidationError, '已有执行记录'):
            self.begin()
        resolved = resolve_action(self.run, first['actionId'], 'completed')
        self.assertEqual(resolved['status'], 'completed')
        with self.assertRaisesRegex(ValidationError, '已有执行记录'):
            self.begin()

    def test_retry_requires_explicit_no_effect_check(self):
        first = self.begin()
        with self.assertRaisesRegex(ValidationError, '核查结论'):
            resolve_action(self.run, first['actionId'], 'not-applied')
        retryable = resolve_action(self.run, first['actionId'], 'not-applied', '在目标系统确认草稿未创建')
        self.assertEqual(retryable['status'], 'retryable')
        second = self.begin()
        self.assertEqual(second['attempt'], 2)
        self.assertEqual(first['actionId'], second['actionId'])

    def test_resume_blocks_in_flight_action(self):
        first = self.begin()
        restored = resume(self.run, self.config_path)
        ledger = restored['actions']
        self.assertEqual(ledger['actions'][0]['status'], 'blocked')
        with self.assertRaisesRegex(ValidationError, '核对目标结果'):
            self.begin()
        with self.assertRaisesRegex(ValidationError, '核查依据'):
            resolve_action(self.run, first['actionId'], 'completed')
        resolve_action(self.run, first['actionId'], 'completed', '目标系统已显示对应草稿')
        with self.assertRaisesRegex(ValidationError, '已有执行记录'):
            self.begin()

    def test_uncertain_result_stays_blocked(self):
        first = self.begin()
        blocked = resolve_action(self.run, first['actionId'], 'uncertain', '等待页面加载后仍无法判断结果')
        self.assertEqual(blocked['status'], 'blocked')
        with self.assertRaises(ValidationError):
            self.begin()

    def test_action_log_contains_no_business_payload(self):
        self.begin()
        raw = (self.run / 'actions.json').read_text()
        self.assertNotIn('password', raw.lower())
        self.assertNotIn('cookie', raw.lower())

    def test_action_ledger_matches_schema(self):
        self.begin()
        ledger = load_actions(self.run)
        from autoscribe.validation import validate
        self.assertEqual(validate(ledger, 'actions')['actions'][0]['status'], 'begun')

    def test_unknown_operation_rejected(self):
        with self.assertRaisesRegex(ValidationError, '副作用'):
            begin_action(self.run, 'w-1', 's-1', 'read', 'home-page')


if __name__ == '__main__':
    unittest.main()
