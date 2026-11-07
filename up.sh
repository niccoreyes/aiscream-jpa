#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# .env is a trusted local shell file. Do not source files from strangers.
if [[ -f .env ]]; then set -a; source .env; set +a; fi
export FHIR_PUBLIC_URL="${FHIR_PUBLIC_URL:-http://localhost:8080/fhir}"
COMPOSE=(docker compose -f docker-compose.yml)

if [[ "${LOCAL_HTTPS:-false}" == true ]]; then
  # Local HTTPS currently supports macOS + Docker Desktop.
  [[ "$(uname)" == Darwin ]] || { echo "Local HTTPS requires macOS + Docker Desktop."; exit 1; }
  command -v caddy >/dev/null
  command -v keytool >/dev/null
  command -v python3 >/dev/null
  export FHIR_HOST
  FHIR_HOST=$(python3 -c 'import os,re,urllib.parse; u=urllib.parse.urlsplit(os.environ["FHIR_PUBLIC_URL"]); assert u.scheme=="https" and u.port in (None,443) and u.path=="/fhir" and not u.query and not u.fragment and not u.username; assert re.fullmatch(r"[A-Za-z0-9.-]+",u.hostname or ""); print(u.hostname)')
  mkdir -p .local-https
  # Optional: reuse an already trusted local Caddy CA instead of creating one.
  CADDY_STORAGE="${CADDY_STORAGE:-$ROOT/.local-https/caddy}"
  if [[ -f .local-https/hostname && "$(cat .local-https/hostname)" != "$FHIR_HOST" ]]; then
    echo "Run ./down.sh before changing the local HTTPS hostname."; exit 1
  fi
  printf '%s\n' "$FHIR_HOST" > .local-https/hostname

  # A private Caddy config avoids changing another site's configuration.
  # skip_install_trust leaves the macOS trust store untouched.
  cat > .local-https/Caddyfile <<EOF
{
    admin localhost:2020
    auto_https disable_redirects
    skip_install_trust
    storage file_system {
        root "$CADDY_STORAGE"
    }
}
$FHIR_HOST {
    bind 127.0.0.1
    tls internal
    reverse_proxy 127.0.0.1:8080
}
EOF
  if curl --max-time 3 -fsS http://localhost:2019/config/ > .local-https/running.json; then
    # Reuse only the simple proxy for this hostname. Save its original config.
    python3 - "$FHIR_HOST" <<'PY'
import json,sys
c=json.load(open('.local-https/running.json'))
s=list(c['apps']['http']['servers'].values())
assert len(s)==1 and len(s[0]['routes'])==1, 'Existing Caddy has other sites; manage it separately.'
assert s[0]['routes'][0]['match']==[{'host':[sys.argv[1]]}], 'Existing Caddy hostname differs.'
PY
    if [[ ! -f .local-https/original-caddy.json ]]; then
      cp .local-https/running.json .local-https/original-caddy.json
    fi
    # The running instance retains its existing CA and storage.
    cat > .local-https/Caddyfile <<EOF
{
    auto_https disable_redirects
    skip_install_trust
}
$FHIR_HOST {
    bind 127.0.0.1
    tls internal
    reverse_proxy 127.0.0.1:8080
}
EOF
    curl --max-time 10 -fsS -H 'Content-Type: text/caddyfile' --data-binary @.local-https/Caddyfile http://localhost:2019/load
    curl --max-time 5 -fsS http://localhost:2019/pki/ca/local | python3 -c 'import json,sys; print(json.load(sys.stdin)["root_certificate"])' > .local-https/root.crt
  elif [[ ! -f .local-https/caddy.pid ]] || ! sudo kill -0 "$(cat .local-https/caddy.pid)" 2>/dev/null; then
    # Fail before touching hosts if someone already owns HTTPS port 443.
    if lsof -nP -iTCP:443 -sTCP:LISTEN >/dev/null 2>&1; then
      echo "Port 443 is in use. Stop your existing local Caddy before running up.sh."; exit 1
    fi
    sudo caddy start --config "$ROOT/.local-https/Caddyfile" --pidfile "$ROOT/.local-https/caddy.pid"
    sudo chmod 644 .local-https/caddy.pid
  fi
  if [[ -f .local-https/caddy.pid ]]; then
    sudo cat "$CADDY_STORAGE/pki/authorities/local/root.crt" > .local-https/root.crt
  fi

  # Copy the running image's CA bundle, preserving trust for remote services.
  docker compose run -T --rm --no-deps --entrypoint java fhir -XshowSettings:properties -version 2> .local-https/java.txt
  JAVA_HOME_IN_IMAGE=$(sed -n 's/^ *java.home = //p' .local-https/java.txt)
  HAPI_IMAGE=$(docker compose config --format json | python3 -c 'import json,sys; print(json.load(sys.stdin)["services"]["fhir"]["image"])')
  TEMP_CONTAINER=$(docker create "$HAPI_IMAGE")
  # -L follows the image's cacerts symlink instead of copying a broken link.
  rm -f .local-https/cacerts
  docker cp -L "$TEMP_CONTAINER:$JAVA_HOME_IN_IMAGE/lib/security/cacerts" .local-https/cacerts
  docker rm "$TEMP_CONTAINER" >/dev/null
  chmod u+w .local-https/cacerts
  keytool -importcert -noprompt -alias aiscream-caddy -file .local-https/root.crt -keystore .local-https/cacerts -storepass changeit
  chmod 644 .local-https/cacerts

  # Add only a tagged entry; down.sh removes exactly this line.
  if ! python3 -c 'import sys; h=sys.argv[1]; sys.exit(0 if any(h in l.split("#")[0].split()[1:] for l in open("/etc/hosts")) else 1)' "$FHIR_HOST"; then
    printf '127.0.0.1 %s # aiscream-jpa-local-https\n' "$FHIR_HOST" > .local-https/hosts-entry
    cat .local-https/hosts-entry | sudo tee -a /etc/hosts >/dev/null
  fi
  COMPOSE+=(-f compose.caddy.yaml)
  echo "Browser trust is optional: import .local-https/root.crt into Keychain if needed."
elif [[ -f .local-https/hostname ]]; then
  echo "Run ./down.sh to clean up the previous local HTTPS setup first."; exit 1
fi

# Remove the prior one-shot builder container so Compose must rebuild the
# classes before starting HAPI. The service dependency enforces that ordering.
"${COMPOSE[@]}" rm --stop --force interceptor >/dev/null 2>&1 || true
"${COMPOSE[@]}" up -d --wait --force-recreate fhir

# Compose's running state does not mean HAPI has finished loading its packages.
echo "Waiting for HAPI metadata..."
for attempt in {1..150}; do
  if curl -fsS --max-time 5 http://localhost:8080/fhir/metadata >/dev/null 2>&1; then
    if [[ "${LOCAL_HTTPS:-false}" == true ]]; then
      curl --cacert .local-https/root.crt -fsS --max-time 30 "${FHIR_PUBLIC_URL%/fhir}/" > .local-https/home.html
      if grep -q 'Failed to load conformance statement' .local-https/home.html; then
        echo "The homepage loaded but its tester could not reach metadata. Check .local-https/home.html"; exit 1
      fi
    fi
    echo "Ready: $FHIR_PUBLIC_URL"
    exit 0
  fi
  sleep 2
done
echo "HAPI did not become ready. Check: docker compose logs --tail=100 fhir"
exit 1
