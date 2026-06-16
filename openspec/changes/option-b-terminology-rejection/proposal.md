## Why

Option A enables automatic validation against PH Core and PH eReferral profiles,
but the stock HAPI configuration cannot enforce strict terminology validation.
Unknown or unresolvable code systems produce warnings that do not trigger
rejection. Additionally, the stock server lacks identifier-based deduplication,
which is needed to prevent duplicate Patient, Practitioner, and Organization
resources in the eReferral system.

This change ensures every code in an IG profile is validated and rejected if
invalid or unresolvable, and adds automatic merge-on-duplicate behavior for
key resource types.

## What Changes

- Fork `hapi-fhir-jpaserver-starter` and build a custom Docker image
  (`niccoreyes/aiscream-hapi:latest`).
- Modify `RepositoryValidationInterceptorFactoryR4.java`:
  - Chain `.rejectOnSeverity(WARNING)` in `buildUsingStoredStructureDefinitions()`
  - Add `.suppressNoBindingMessage()` and `.suppressWarningForExtensibleValueSetValidation()`
- Add `PhEreferralDeduplicationInterceptor.java` in `ph.ereferral.interceptor`:
  - Hooks `SERVER_INCOMING_REQUEST_PRE_HANDLED` (runs before validation)
  - Searches for existing Patient/Practitioner/Organization by matching identifiers
  - Merges incoming fields into existing ("incoming wins" strategy)
  - Returns HTTP 200 with dedup OperationOutcome instead of creating duplicates
  - Uses `setLoadSynchronous(true)` and `SystemRequestDetails` for reliable DAO queries
- Modify `StarterJpaConfig.java`:
  - Move `registerCustomInterceptors()` call BEFORE `repositoryValidatingInterceptor`
    registration to ensure dedup runs before validation

## Capabilities

### New Capabilities
- `strict-terminology-validation`: Reject resources with invalid or unresolvable
  codes in any PH Core or PH eReferral coded element.
- `identifier-deduplication`: Auto-merge duplicate Patient, Practitioner, and
  Organization resources on POST by matching identifiers.

## Impact

- Affected code: custom HAPI JPA starter fork at `niccoreyes/hapi-fhir-jpaserver-starter`
- Affected behavior: all resource writes (POST/PUT/Bundles/patches) fail if any
  code cannot be validated; duplicates are auto-merged instead of creating new resources
- Dependency: remote terminology service plus any locally-loaded CodeSystems
- Docker image: `niccoreyes/aiscream-hapi:latest`
