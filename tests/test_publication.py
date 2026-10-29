import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ai_client
import run_daily
import update_index
import utils

DATE = "2026-10-28"


def feed_text(feed, date=DATE):
    label = datetime.date.fromisoformat(date).strftime("%A, %B %d %Y")
    return (f"# {feed} — {label}\n\n---\n\n"
            "PROBLEM: A specific example\nSOLUTION_PYTHON: a solution\nSOLUTION_JS: a solution\n"
            "THE_PROMPT: Analyze the supplied example.\nWHEN_TO_USE: Practice reviewing an example.\n"
            "RESOURCE_TITLE: Official docs\nRESOURCE_URL: https://docs.python.org/3/\n"
            "WHAT_YOULL_LEARN: Python fundamentals and the way the language executes programs.\n"
            "[Read primary docs](https://docs.python.org/3/)\n\n"
            "[Browse](.)\n\n---\n\n*← [Back to Index](../../INDEX.md)*\n")


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "README.md").write_text(
            "# Digest\n\n<!-- AUTO-UPDATED DAILY — DO NOT EDIT MANUALLY -->\nOld state\n\n---\nNotes\n"
        )

    def fake_run(self, command, cwd, env, check, timeout):
        self.assertEqual(env["TECHPULSE_DATE"], DATE)
        self.assertTrue(check)
        self.assertLessEqual(timeout, 600)
        self.assertNotEqual(cwd, self.root)
        self.assertFalse((self.root / f"feeds/news/{DATE}.md").exists())
        script = Path(command[1]).name
        feed = next(f for f, (_, _, s) in update_index.FEEDS.items() if s == script)
        target = cwd / f"feeds/{feed}/{DATE}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(feed_text(feed))

    def run_fake(self, runner=None):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-only"}, clear=True):
            return run_daily.run_daily(self.root, DATE, runner or self.fake_run)

    def test_success_is_complete_and_rerun_is_noop(self):
        self.assertTrue(self.run_fake())
        status = json.loads((self.root / "STATUS.json").read_text())
        self.assertEqual(status["feeds_published"], 9)
        self.assertEqual(status["published_date"], DATE)
        before = {str(p.relative_to(self.root)): p.read_bytes()
                  for p in self.root.rglob("*") if p.is_file()}
        runner = Mock(side_effect=AssertionError("Rerun must not call a provider"))
        self.assertFalse(self.run_fake(runner))
        runner.assert_not_called()
        after = {str(p.relative_to(self.root)): p.read_bytes()
                 for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_source_process_failure_preserves_all_public_paths(self):
        original = (self.root / "README.md").read_bytes()
        def fails(*args, **kwargs):
            self.fake_run(*args, **kwargs)
            raise subprocess.CalledProcessError(1, args[0])
        with self.assertRaises(subprocess.CalledProcessError):
            self.run_fake(fails)
        self.assertEqual((self.root / "README.md").read_bytes(), original)
        self.assertFalse((self.root / "feeds").exists())
        self.assertFalse((self.root / "STATUS.json").exists())

    def test_zero_outputs_cannot_publish(self):
        with self.assertRaises(FileNotFoundError):
            self.run_fake(lambda *a, **k: None)
        self.assertFalse((self.root / "archive").exists())

    def test_partial_outputs_cannot_publish_even_with_legacy_same_date_files(self):
        path = self.root / f"feeds/learning/{DATE}.md"
        path.parent.mkdir(parents=True)
        path.write_text(feed_text("learning"))
        before = path.read_bytes()
        def partial(command, **kwargs):
            if Path(command[1]).name != "generate_learning.py":
                # Existing partial output is intentionally allowed in this test.
                cwd = kwargs["cwd"]
                feed = next(f for f, (_, _, s) in update_index.FEEDS.items()
                            if s == Path(command[1]).name)
                target = cwd / f"feeds/{feed}/{DATE}.md"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(feed_text(feed))
        with self.assertRaises(FileNotFoundError):
            self.run_fake(partial)
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse((self.root / "STATUS.json").exists())

    def test_malformed_output_cannot_publish(self):
        def malformed(command, **kwargs):
            self.fake_run(command, **kwargs)
            if Path(command[1]).name == "generate_learning.py":
                (kwargs["cwd"] / f"feeds/learning/{DATE}.md").write_text("# Empty")
        with self.assertRaises(ValueError):
            self.run_fake(malformed)
        self.assertFalse((self.root / "STATUS.json").exists())

    def test_broken_readme_marker_stops_transaction(self):
        (self.root / "README.md").write_text("Original content without a publication marker")
        with self.assertRaises(ValueError):
            self.run_fake()
        self.assertFalse((self.root / "archive").exists())

    def test_legacy_placeholder_archives_excluded_and_links_rebased(self):
        bad = self.root / "archive/2026/10/2026-10-29.md"
        bad.parent.mkdir(parents=True)
        bad.write_text("**Feeds:** 0/9 published\nNot yet published today.")
        self.run_fake()
        index = (self.root / "INDEX.md").read_text()
        self.assertNotIn("2026-10-29.md", index)
        archive = (self.root / update_index.archive_path(DATE)).read_text()
        self.assertIn("](../../../INDEX.md)", archive)
        self.assertIn("](../../../feeds/news)", archive)
        self.assertNotIn("commits", (self.root / "STATS.md").read_text().split("These are")[0])
        self.assertTrue(bad.exists())

    def test_validator_rejects_wrong_date_placeholder_unsafe_and_missing_source(self):
        path = self.root / "sample.md"
        for text in [feed_text("news", "2026-10-27"),
                     feed_text("news") + "\nTODO", feed_text("news") + "\n<script>alert(1)</script>",
                     feed_text("news") + "\n```python\nprint(1)",
                     feed_text("news").replace("https://docs.python.org/3/", "")]:
            with self.subTest(text=text[-60:]):
                path.write_text(text)
                with self.assertRaises(ValueError):
                    update_index.validate_feed(path, DATE, "news")

    def test_fixed_date_used_even_if_wall_clock_differs(self):
        with patch.dict(os.environ, {"TECHPULSE_DATE": DATE}):
            self.assertEqual(utils.today()[0], DATE)


class ProviderTests(unittest.TestCase):
    def test_unavailable_model_falls_back_without_leaking_error(self):
        class Error(Exception):
            status_code = 404
        with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy", "GROQ_API_KEY": "dummy"}, clear=True), \
                patch.object(ai_client, "_call_gemini", side_effect=Error("secret-test-value")), \
                patch.object(ai_client, "_call_groq", return_value="Valid generated response. " * 5):
            self.assertIn("Valid generated", ai_client.generate("system", "user"))

    def test_all_provider_failures_raise_without_system_exit_or_raw_error(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy"}, clear=True), \
                patch.object(ai_client, "_call_gemini", side_effect=RuntimeError("secret-test-value")):
            with self.assertRaises(ai_client.GenerationError) as ctx:
                ai_client.generate("system", "user")
            self.assertNotIn("secret-test-value", str(ctx.exception))

    def test_empty_response_and_no_credentials_fail(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ai_client.GenerationError):
                ai_client.check_configuration()
        for response in (None, "", "short"):
            with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy"}, clear=True), \
                    patch.object(ai_client, "_call_gemini", return_value=response):
                with self.assertRaises(ai_client.GenerationError):
                    ai_client.generate("system", "user")

    def test_transient_retries_bounded_and_404_not_retried(self):
        for status, attempts in ((503, 3), (404, 1)):
            error = RuntimeError("provider failure")
            error.status_code = status
            call = Mock(side_effect=error)
            with patch.object(ai_client.time, "sleep"):
                with self.assertRaises(RuntimeError):
                    ai_client._retry(call)
            self.assertEqual(call.call_count, attempts)


if __name__ == "__main__":
    unittest.main()
