# PH eReferral — HAPI FHIR JPA Server

A customized HAPI FHIR JPA server for the Philippine eReferral system, with
automatic IG profile validation and identifier-based deduplication.

## What this does

1. **Preloads PH Core and PH eReferral IGs** from `build.fhir.org` at startup.
2. **Auto-validates every resource** against all stored profiles — no `$validate`
   call needed.
3. **Detects and auto-merges duplicates** on POST by matching identifiers
   (PhilHealth ID, PhilSys ID, or any identifier).
4. **Terminology validation** is delegated to `https://tx.fhirlab.net/fhir`.
5. **Bundle transaction support** — POST `Bundle` of type `transaction` to
   create Patient + Observations in one call.

## Quick start

```bash
docker compose up -d
```

The server is at `http://localhost:8080/fhir`.

## Why a custom Docker image

The stock `hapiproject/hapi` image supports configuration-only changes
(Option A), but cannot run custom interceptors. For strict terminology
enforcement and identifier-based deduplication (Option B), we forked the
starter and built a custom image.

### What's different from upstream

| File | Change | Reason |
|---|---|---|
| `RepositoryValidationInterceptorFactoryR4.java` | `.rejectOnSeverity(WARNING)` + suppression methods | Unknown code systems (e.g. PSGC) now reject instead of warn |
| `StarterJpaConfig.java` | `registerCustomInterceptors()` moved before `RepositoryValidatingInterceptor` | Dedup must run before validation |
| `PhCoreDeduplicationInterceptor.java` | New interceptor | Auto-merges POSTs by identifier match; returns Bundle with merged resource + info OperationOutcome |

## Architecture

```
docker-compose.yml
├── fhir (custom image: niccoreyes/aiscream-hapi:latest)
│   ├── application.yaml (IGs, validation, dedup config)
│   └── PhCoreDeduplicationInterceptor (auto-merge)
└── db (postgres:17.2-bookworm)
```

## Validation flow

```
POST /Patient
  → SERVER_INCOMING_REQUEST_PRE_HANDLED   (dedup check)
     → if duplicate found: merge via DAO, throw DeduplicationMatchedException
  → STORAGE_PRESTORAGE_RESOURCE_CREATED   (RepositoryValidatingInterceptor)
     → enforce profile + rejectOnSeverity(WARNING)
  → Committed (or rejected with 422)

Exception path (when dedup fires):
  DeduplicationMatchedException (HTTP 200)
    → SERVER_OUTGOING_FAILURE_OPERATIONOUTCOME
       → Replace OperationOutcome with Bundle (merged resource + info OO)
    → Stream Bundle to client
```

**Note:** `hapi.fhir.validation.requests_enabled` is set to `false`. The
`RequestValidatingInterceptor` is an old-style `IServerInterceptor` that fires
at `SERVER_INCOMING_REQUEST_POST_PROCESSED`, which is **before** our
`PRE_HANDLED` hook. Keeping it disabled prevents the validator from rejecting
resources before dedup can merge them. The `RepositoryValidatingInterceptor`
at the `STORAGE` level still validates all resources on insert/update.

## Dedup behavior

### Supported resource types

| Resource type | Match criteria | Merge strategy |
|---|---|---|
| Patient | PhilHealth ID or any identifier system+value | Incoming wins; keep existing non-empty fields; identifier lists unioned |
| Practitioner | Any identifier system+value | Same as Patient |
| Organization | Any identifier system+value | Same as Patient |

Multiple matches → picks newest by `meta.lastUpdated`.

### Response format on duplicate POST

A duplicate POST returns HTTP `200` with a `Bundle` of type `collection`:

```json
{
  "resourceType": "Bundle",
  "type": "collection",
  "total": 2,
  "entry": [
    {
      "response": { "status": "200" },
      "resource": { "resourceType": "Patient", "id": "11454", ...merged fields... }
    },
    {
      "response": { "status": "200" },
      "resource": {
        "resourceType": "OperationOutcome",
        "issue": [{
          "severity": "information",
          "code": "informational",
          "diagnostics": "Merged incoming Patient into existing resource Patient/11454"
        }]
      }
    }
  ]
}
```

