#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$ROOT_DIR/environment.yml"
ENV_NAME="mailling"

if ! command -v conda >/dev/null 2>&1; then
  echo "conda not found. Install Miniconda/Anaconda first."
  exit 1
fi

if conda env list | awk '{print $1}' | grep -q "^${ENV_NAME}$"; then
  conda env update -f "$ENV_FILE" --prune
else
  conda env create -f "$ENV_FILE"
fi

# Install Chromium (best effort; Selenium can auto-manage drivers)
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y chromium chromium-driver \
    || sudo apt-get install -y chromium-browser chromium-chromedriver \
    || true
elif command -v dnf >/dev/null 2>&1; then
  sudo dnf install -y chromium || true
elif command -v yum >/dev/null 2>&1; then
  sudo yum install -y chromium || true
elif command -v brew >/dev/null 2>&1; then
  brew install --cask chromium || true
else
  echo "No supported package manager found. Install Chromium manually."
fi

echo "Done. Activate with: conda activate ${ENV_NAME}"
