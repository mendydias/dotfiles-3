"""Regression tests for the personal Orca guide (Python standard library only)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import keybind_sheet as sheet


class KeybindSheetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def document(self, name, data):
        path = self.root / name
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_linux_wins_and_other_platform_is_ignored(self):
        path = self.document("orca.json", {
            "version": 1, "keybindings": {"tab.close": ["Ctrl+W"]},
            "platforms": {"linux": {"tab.close": ["Ctrl+Alt+Shift+T"]},
                          "darwin": {"tab.close": ["Cmd+Q"]}},
        })
        rows, reserved = sheet.read_orca(path)
        self.assertEqual([item["trigger"] for item in rows], ["Ctrl+Alt+Shift+T"])
        self.assertNotIn("Ctrl+W", reserved)

    def test_legacy_root_overrides(self):
        rows, _ = sheet.read_orca(self.document("orca.json", {"version": 1, "tab.close": ["Ctrl+W"]}))
        self.assertEqual(rows[0]["raw"], "tab.close")

    def test_disabled_override_masks_common_and_is_not_counted(self):
        path = self.document("orca.json", {"keybindings": {"tab.close": ["Ctrl+W"]},
                                          "platforms": {"linux": {"tab.close": []}}})
        rows, reserved = sheet.read_orca(path)
        self.assertEqual(rows[0]["status"], "Unbound")
        self.assertFalse(reserved)

    def test_indexed_actions_expand_display_and_reserved_range(self):
        path = self.document("orca.json", {"keybindings": {"tab.selectByIndex": ["Ctrl+Alt+1"],
                                                           "tab.newAgent.codex": ["Ctrl+Shift+2"]}})
        rows, reserved = sheet.read_orca(path)
        self.assertEqual(rows[0]["sequence"][-1][-1], "1–9")
        self.assertEqual(rows[1]["sequence"][-1][-1], "2")
        self.assertIn("Ctrl+Alt+9", reserved)

    def test_duplicate_bindings_are_deduplicated(self):
        path = self.document("orca.json", {"keybindings": {"tab.close": ["Ctrl+W", "control+w"]}})
        self.assertEqual(len(sheet.read_orca(path)[0]), 1)

    def test_invalid_orca_sections_and_binding_types_fail(self):
        for document in [{"keybindings": []}, {"platforms": {"linux": []}},
                         {"keybindings": {"tab.close": "Ctrl+W"}}, {"version": 2}]:
            with self.subTest(document=document), self.assertRaises(ValueError):
                sheet.read_orca(self.document("orca.json", document))

    def test_opencode_alternatives_leader_and_shadowed_keys(self):
        path = self.document("cli.json", {"keybinds": {
            "leader": "ctrl+space", "model.list": ["<leader>m", "alt+m"],
            "session.page.up": {"key": "ctrl+alt+b,alt+pageup"},
            "variant.cycle": False,
        }, "secret": "MUST_NOT_BE_EMBEDDED"})
        rows = sheet.read_opencode(path, {"Ctrl+Alt+B": "Toggle sidebar"})
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["sequence"], [["Ctrl", "Space"], ["M"]])
        self.assertEqual(rows[2]["status"], "Shadowed in Orca")
        self.assertNotIn("MUST_NOT_BE_EMBEDDED", sheet.render_page(rows))

    def test_claude_contexts_and_later_unbinding(self):
        path = self.document("claude.json", {"bindings": [
            {"context": "Chat", "bindings": {"alt+m": "chat:modelPicker", "alt+e": "command:effort"}},
            {"context": "Chat", "bindings": {"alt+m": None}},
            {"context": "Scroll", "bindings": {"alt+pageup": "scroll:fullPageUp"}},
        ]})
        rows = sheet.read_claude(path, {})
        self.assertEqual(len(rows), 2)
        self.assertIn("fullscreen", rows[1]["note"])

    def test_launcher_reads_actual_binding(self):
        path = self.root / "user.lua"
        path.write_text('hl.bind("SUPER + ALT + SHIFT + K", action, { description = "Open the searchable Orca keybind guide" })')
        rows = sheet.read_launcher(path)
        self.assertEqual(rows[0]["sequence"], [["Super", "Alt", "Shift", "K"]])

    def test_embedded_script_cannot_be_closed_by_configuration(self):
        payload = '</script><img src=x onerror="alert(1)">'
        page = sheet.render_page([sheet.row("General", payload, "Ctrl+A")])
        self.assertNotIn(payload, page)
        self.assertIn(r"\u003c/script>", page)
        self.assertEqual(page.count("</script>"), 1)

    def test_optional_missing_harness_files_are_allowed(self):
        missing = self.root / "missing.json"
        self.assertEqual(sheet.read_opencode(missing, {}), [])
        self.assertEqual(sheet.read_claude(missing, {}), [])
        with self.assertRaises(ValueError):
            sheet.read_orca(missing)

    def test_invalid_input_preserves_old_html_and_fails_visibly(self):
        config = self.root / "broken.json"
        config.write_text("{not json}")
        output = self.root / "guide.html"
        output.write_text("original guide")
        result = subprocess.run([sys.executable, str(Path(sheet.__file__)), str(config), "-o", str(output)],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Could not read", result.stderr)
        self.assertEqual(output.read_text(), "original guide")

    def test_atomic_write_failure_preserves_previous_output(self):
        output = self.root / "guide.html"
        output.write_text("original")
        with patch.object(sheet.os, "replace", side_effect=OSError("replacement failed")):
            with self.assertRaises(OSError):
                sheet.write_page(output, "new")
        self.assertEqual(output.read_text(), "original")
        self.assertEqual(list(self.root.glob(".keybinds-*")), [])

    def test_build_rows_and_successful_write(self):
        config = self.document("orca.json", {"keybindings": {"tab.newTerminal": ["Ctrl+Shift+T"]}})
        missing = self.root / "missing"
        rows = sheet.build_rows(config, missing, missing, missing)
        self.assertTrue(any(item["category"] == "Limitations" for item in rows))
        output = self.root / "guide.html"
        sheet.write_page(output, sheet.render_page(rows))
        self.assertIn("Orca · Keybind Atlas", output.read_text())
        self.assertNotIn("__DATA__", output.read_text())

    def test_regeneration_reflects_config_changes(self):
        path = self.document("orca.json", {"keybindings": {"tab.newTerminal": ["Ctrl+Shift+T"]}})
        original = sheet.render_page(sheet.read_orca(path)[0])
        path.write_text(json.dumps({"keybindings": {"tab.newTerminal": ["Ctrl+Alt+T"]}}))
        regenerated = sheet.render_page(sheet.read_orca(path)[0])
        self.assertNotEqual(original, regenerated)
        self.assertIn('"trigger": "Ctrl+Alt+T"', regenerated)
        self.assertNotIn('"trigger": "Ctrl+Shift+T"', regenerated)

    def test_malformed_harness_config_does_not_replace_guide(self):
        config = self.document("orca.json", {"keybindings": {}})
        harness = self.root / "cli.json"
        harness.write_text("{broken}")
        output = self.root / "guide.html"
        output.write_text("original guide")
        result = subprocess.run([sys.executable, str(Path(sheet.__file__)), str(config),
                                 "--opencode-config", str(harness), "-o", str(output)],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(output.read_text(), "original guide")


if __name__ == "__main__":
    unittest.main()
