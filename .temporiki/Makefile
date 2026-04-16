.PHONY: sync sync-mempalace sync-chroma-client test ingest lint lint-autofix watch palace-init palace-mine palace-search palace-kg-query palace-health palace-event session-launch palace-auto session-start session-stop obsidian-ux-pack obsidian-zero

sync:
	uv sync --project .temporiki --extra dev

sync-mempalace:
	uv sync --project .temporiki --extra dev --extra mempalace

sync-chroma-client:
	uv sync --project .temporiki --extra dev --extra chroma-client

test:
	uv --project .temporiki run python -m pytest -q

ingest:
	uv --project .temporiki run temporiki ingest

lint:
	uv --project .temporiki run temporiki lint

lint-autofix:
	uv --project .temporiki run temporiki lint --autofix

watch:
	uv --project .temporiki run temporiki watch --interval-seconds 5

palace-init:
	uv --project .temporiki run temporiki palace-init

palace-mine:
	uv --project .temporiki run temporiki palace-mine

palace-search:
	uv --project .temporiki run temporiki palace-search "$(Q)"

palace-kg-query:
	uv --project .temporiki run temporiki palace-kg-query --as-of "$(AS_OF)"

palace-health:
	uv --project .temporiki run temporiki palace-health

palace-event:
	uv --project .temporiki run temporiki palace-event

session-launch:
	./.temporiki/hooks/session-launch.sh

palace-auto:
	uv --project .temporiki run temporiki palace-auto

session-start:
	./.temporiki/hooks/session-start.sh

session-stop:
	./.temporiki/hooks/session-stop.sh

obsidian-ux-pack:
	uv --project .temporiki run temporiki obsidian-ux-pack

obsidian-zero:
	./.temporiki/hooks/obsidian-zero.sh
