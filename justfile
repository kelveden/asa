export VERSION := `cat pyproject.toml | grep -E 'version = .+' | sed -r 's/version = \"(.+)\"/\1/'`

init:
    uv sync

build:
    uv build

run +args:
    uv run python -m asa {{args}}

install: build
    uv tool install "dist/asa-${VERSION}-py3-none-any.whl" --force