This is implemented via:
- `SERVER_INCOMING_REQUEST_PRE_HANDLED`: detect duplicate, merge via DAO,
  store merged resource in `RequestDetails.getUserData()`, throw a custom
  `DeduplicationMatchedException extends BaseServerResponseException` (HTTP 200)
  with a `Location` header.
- `SERVER_OUTGOING_FAILURE_OPERATIONOUTCOME`: retrieve the merged resource
  from user data, build the Bundle, replace the `ResponseDetails.resource`.

**Important:** Dedup only works for individual `POST /Patient` (etc.) calls —
not for resources created inside a transaction `Bundle`. In transactions,
individual resource creates are handled at the DAO level and bypass the
server-level `PRE_HANDLED` hook.

## Known limitations & design decisions

### `SERVER_HANDLE_EXCEPTION` does not fire for PRE_HANDLED exceptions

In HAPI 8.8.0, exceptions thrown from `SERVER_INCOMING_REQUEST_PRE_HANDLED`
hooks are caught by the main request handler catch block. However,
`SERVER_HANDLE_EXCEPTION` is only reached if no custom hook was registered
for it. The default `ExceptionHandlingInterceptor` handles it, but returning
`false` would skip the failure operation outcome hook. Instead, we hook
`SERVER_OUTGOING_FAILURE_OPERATIONOUTCOME` to replace the OperationOutcome
with a Bundle.

### Response severity is always "error" on BaseServerResponseException

HAPI's `ExceptionHandlingInterceptor.createOperationOutcome()` hardcodes
`severity: "error"` for all `BaseServerResponseException` issues. We bypass
this by replacing the entire response resource via
`SERVER_OUTGOING_FAILURE_OPERATIONOUTCOME`.

### Old-style IServerInterceptor runs before @Hook-based interceptors

`RequestValidatingInterceptor` implements the deprecated `IServerInterceptor`
interface. HAPI invokes old-style interceptors before `@Hook`-based
interceptors, regardless of `registerInterceptor()` order. This forces
`requests_enabled: false`.

### Terminology rejection of UCUM codes

The remote terminology server (`tx.fhirlab.net`) may not recognize all UCUM
codes (e.g., `mm[Hg]`). With `rejectOnSeverity(WARNING)`, this causes
validation errors. Workaround: omit `system`/`code` from `valueQuantity`
when using UCUM codes, or use plain units.

## How to operate

### Starting the server

```bash
docker compose up -d
docker compose logs -f fhir  # watch startup logs
```

Wait for the log line: `Server started successfully on port 8080`.

### Rebuilding after code changes

```bash
# 1. Build the custom image from the fork
cd hapi-fhir-jpaserver-starter
docker build -t niccoreyes/aiscream-hapi:latest .
docker push niccoreyes/aiscream-hapi:latest

# 2. Restart the stack
cd ..
docker compose down -v --remove-orphans
docker compose up -d

# 3. Wait for startup (IG preloading takes ~30-60s)
sleep 60

# 4. Verify
curl http://localhost:8080/fhir/metadata
```

### Viewing logs

```bash
docker compose logs -f fhir
```

### Postman / REST client base URL

```
http://localhost:8080/fhir
```

## Running tests

### Automated test script

```bash
python3 tests/run-bundle-test.py
```

This script:
1. Creates a Patient with PH eReferral profile
2. POSTs a transaction Bundle with 2 Observations (Blood Pressure + Hemoglobin)
   compliant with PH Core Observation profile
3. Verifies Observations were created
4. POSTs a duplicate Patient → verifies dedup returns Bundle with merged
   resource + informational OperationOutcome
5. Confirms only 1 Patient exists for the identifier

### Test logs

Test runs are saved as markdown files in `tests/`:

```
tests/bundle-transaction-test-YYYYMMDD-HHMMSS.md
```

Each log includes the curl commands, request payloads, server responses, and
verification results.

### Manual testing

