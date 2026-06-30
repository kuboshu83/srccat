.PHONY: test run

test:
	@uv run pytest

test-run:
	@uv run srccat --language python