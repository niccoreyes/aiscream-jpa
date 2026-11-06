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

The FHIR base URL is **http://localhost:8080/fhir**. The metadata response is
the server's CapabilityStatement. To follow startup or investigate a failure:

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
