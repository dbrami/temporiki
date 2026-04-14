from __future__ import annotations

from temporiki_tools.obsidian_pack import install_ux_pack


def test_install_ux_pack_creates_dashboards_and_templates(tmp_path):
    install_ux_pack(tmp_path)

    assert (tmp_path / "wiki" / "meta" / "dashboard.md").exists()
    assert (tmp_path / "wiki" / "meta" / "decision-timeline.md").exists()
    assert (tmp_path / "wiki" / "_templates" / "decision.md").exists()
    assert (tmp_path / "wiki" / "_templates" / "concept.md").exists()
