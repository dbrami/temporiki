from __future__ import annotations

import json

from temporiki_tools.onboarding import run_onboarding


def test_onboarding_sets_expected_structure(tmp_path):
    out = run_onboarding(tmp_path)

    assert (tmp_path / "raw" / "webclips").exists()
    assert (tmp_path / "raw" / "assets").exists()
    assert (tmp_path / "raw" / "webclips" / ".gitkeep").exists()
    assert (tmp_path / "raw" / "assets" / ".gitkeep").exists()
    assert (tmp_path / "wiki" / "meta" / "dashboard.md").exists()
    assert (tmp_path / "wiki" / "_templates" / "decision.md").exists()
    app = json.loads((tmp_path / ".obsidian" / "app.json").read_text(encoding="utf-8"))
    assert app["attachmentFolderPath"] == "raw/webclips"
    assert out["obsidian_attachment_folder_path"] == "raw/webclips"
    assert isinstance(out["checklist"], list)
    assert len(out["checklist"]) >= 5
