#!/usr/bin/env sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHONPATH="$ROOT/src" python3 -m qingyuan_os demo --output "$ROOT/outputs/demo"
