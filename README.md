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
| `PhEreferralDeduplicationInterceptor.java` | New interceptor | Auto-merges POSTs by identifier match |

## Architecture

```
docker-compose.yml
├── fhir (custom image: niccoreyes/aiscream-hapi:latest)
│   ├── application.yaml (IGs, validation, dedup config)
│   └── PhEreferralDeduplicationInterceptor (auto-merge)
└── db (postgres:17.2-bookworm)
```

## Validation flow

```
POST /Patient
  → SERVER_INCOMING_REQUEST_PRE_HANDLED  (dedup check)
     → if duplicate found: merge via DAO, return 200
  → STORAGE_PRESTORAGE_RESOURCE_CREATED  (RepositoryValidatingInterceptor)
     → enforce profile + rejectOnSeverity(WARNING)
  → Committed (or rejected with 422)
```

## Dedup behavior

| Resource type | Match criteria | Merge strategy |
|---|---|---|
| Patient | PhilHealth ID or PhilSys ID | Incoming wins; keep existing non-empty fields; identifier lists unioned |
| Practitioner | Any identifier system+value | Same as Patient |
| Organization | Any identifier system+value | Same as Patient |

Multiple matches → picks newest by `meta.lastUpdated`.

## Debugging process & key learnings

### 1. `STORAGE_PRESTORAGE_RESOURCE_CREATED` hook doesn't work for dedup

Even when registered before the `RepositoryValidatingInterceptor`, the storage
hook fires but the resource modifications are not visible to the validator.
HAPI's storage pipeline may use a copy of the resource.

**Solution:** Use `SERVER_INCOMING_REQUEST_PRE_HANDLED` instead. At this level,
we can search for existing matches, merge via the DAO directly, and throw a
HAPI exception to return the response.

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

### 4. Anonymous `BaseServerResponseException` for clean dedup responses

`BaseServerResponseException` is abstract but can be instantiated as an
anonymous class. By overriding `getStatusCode()` to return 200, the client
receives an HTTP 200 with an OperationOutcome describing the merge — rather
than an error.

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
    custom-bean-packages: ph.ereferral.interceptor   # scan dedup interceptor
    custom-interceptor-classes:
      - ph.ereferral.interceptor.PhEreferralDeduplicationInterceptor
    validation:
      requests_enabled: true                         # HTTP-layer validation
    implementationguides:
      ph_core: ...      # fhir.ph.core 0.2.0
      ph_eref: ...      # fhir.ph.ereferral 0.1.0
    remote_terminology_service:
      all:
        system: '*'
        url: 'https://tx.fhirlab.net/fhir'
```

## Testing

```bash
# Create a valid Patient
curl -X POST http://localhost:8080/fhir/Patient -H 'Content-Type: application/json' \
  -d '{"resourceType":"Patient","meta":{"profile":["urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"]},"identifier":[{"system":"http://philhealth.gov.ph/fhir/Identifier/philhealth-id","value":"TEST-001"}],"name":[{"family":"Test","given":["User"]}],"gender":"male","birthDate":"1980-01-01"}'

# POST same identifier (no birthDate) — should auto-merge
curl -X POST http://localhost:8080/fhir/Patient -H 'Content-Type: application/json' \
  -d '{"resourceType":"Patient","meta":{"profile":["urn://example.com/ph-ereferral/fhir/StructureDefinition/ereferral-patient"]},"identifier":[{"system":"http://philhealth.gov.ph/fhir/Identifier/philhealth-id","value":"TEST-001"}],"name":[{"family":"Test","given":["Merged"]}],"gender":"female"}'

# POST without meta.profile — should be rejected
curl -X POST http://localhost:8080/fhir/Patient -H 'Content-Type: application/json' \
  -d '{"resourceType":"Patient","name":[{"family":"No","given":["Profile"]}],"gender":"male","birthDate":"1980-01-01"}'
```

## Fork & image updates

To rebuild the custom image after changing the fork:

```bash
cd hapi-fhir-jpaserver-starter
docker build -t niccoreyes/aiscream-hapi:latest .
docker push niccoreyes/aiscream-hapi:latest
cd .. && docker compose up -d
```
