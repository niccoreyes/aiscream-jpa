## Why

The PH eReferral HAPI FHIR server needs to automatically validate all resources
against PH Core and PH eReferral Implementation Guide profiles, enforce strict
terminology validation, and auto-merge duplicate Patient, Practitioner, and
Organization resources by identifier — without requiring clients to call
`$validate` or manage deduplication logic.

The stock `hapiproject/hapi` Docker image supports configuration-only
auto-validation (Option A) but cannot run custom interceptors for strict
terminology enforcement or identifier-based deduplication (Option B).
Therefore, the `hapi-fhir-jpaserver-starter` was forked and a custom Docker
image (`niccoreyes/aiscream-hapi:latest`) was built.

## What Changes

### Configuration (stock image)
- Enable `RepositoryValidatingInterceptor` to validate all stored resources
  against known StructureDefinitions
- Enable `RequestValidatingInterceptor` for HTTP-layer validation (later
  disabled due to interceptor ordering constraints — see below)
- Preload PH Core (0.2.0) and PH eReferral (0.1.0) IGs as stored
  StructureDefinitions at startup
- Configure remote terminology validation via `https://tx.fhirlab.net/fhir`
- All resource writes (POST/PUT, Bundles, patches) are validated automatically
- Resources without `meta.profile` are rejected with 422 HAPI-0575

### Fork customizations
- **StarterJpaConfig.java**: Move `registerCustomInterceptors()` before
  `RepositoryValidatingInterceptor` registration so dedup runs before validation
- **RepositoryValidationInterceptorFactoryR4.java**: Add
  `.rejectOnSeverity(WARNING)`, `.suppressNoBindingMessage()`, and
  `.suppressWarningForExtensibleValueSetValidation()` for strict terminology
  enforcement
- **PhCoreDeduplicationInterceptor.java**: New interceptor in
  `ph.phcore.interceptor` for auto-merge on identifier match:
  - Hooks `SERVER_INCOMING_REQUEST_PRE_HANDLED` for both `CREATE` and
    `TRANSACTION` operations
  - For individual POST: merges via DAO and returns dedup Bundle
  - For transaction Bundles: converts matching entries from POST to PUT
    against existing resource IDs, preserving fullUrl for reference resolution

### Known constraint
`hapi.fhir.validation.requests_enabled` is set to `false`. The
`RequestValidatingInterceptor` is an old-style `IServerInterceptor` that fires
at `SERVER_INCOMING_REQUEST_POST_PROCESSED`, which is **before**
`SERVER_INCOMING_REQUEST_PRE_HANDLED` (the dedup hook). HAPI invokes
old-style interceptors before `@Hook`-based interceptors regardless of
`registerInterceptor()` order, so request-level validation must remain disabled
to allow dedup to run first. The `RepositoryValidatingInterceptor` at the
`STORAGE` level still validates all resources on insert/update.

## Capabilities

### New Capabilities
- `auto-validation`: Automatic FHIR validation against PH Core and PH eReferral
  IG profiles on every resource write, using stock HAPI JPA server configuration
- `strict-terminology-validation`: Reject resources with invalid or unresolvable
  codes in any coded element
- `identifier-deduplication`: Auto-merge duplicate Patient, Practitioner, and
  Organization resources on POST (both individual and within transaction
  Bundles) by matching identifiers

## Impact

- Affected configuration: `application.yaml` (hapi.fhir section)
- Affected behavior: All resource writes are validated; invalid payloads are
  rejected at the repository layer; duplicates are auto-merged
- Remote terminology dependency: `https://tx.fhirlab.net/fhir` must be
  accessible
- Custom Docker image: `niccoreyes/aiscream-hapi:latest`
- Fork: `niccoreyes/hapi-fhir-jpaserver-starter` (based on upstream 8.8.0)
