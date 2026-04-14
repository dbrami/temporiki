from __future__ import annotations

import json
import time
from pathlib import Path

import typer

from temporiki_tools.automation import run_cycle
from temporiki_tools.mempalace_chroma import is_chroma_available
from temporiki_tools.mempalace_lite import init_lite, kg_query_decisions
from temporiki_tools.mempalace_router import auto_mine, auto_search
from temporiki_tools.onboarding import run_onboarding
from temporiki_tools.obsidian_pack import install_ux_pack
from temporiki_tools.ops import ingest_delta, lint_wiki, save_query_result

app = typer.Typer(no_args_is_help=True)


def _top_confidence(results: list[dict[str, object]]) -> float:
    if not results:
        return 0.0
    return float(results[0].get("confidence", 0.0))


def _render_auto_answer(results: list[dict[str, object]], max_items: int = 3) -> str:
    lines: list[str] = []
    for i, r in enumerate(results[:max_items], start=1):
        text = str(r.get("text", "")).strip().replace("\n", " ")
        source = str(r.get("source_file", ""))
        confidence = float(r.get("confidence", 0.0))
        provenance = str(r.get("provenance", ""))
        if len(text) > 240:
            text = text[:237] + "..."
        lines.append(
            f"{i}. {text}\n   - source: {source}\n   - confidence: {confidence:.3f} ({provenance})"
        )
    return "\n".join(lines) if lines else "No results."


@app.command("ingest")
def ingest(root: Path = Path(".")) -> None:
    changed = ingest_delta(root)
    typer.echo(json.dumps(changed, indent=2))


@app.command("lint")
def lint(root: Path = Path("."), autofix: bool = False) -> None:
    report = lint_wiki(root, autofix=autofix)
    typer.echo(json.dumps(report, indent=2))


@app.command("query")
def query(
    question: str,
    answer: str = "",
    save: bool = True,
    root: Path = Path("."),
) -> None:
    if not save:
        typer.echo("Set --save to persist query results.")
        return
    out = save_query_result(root=root, question=question, answer=answer)
    typer.echo(str(out))


@app.command("watch")
def watch(root: Path = Path("."), interval_seconds: int = 5) -> None:
    typer.echo(f"Watching {root.resolve() / 'raw'} every {interval_seconds}s")
    while True:
        changed = ingest_delta(root)
        if changed:
            typer.echo(f"Detected {len(changed)} changed source(s)")
        time.sleep(interval_seconds)


@app.command("palace-auto")
def palace_auto(
    root: Path = Path("."),
    watch_interval_seconds: int = 15,
    lint_every_seconds: int = 300,
    health_every_seconds: int = 120,
    lint_autofix: bool = True,
    once: bool = False,
) -> None:
    """
    Automatic monitor loop:
    - watches raw/ deltas
    - re-indexes memory when changes are detected
    - runs periodic lint and health checks
    """
    root = root.resolve()
    typer.echo(
        f"Auto loop started at {root} (watch={watch_interval_seconds}s, "
        f"lint={lint_every_seconds}s, health={health_every_seconds}s)"
    )
    last_lint_at = 0.0
    last_health_at = 0.0

    while True:
        now = time.time()
        run_lint_now = (now - last_lint_at) >= max(1, lint_every_seconds)
        run_health_now = (now - last_health_at) >= max(1, health_every_seconds)

        report = run_cycle(
            root=root,
            run_lint=run_lint_now,
            run_health=run_health_now,
            lint_autofix=lint_autofix,
        )
        typer.echo(json.dumps(report, indent=2))

        if run_lint_now:
            last_lint_at = now
        if run_health_now:
            last_health_at = now

        if once:
            return
        time.sleep(max(1, watch_interval_seconds))


@app.command("palace-init")
def palace_init(root: Path = Path(".")) -> None:
    db = init_lite(root)
    typer.echo(str(db))


@app.command("palace-mine")
def palace_mine(root: Path = Path("."), wing: str = "raw", room: str = "general") -> None:
    out = auto_mine(root, wing=wing, room=room)
    typer.echo(json.dumps(out, indent=2))


@app.command("palace-search")
def palace_search(
    query: str,
    root: Path = Path("."),
    wing: str | None = None,
    room: str | None = None,
    n_results: int = 5,
    as_of: str | None = None,
    auto_save: bool = True,
    auto_save_min_confidence: float = 0.85,
) -> None:
    root = root.resolve()
    out = auto_search(
        root=root,
        query=query,
        wing=wing,
        room=room,
        n_results=n_results,
        as_of=as_of,
    )
    results = out.get("results", [])
    if isinstance(results, list) and auto_save and results:
        top_conf = _top_confidence(results)
        if top_conf >= max(0.0, min(1.0, auto_save_min_confidence)):
            answer = _render_auto_answer(results)
            tags = ["query", "auto", str(out.get("strategy", "unknown"))]
            saved = save_query_result(root=root, question=query, answer=answer, tags=tags)
            out["saved_query_path"] = saved.relative_to(root).as_posix()
            out["auto_saved"] = True
        else:
            out["auto_saved"] = False
            out["auto_save_reason"] = f"top_confidence={top_conf:.3f} below threshold={auto_save_min_confidence:.3f}"
    typer.echo(json.dumps(out, indent=2))


@app.command("palace-kg-query")
def palace_kg_query(
    root: Path = Path("."),
    topic: str | None = None,
    as_of: str | None = None,
) -> None:
    rows = kg_query_decisions(root=root, topic=topic, as_of=as_of)
    typer.echo(json.dumps(rows, indent=2))


@app.command("palace-health")
def palace_health() -> None:
    typer.echo(json.dumps({"chroma_available": is_chroma_available()}, indent=2))


@app.command("obsidian-ux-pack")
def obsidian_ux_pack(root: Path = Path(".")) -> None:
    created = install_ux_pack(root)
    typer.echo(json.dumps({"created": created}, indent=2))


@app.command("onboard")
def onboard(root: Path = Path(".")) -> None:
    out = run_onboarding(root)
    typer.echo(json.dumps(out, indent=2))
