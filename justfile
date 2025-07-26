export VERSION := `cat pyproject.toml | grep -E 'version = .+' | sed -r 's/version = \"(.+)\"/\1/'`

init:
    uv run pre-commit install
    uv sync

check:
    uv run ruff check
    uv run mypy .

build: check
    uv build

install: build
    uv tool install "dist/asa-${VERSION}-py3-none-any.whl" --force

run +args:
    uv run python -m asa {{args}}
