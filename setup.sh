#!/usr/bin/env bash

set -e
cd "$(dirname "$0")"

if ! command -v uv > /dev/null ; then
    echo "Please install uv: "
    exit 1
fi

echo "Installing pre-commit hooks..."
if command -v prek > /dev/null ; then
    prek install
elif command -v pre-commit > /dev/null ; then
    pre-commit install
else
    uvx pre-commit install
fi

echo "Creating python virtual environment..."
uv sync

echo "Installing Playwright with Chromium..."
uv run playwright install --with-deps --no-shell chromium
