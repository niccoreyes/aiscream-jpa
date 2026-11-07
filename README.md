# PH Core HAPI FHIR JPA server

A Docker Compose deployment of HAPI FHIR JPA with PostgreSQL, configured to
install PH Core 0.2.1 and validate resources using its profiles. This repository
contains the server configuration and a small custom repository-validation
factory; it does not contain a separate HAPI server distribution.

## Prerequisites

- Docker Engine or Docker Desktop with the Docker Compose plugin, running and
  able to pull images.
- A free local port 8080 and sufficient disk space for images, Maven dependencies,
  PostgreSQL data and implementation guide packages.
- Internet access for image and Maven downloads, FHIR packages and remote
  terminology services. The first startup can take several minutes.
- `curl` and Python 3 for the examples below.

## Start and check the server

From the repository directory:

```bash
./up.sh
docker compose ps
curl -fsS http://localhost:8080/fhir/metadata | python3 -m json.tool
```

Use **http://localhost:8080/fhir** to access the server locally. The
CapabilityStatement base URL is configured with `hapi.fhir.server_address`;
the homepage's **FHIR Base** link is configured separately with
`hapi.fhir.tester.home.server_address`. To follow startup or investigate a failure:

```bash
docker compose logs -f fhir
docker compose logs interceptor
docker compose logs db
```

`up.sh` removes the previous one-shot builder container, builds the custom
interceptor, and force-recreates HAPI after the build succeeds. It waits for
Compose readiness; check the logs as well for package installation or validation
problems. The PostgreSQL data directory is retained. Run `./up.sh` after Java
changes: a plain `docker compose up` can reuse an already completed builder.

## How the deployment fits together

| Service | Purpose |
| --- | --- |
| `interceptor` | Uses Maven and Java 21 in a temporary build container to compile the custom factory. |
| `db` | PostgreSQL `17.2-bookworm`, with data bind-mounted at `./hapi.postgress.data`. |
| `fhir` | `hapiproject/hapi:latest`, serving FHIR on port 8080 after the database is healthy and the build succeeds. |

The build removes stale `hapi-extra-classes/ext/`, compiles against the HAPI
8.12.0 dependencies in the POM, writes the class under `ext/`, and removes
temporary Maven `target/` output on exit. The folder is mounted at
`/app/extra-classes` for HAPI to load. Maven dependencies are retained in the
Compose named volume `maven-cache` and reused across builds. The first build
still needs network access to download dependencies.

The HAPI image uses the mutable `latest` tag, while the custom code compiles
against a fixed HAPI version. A future image can therefore introduce
incompatibilities or change defaults. For reproducible deployments, select and
test a specific compatible image tag and review the POM alongside upgrades.

## PH Core packages

At startup, `application.yaml` configures these packages in dependency-first
order with `STORE_AND_INSTALL`, `reloadExisting: false`, and
`fetchDependencies: false`:

