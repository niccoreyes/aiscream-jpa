## Why

Option A enables automatic validation against PH Core and PH eReferral profiles,
but the stock HAPI configuration cannot enforce strict terminology validation.
Unknown or unresolvable code systems produce warnings that do not trigger
rejection. This change ensures every code in an IG profile is validated and
rejected if invalid or unresolvable.

## What Changes

- Fork `hapi-fhir-jpaserver-starter` and build a custom Docker image.
- Provide a custom `IRepositoryValidationInterceptorFactory` that creates a
  `RepositoryValidatingInterceptor` with stricter terminology handling.
- Add a `ValidationMessageUnknownCodeSystemPostProcessingInterceptor` (or
  equivalent) to promote unknown/unresolvable code-system issues to ERROR.
- Ensure `RemoteTerminologyServiceValidationSupport` still delegates to
  `https://tx.fhirlab.net/fhir`, but local/unknown code systems are treated as
  errors rather than warnings.

## Capabilities

### New Capabilities
- `strict-terminology-validation`: Reject resources with invalid or unresolvable
  codes in any PH Core or PH eReferral coded element.

## Impact

- Affected code: custom HAPI JPA starter fork.
- Affected behavior: all resource writes (POST/PUT/Bundles/patches) fail if any
  code cannot be validated.
- Dependency: remote terminology service plus any locally-loaded CodeSystems.
