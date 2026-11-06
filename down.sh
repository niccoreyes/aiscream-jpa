#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

confirm_with_timeout() {
  local prompt="$1"
  local answer=""
  if ! read -r -t 2 -p "$prompt [y/N] " answer; then
    printf '\n'
  fi
  [[ "$answer" =~ ^[Yy]$ ]]
}

# Stop and remove this Compose project's containers and network. The database is
# bind-mounted, so its host data remains unless explicitly deleted below.
docker compose down

if confirm_with_timeout "Delete generated Maven outputs (hapi-extra-classes/ext and target)?"; then
  rm -rf hapi-extra-classes/ext hapi-extra-classes/target
  echo "Removed generated interceptor classes and Maven build output."
else
  echo "Kept generated Maven outputs."
fi

if confirm_with_timeout "Permanently delete PostgreSQL data at hapi.postgress.data?"; then
  rm -rf hapi.postgress.data
  echo "Removed PostgreSQL data."
else
  echo "Kept PostgreSQL data."
fi
