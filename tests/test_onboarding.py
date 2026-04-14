from __future__ import annotations

from temporiki_tools.onboarding import run_onboarding


def test_onboarding_sets_expected_structure(tmp_path):
    out = run_onboarding(tmp_path)

    assert (tmp_path / "raw" / "webclips").exists()
    assert (tmp_path / "raw" / "assets").exists()
    assert (tmp_path / "raw" / "webclips" / ".gitkeep").exists()
    assert (tmp_path / "raw" / "assets" / ".gitkeep").exists()
    assert (tmp_path / "wiki" / "meta" / "dashboard.md").exists()
    assert (tmp_path / "wiki" / "_templates" / "decision.md").exists()
    assert isinstance(out["checklist"], list)
    assert len(out["checklist"]) >= 5

