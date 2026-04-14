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
	uv run temporiki ingest

lint:
	uv run temporiki lint

lint-autofix:
	uv run temporiki lint --autofix

watch:
	uv run temporiki watch --interval-seconds 5

palace-init:
	uv run temporiki palace-init

palace-mine:
	uv run temporiki palace-mine

palace-search:
	uv run temporiki palace-search "$(Q)"

palace-kg-query:
	uv run temporiki palace-kg-query --as-of "$(AS_OF)"

palace-health:
	uv run temporiki palace-health

session-launch:
	./hooks/session-launch.sh

palace-auto:
	uv run temporiki palace-auto

session-start:
	./hooks/session-start.sh

session-stop:
	./hooks/session-stop.sh

obsidian-ux-pack:
	uv run temporiki obsidian-ux-pack
