#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# Remove the prior one-shot builder container so Compose must rebuild the
# classes before starting HAPI. The service dependency enforces that ordering.
docker compose rm --stop --force interceptor >/dev/null 2>&1 || true
docker compose up -d --wait --force-recreate fhir