| Package | Version | Source |
| --- | --- | --- |
| `hl7.terminology.r4` | 7.5.0 | HAPI's package resolution |
| `hl7.fhir.uv.extensions.r4` | 5.3.0 | HAPI's package resolution |
| `fhir.ph.core` | 0.2.1 | [PH Core package](https://fhir.doh.gov.ph/phcore/0.2.1/package.tgz) |

R4 core definitions are supplied by the server. Dependencies are explicitly
pinned to avoid an incompatible transitive extensions version. Review package
compatibility and ordering when changing versions. Since `reloadExisting` is
false, changing a package's contents without changing its version should not be
assumed to reload it into an existing database.

For example, inspect stored StructureDefinitions with:

```bash
curl -fsS 'http://localhost:8080/fhir/StructureDefinition?_count=20' | python3 -m json.tool
```

## Validation

Two mechanisms are configured:

- **Request validation** is enabled for incoming writes. It checks declared
  profiles and rejects validation errors; response validation is disabled.
- **Repository validation** uses the custom factory in
  `hapi-extra-classes/src/main/java/ext/`. At startup it searches stored resource
  StructureDefinitions whose canonical URLs begin with the PH Core profile
  prefix, groups them by resource type, and identifies the root profile for
  each type. It applies that profile as an implied baseline when `meta.profile`
  is empty or absent. If any profile is declared, this implied rule is skipped;
  request validation checks declared profiles. Types with no matching stored
  profile receive no rule from this factory.

The factory expects exactly one root PH Core profile per discovered resource
type; it fails startup if it finds more or fewer. Rules are constructed at
startup, so restart HAPI after changing the stored profiles. Check logs and
the installed definitions if expected rules are missing. The starter's own
repository-validation factory switch remains commented out; the custom
`@Primary` bean is discovered through `custom-bean-packages: ext`.

You can also submit a resource for explicit validation without storing it:

```bash
curl -sS -X POST 'http://localhost:8080/fhir/Patient/$validate' \
  -H 'Content-Type: application/fhir+json' \
  --data-binary @patient.json | python3 -m json.tool
```

Create `patient.json` with the resource you want to check. Inspect the returned
FHIR OperationOutcome and HTTP status; successful validation depends on the
resource, installed profiles and terminology availability. Use synthetic data
for local experiments.

### PH Core test bundles

The [PH Core test bundles repository](https://github.com/niccoreyes/ph-core-testbundles/tree/phcore-0.2.1)
provides transaction Bundle fixtures for selected PH Core 0.2.1 constraints,
including expected-valid and expected-invalid cases. Its README explains how to
run the Python harness against this server and interpret write acceptance and
`$validate` results separately. These are focused examples, not a complete
conformance suite; results depend on the server configuration and terminology.
The harness creates and deletes resources, overwrites its local results file,
and performs best-effort cleanup, so use a disposable test environment.

This checkout does **not** include the historical identifier-deduplication or
automatic merge interceptor, PH eReferral package, custom HAPI image, or
response-validation setup described in older commits. Do not rely on automatic
deduplication when creating resources.

## Terminology and search

`application.yaml` maps LOINC, SNOMED CT and several Philippine and example
code systems to `https://tx.fhirlab.net/fhir`; UCUM is mapped to
`https://tx.fhir.org/r4`. These mappings configure routing, not a guarantee that
the remote service contains every code or is reachable. Validation and expansion
results can depend on those services. Check their availability and content when
investigating terminology errors.

ValueSet pre-expansion and its background task are disabled, so expansion is
performed on demand. Extended Hibernate Search/Lucene configuration and its
persistent volume are commented out; do not assume full-text or advanced search
is enabled. Most other commented settings are examples, not assertions about
the running image's defaults. See the [HAPI terminology documentation](https://hapifhir.io/hapi-fhir/docs/server_jpa/terminology.html)
and [search documentation](https://hapifhir.io/hapi-fhir/docs/server_jpa/elastic.html).

## Configuration and operations

- Edit `application.yaml` for HAPI settings and package or terminology mappings.
  It is mounted as `/app/config/application.yaml`. Avoid duplicate YAML mappings;
  many examples are already present as comments.
- Edit `docker-compose.yml` for images, ports, mounts and database settings.
  The database username and password are currently `admin` in both Compose and
  the datasource configuration. Change both consistently for any non-local
  deployment and use an appropriate secrets mechanism.
- Review the [upstream starter configuration](https://raw.githubusercontent.com/hapifhir/hapi-fhir-jpaserver-starter/refs/heads/master/src/main/resources/application.yaml)
  and the documentation matching your deployed image before changing settings;
  upstream master can differ from the running image.
- Apply configuration changes with `./up.sh`. To start without rebuilding the
  interceptor, use `docker compose up -d --wait fhir` only when the existing
  compiled class is current.
- Stop and remove the Compose containers and network while retaining database
  data with `docker compose down`. A normal restart is `docker compose down`
  followed by `./up.sh`. This retains the Maven cache; `docker compose down -v`
  removes the named cache volume and the next build must download dependencies again.
- `./down.sh` also stops the stack, then separately prompts whether to delete
  generated Java output and the PostgreSQL directory. Each prompt defaults to
  no after two seconds. Confirming deletion of the database is permanent.

Back up the PostgreSQL data using a PostgreSQL-consistent backup procedure before
upgrades or destructive maintenance. Removing containers alone does not remove
the bind-mounted database directory. Avoid deleting that directory unless a clean
slate is explicitly intended.

The Compose configuration exposes port 8080 and uses example database
credentials; it does not establish a production security boundary. Configure
authentication, access controls, transport security, backups and appropriate
network exposure before using real patient data.

## Troubleshooting

- **Port already allocated:** stop the conflicting service or change the host
  side of the `8080:8080` mapping and use the new port in client URLs.
- **Build fails:** inspect `docker compose logs interceptor`, Docker networking
  and Maven dependency access. HAPI should not be recreated until compilation
  succeeds. Check the HAPI image and POM versions for compatibility.
- **Database does not become healthy:** inspect `docker compose logs db`, disk
  space, bind-mount permissions and matching datasource credentials. Preserve
  existing data while diagnosing.
- **HAPI fails or package/profile rules are unexpected:** inspect
  `docker compose logs fhir`, package download access, stored definitions, and
  the factory's one-root-per-resource-type requirement.
- **Terminology validation fails:** inspect the OperationOutcome and test the
  configured terminology endpoint and relevant CodeSystem. A reachable server
  may still lack the requested content.

Useful references: [HAPI JPA configuration](https://hapifhir.io/hapi-fhir/docs/server_jpa/configuration.html),
[validation support](https://hapifhir.io/hapi-fhir/docs/validation/validation_support_modules.html),
and [package installation](https://hapifhir.io/hapi-fhir/docs/server_jpa/packages.html).

## Reproducible local HTTPS on macOS

Read the [visual architecture and setup guide](https://niccoreyes.github.io/aiscream-jpa/)
for startup and shutdown diagrams, configuration, and troubleshooting.
The guide lives in `docs/` and GitHub Pages publishes it from `main`.

Copy `.env.example` to `.env`, edit `FHIR_PUBLIC_URL` and `FHIR_TESTER_NAME`,
then run `./up.sh`. Set `LOCAL_HTTPS=false` for ordinary HTTP or a separately
managed proxy. The same URL is used for the API and the homepage tester.
Docker Desktop, Caddy, Python 3 and Java `keytool` must already be installed.
The `.env` file is sourced by Bash: use shell-compatible assignments and trust
its contents as you would a script.

`up.sh` prepares Java's CA truststore, maps the hostname to Docker's host gateway,
and adds a marked `/etc/hosts` entry only when none exists. It can reuse an
existing single-site Caddy for the same hostname, saving its original config;
otherwise it starts its own Caddy instance. A different Caddy configuration is
rejected rather than overwritten. New instances may request `sudo` for port 443.
Generated state and CA material stay in the ignored `.local-https/` directory.
The truststore retains the HAPI image's existing CAs for remote terminology calls.
If you already trusted Caddy's CA, set `CADDY_STORAGE` in `.env` to its existing
data folder (see `.env.example`) to reuse it without changing Keychain trust.

`./down.sh` stops the stack, restores the saved Caddy configuration or stops the
Caddy instance it started, and removes only its marked hosts entry. Existing
hosts entries and PostgreSQL data are preserved. It does not modify macOS
certificate trust. If you change the hostname, run `down.sh` first.

For a newly created CA, browser trust is a manual one-time step: import
`.local-https/root.crt` into Keychain Access and trust it for SSL. The script
retains CA material across shutdowns so that trust remains valid next time.
If you later remove browser trust, remove that exact certificate in Keychain
Access. Never distribute the generated CA private key.

Both existing and newly started Caddy instances use a loopback listener.
This workflow is for synthetic demo data on macOS with Docker Desktop.

### Manual setup reference

The instructions below describe the original manual setup. Prefer `up.sh` and
`down.sh` above; manual setup alone does not configure the tester's JVM trust.

To record a browser demo using the URL `https://phcore.thomasreyes.ph/fhir/...`
while HAPI continues to run at `http://localhost:8080/fhir`, use Caddy as a
temporary local TLS reverse proxy. This does not change public DNS or configure
TLS in HAPI. Only this Mac will use the local proxy while the `/etc/hosts`
override is present. The Mac must trust Caddy's local CA for the browser to show
a trusted HTTPS connection.

### Install Caddy (if needed)

```bash
brew install caddy
```

### Temporarily map the demo hostname to this Mac

Check `/etc/hosts` first to avoid adding a duplicate. If no mapping exists, add:

```bash
printf '\n127.0.0.1 phcore.thomasreyes.ph\n' | sudo tee -a /etc/hosts
```

While this entry exists, this Mac will reach the local proxy instead of the
public `phcore.thomasreyes.ph` site.

### Create a temporary Caddyfile

Save the following as `Caddyfile` in this repository (or another convenient
local folder):

```caddyfile
{
    auto_https disable_redirects
}

phcore.thomasreyes.ph {
    tls internal
    bind 127.0.0.1

    reverse_proxy 127.0.0.1:8080
}
```

This forwards all paths, including `/`, to HAPI and preserves the original
request path. The example assumes HAPI is available at `http://127.0.0.1:8080`,
with the FHIR API under `/fhir` as in the local server check above.

### Start and use the proxy

Start HAPI first, then run Caddy in a terminal from the folder containing the
`Caddyfile`:

```bash
sudo caddy run --config "$PWD/Caddyfile"
```

Caddy listens on HTTPS port 443. The first run may prompt for permission to
trust its local CA. If automatic trust does not succeed, leave Caddy running
and run this in another terminal:

```bash
sudo caddy trust
```

Open `https://phcore.thomasreyes.ph/fhir/metadata` in the browser. The TLS
connection is encrypted between the browser and local Caddy; Caddy forwards to
HAPI over loopback HTTP. No OAuth or browser insecure-content exception is
needed for this setup. The locally trusted certificate and hosts override are
for this Mac only; another computer will not inherit them.

### Undo the demo setup

While Caddy is still running, remove trust for its local CA:

```bash
sudo caddy untrust
```

Then stop Caddy with `Ctrl+C`. Remove only the demo mapping from `/etc/hosts`
by editing the file with administrator privileges and deleting this line:

```text
127.0.0.1 phcore.thomasreyes.ph
```

Remove the temporary `Caddyfile` if it is no longer needed. Caddy can remain
installed for future demos; if it was installed just for this, uninstall it
with `brew uninstall caddy`. `caddy untrust` removes trust from local trust
stores; Caddy's local CA files may remain in its data directory.

This is a local demo setup, not production transport security. Use synthetic
data and do not expose the local HAPI service or Caddy listener to a network.
