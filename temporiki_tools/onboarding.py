from __future__ import annotations

from pathlib import Path

from temporiki_tools.obsidian_pack import install_ux_pack


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
    checklist = [
        "Open Obsidian and select this repo folder as vault",
        "Enable Obsidian Terminal and Web Clipper plugins",
        "Set Web Clipper target to raw/webclips/",
        "Start your LLM CLI in repo terminal (claude/codex/gemini)",
        "Run ./hooks/session-start.sh once per shell session",
    ]
    return {
        "root": str(root),
        "created": created,
        "checklist": checklist,
    }

