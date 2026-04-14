.PHONY: sync sync-mempalace sync-chroma-client test ingest lint lint-autofix watch palace-init palace-mine palace-search palace-kg-query palace-health session-launch palace-auto session-start session-stop obsidian-ux-pack

sync:
	uv sync --extra dev

sync-mempalace:
	uv sync --extra dev --extra mempalace

sync-chroma-client:
	uv sync --extra dev --extra chroma-client

test:
	uv run pytest

ingest:
	uv run memoriki ingest

lint:
	uv run memoriki lint

lint-autofix:
	uv run memoriki lint --autofix

watch:
	uv run memoriki watch --interval-seconds 5

palace-init:
	uv run memoriki palace-init

palace-mine:
	uv run memoriki palace-mine

palace-search:
	uv run memoriki palace-search "$(Q)"

palace-kg-query:
	uv run memoriki palace-kg-query --as-of "$(AS_OF)"

palace-health:
	uv run memoriki palace-health

session-launch:
	./hooks/session-launch.sh

palace-auto:
	uv run memoriki palace-auto

session-start:
	./hooks/session-start.sh

session-stop:
	./hooks/session-stop.sh

obsidian-ux-pack:
	uv run memoriki obsidian-ux-pack
