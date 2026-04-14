from __future__ import annotations

import json
from pathlib import Path

from temporiki_tools.obsidian_pack import install_ux_pack


def _upsert_obsidian_files_and_links_defaults(root: Path) -> dict[str, object]:
    app_json = root / ".obsidian" / "app.json"
    app_json.parent.mkdir(parents=True, exist_ok=True)

    current: dict[str, object] = {}
    if app_json.exists():
        try:
            loaded = json.loads(app_json.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                current = loaded
        except Exception:
            current = {}

    # Ensure clipped assets and downloaded attachments land in raw/webclips.
    current["attachmentFolderPath"] = "raw/webclips"
    app_json.write_text(json.dumps(current, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return current


def run_onboarding(root: Path) -> dict[str, object]:
    root = root.resolve()
    dirs = [
        root / "raw" / "webclips",
        root / "raw" / "assets",
        root / "wiki" / "queries",
        root / "wiki" / "meta",
        root / "wiki" / "_templates",
        root / ".memplite",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    for keep in [root / "raw" / "webclips" / ".gitkeep", root / "raw" / "assets" / ".gitkeep"]:
        if not keep.exists():
            keep.write_text("\n", encoding="utf-8")

    created = install_ux_pack(root)
    obsidian_app = _upsert_obsidian_files_and_links_defaults(root)
    checklist = [
        "Open Obsidian and select this repo folder as vault",
        "Enable Obsidian Terminal and Web Clipper plugins",
        "Web Clipper target: raw/webclips/",
        "Start your LLM CLI in repo terminal (claude/codex/gemini)",
        "Run ./.temporiki/hooks/session-start.sh once per shell session",
    ]
    return {
        "root": str(root),
        "created": created,
        "obsidian_attachment_folder_path": str(obsidian_app.get("attachmentFolderPath", "")),
        "checklist": checklist,
    }
