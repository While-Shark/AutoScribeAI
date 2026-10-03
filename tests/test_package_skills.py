import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from package_skills import build_bundle


class SkillsBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_bundle_is_reproducible_and_contains_runtime_dependencies(self):
        first = self.root / 'first.zip'
        second = self.root / 'second.zip'
        result = build_bundle(first)
        build_bundle(second)
        self.assertGreater(result['files'], 30)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        with zipfile.ZipFile(first) as archive:
            self.assertIsNone(archive.testzip())
            names = set(archive.namelist())
        skill_paths = sorted({
            name.split('/')[2] for name in names
            if name.startswith('AutoScribeAI/skills/') and name.endswith('/SKILL.md')
        })
        self.assertEqual(skill_paths, [
            'autoscribe-manual-verifier', 'autoscribe-manual-writer',
            'autoscribe', 'autoscribe-project-analyzer',
            'autoscribe-software-explorer',
        ])
        for path in (
            'AutoScribeAI/skills/autoscribe/SKILL.md',
            'AutoScribeAI/skills/autoscribe-manual-writer/SKILL.md',
            'AutoScribeAI/references/RUN_PROTOCOL.md',
            'AutoScribeAI/schemas/manual.schema.json',
            'AutoScribeAI/scripts/autoscribe_cli.py',
            'AutoScribeAI/docs/INSTALLATION.md',
        ):
            self.assertIn(path, names)
        self.assertFalse(any('/tests/' in name or '/.git/' in name for name in names))

    def test_extracted_bundle_cli_runs_without_repository_checkout(self):
        bundle = self.root / 'bundle.zip'
        build_bundle(bundle)
        extracted = self.root / 'extracted'
        with zipfile.ZipFile(bundle) as archive:
            archive.extractall(extracted)
        repo = extracted / 'AutoScribeAI'
        help_result = subprocess.run(
            [sys.executable, str(repo / 'scripts/autoscribe_cli.py'), '--help'],
            check=False, capture_output=True, text=True,
        )
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        validate_result = subprocess.run(
            [sys.executable, str(repo / 'scripts/autoscribe_cli.py'),
             'validate', 'project', str(repo / 'examples/project.json')],
            check=False, capture_output=True, text=True,
        )
        self.assertEqual(validate_result.returncode, 0, validate_result.stderr)
        self.assertIn('"valid": true', validate_result.stdout)

    def test_existing_output_is_preserved(self):
        output = self.root / 'existing.zip'
        output.write_bytes(b'keep')
        with self.assertRaises(FileExistsError):
            build_bundle(output)
        self.assertEqual(output.read_bytes(), b'keep')


if __name__ == '__main__':
    unittest.main()
