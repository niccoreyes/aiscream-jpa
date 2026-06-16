## Why

The PH eReferral HAPI FHIR server needs automatic FHIR validation against PH Core and
PH eReferral Implementation Guide profiles, without requiring clients to call `$validate`.
This MVP phase uses the stock `hapiproject/hapi` Docker image with auto-validation
enabled via configuration alone, establishing the baseline validation infrastructure.

## What Changes

- Enable `RepositoryValidatingInterceptor` to validate all stored resources against
  known StructureDefinitions
- Enable `RequestValidatingInterceptor` for HTTP-layer validation
- Preload PH Core (0.2.0) and PH eReferral (0.1.0) IGs as stored StructureDefinitions
- Configure remote terminology validation via `tx.fhirlab.net/fhir`
- All resource writes (POST/PUT, Bundles, patches) are validated automatically
- Resources without `meta.profile` are rejected with 422 HAPI-0575

## Capabilities

### New Capabilities
- `auto-validation`: Automatic FHIR validation against PH Core and PH eReferral IG
  profiles on every resource write, using stock HAPI JPA server configuration.

## Impact

- Affected configuration: `application.yaml` (hapi.fhir section)
- Affected behavior: All resource writes are now validated; invalid payloads are
  rejected at the repository layer
- Remote terminology dependency: `https://tx.fhirlab.net/fhir` must be accessible
- Not in scope: custom Docker images, deduplication, custom interceptors
