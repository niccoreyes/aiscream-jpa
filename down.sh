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

# Undo only system changes recorded by up.sh, even if .env has since changed.
if [[ -f .local-https/original-caddy.json ]]; then
  curl --max-time 10 -fsS -H 'Content-Type: application/json' --data-binary @.local-https/original-caddy.json http://localhost:2019/load
  rm .local-https/original-caddy.json
fi
if [[ -f .local-https/caddy.pid ]]; then
  CADDY_PID=$(cat .local-https/caddy.pid)
  if ps -p "$CADDY_PID" -o command= | grep -F "$ROOT/.local-https/Caddyfile" >/dev/null; then
    curl --max-time 10 -fsS -X POST http://localhost:2020/stop
  fi
fi
if [[ -f .local-https/hosts-entry ]]; then
  sudo python3 - "$ROOT/.local-https/hosts-entry" <<'PY'
import sys
from pathlib import Path
entry = Path(sys.argv[1]).read_text()
hosts = Path('/etc/hosts')
with hosts.open('r+') as f:
    lines = f.readlines()
    f.seek(0)
    f.writelines(line for line in lines if line != entry)
    f.truncate()
PY
  rm .local-https/hosts-entry
fi
# Keep CA material so optional browser trust remains valid on the next startup.
rm -f .local-https/hostname .local-https/caddy.pid

if confirm_with_timeout "Delete generated Maven outputs (hapi-extra-classes/ext and target)?"; then
  rm -rf hapi-extra-classes/ext hapi-extra-classes/target
  echo "Removed generated interceptor classes and Maven build output."
else
  echo "Kept generated Maven outputs."
fi

echo "Kept PostgreSQL data."
