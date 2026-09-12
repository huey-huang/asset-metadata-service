#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
python3 -m py_compile src/*.py
python3 -m json.tool schemas/metadata-result.schema.json >/dev/null
echo "Metadata runtime validation passed."
