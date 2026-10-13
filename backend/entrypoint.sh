#!/bin/sh
set -eu

alembic upgrade head
if [ "${DEMO_SEED:-0}" = "1" ]; then
  python -m app.seed
fi
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
