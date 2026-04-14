# Contributing to Temporiki

Thanks for your interest in Temporiki. Contributions are welcome across code, docs, and ideas.

## Where to start

- **Ideas, questions, use cases** → [GitHub Discussions](https://github.com/dbrami/temporiki/discussions)
- **Bugs, regressions, broken behavior** → [GitHub Issues](https://github.com/dbrami/temporiki/issues)
- **Pull requests** → fork, branch, PR against `main`

## Pull request guidelines

- Keep changes focused — one concern per PR
- Follow the versioning rules in the README (SemVer + CHANGELOG update for impactful changes)
- Run `uv run temporiki lint --autofix` before submitting if you touched wiki content
- Run `uv run python -m pytest -q` if you touched `temporiki_tools/`
- Reference the Discussion or Issue your PR addresses (e.g., `Closes #12`)

## Code of conduct

Be kind. Assume good intent. Critique ideas, not people.

## License

By contributing, you agree that your contributions will be licensed under the MIT License (see `LICENSE`).
