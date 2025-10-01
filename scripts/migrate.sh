#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ -f .env ]; then
  set -o allexport
  source .env
  set +o allexport
fi

exec poetry run alembic upgrade head