```bash
# Create a valid Patient
curl -X POST http://localhost:8080/fhir/Patient \
  -H 'Content-Type: application/json' \
  -d '{"resourceType":"Patient","meta":{"profile":["urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"]},"identifier":[{"system":"http://philhealth.gov.ph/fhir/Identifier/philhealth-id","value":"TEST-001"}],"name":[{"family":"Test","given":["User"]}],"gender":"male","birthDate":"1980-01-01"}'

# Duplicate POST (same identifier) — returns Bundle with merged Patient + info OO
curl -X POST http://localhost:8080/fhir/Patient \
  -H 'Content-Type: application/json' \
  -d '{"resourceType":"Patient","meta":{"profile":["urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"]},"identifier":[{"system":"http://philhealth.gov.ph/fhir/Identifier/philhealth-id","value":"TEST-001"}],"name":[{"family":"Test","given":["Merged"]}],"gender":"female"}'

# POST without meta.profile — should be rejected
curl -X POST http://localhost:8080/fhir/Patient \
  -H 'Content-Type: application/json' \
  -d '{"resourceType":"Patient","name":[{"family":"No","given":["Profile"]}],"gender":"male","birthDate":"1980-01-01"}'

# POST a transaction Bundle with Observations
# See tests/run-bundle-test.py for the full payload
```

## Debugging process & key learnings

### 1. `STORAGE_PRESTORAGE_RESOURCE_CREATED` hook doesn't work for dedup

Even when registered before the `RepositoryValidatingInterceptor`, the storage
hook fires but the resource modifications are not visible to the validator.
HAPI's storage pipeline may use a copy of the resource.

**Solution:** Use `SERVER_INCOMING_REQUEST_PRE_HANDLED` instead. At this level,
we can search for existing matches, merge via the DAO directly, and throw a
HAPI exception to abort processing.

### 2. DAO search requires `setLoadSynchronous(true)` + `SystemRequestDetails`

Without `setLoadSynchronous(true)`, `IBundleProvider.getResources()` returned
empty results even when the REST API search worked. Adding
`SystemRequestDetails` as the request context ensures a fresh, non-cached
search.

### 3. `@Interceptor(order = N)` does NOT override registration order

HAPI's `RestfulServer.registerInterceptor()` adds interceptors to a list.
Invocation order follows registration order, not the `@Interceptor(order)`
annotation. The annotation's `order` attribute controls ordering within a
single interceptor's hooks, not between different interceptors.

### 4. Returning a custom resource from a hook

`BaseServerResponseException` only produces `OperationOutcome` responses.
To return an arbitrary resource (e.g., a `Bundle` with the merged Patient),
we hook `SERVER_OUTGOING_FAILURE_OPERATIONOUTCOME` which provides a mutable
`ResponseDetails` object. Calling `setResponseResource(bundle)` and
`setResponseCode(200)` replaces the failure response entirely. HAPI's
`ExceptionHandlingInterceptor` then streams the new resource using normal
content negotiation.

### 5. `@Component` + `custom-bean-packages` for Spring-injected interceptors

The starter's `registerCustomInterceptors()` first tries
`ApplicationContext.getBean()`. If the class is annotated with `@Component`
and the package is listed in `custom-bean-packages`, Spring creates the bean
with dependency injection (e.g. `DaoRegistry`). If not found, it falls back to
reflection instantiation (POJO, no injection).

## Configuration

See `application.yaml` for all settings. Key properties:

```yaml
hapi:
  fhir:
    enable_repository_validating_interceptor: true  # auto-validation
    custom-bean-packages: ph.phcore.interceptor   # scan dedup interceptor
    custom-interceptor-classes:
      - ph.phcore.interceptor.PhCoreDeduplicationInterceptor
    validation:
      requests_enabled: false  # must be false: RequestValidatingInterceptor
                               # runs before PRE_HANDLED hooks
    implementationguides:
      ph_core: ...
      ph_eref: ...
    remote_terminology_service:
      all:
        system: '*'
        url: 'https://tx.fhirlab.net/fhir'
```

## Fork & image updates

```bash
cd hapi-fhir-jpaserver-starter
# Make code changes...
docker build -t niccoreyes/aiscream-hapi:latest .
docker push niccoreyes/aiscream-hapi:latest
cd .. && docker compose up -d
```
