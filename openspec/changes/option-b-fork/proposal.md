## Why

The stock `hapiproject/hapi` Docker image cannot support custom interceptors or
modified validation rules. To enable strict terminology validation and
identifier-based deduplication, the `hapi-fhir-jpaserver-starter` must be
forked and customized.

## What Changes

- **StarterJpaConfig.java**: Move `registerCustomInterceptors()` before
  `RepositoryValidatingInterceptor` registration to ensure custom interceptors
  (dedup) run before validation.
- **RepositoryValidationInterceptorFactoryR4.java**: Add stricter
  `rejectOnSeverity(WARNING)` and suppression methods for terminology
  enforcement.
- **PhEreferralDeduplicationInterceptor.java**: New interceptor in
  `ph.ereferral.interceptor` package for auto-merge on identifier match.

## Impact

- Custom Docker image: `niccoreyes/aiscream-hapi:latest`
- Fork: `niccoreyes/hapi-fhir-jpaserver-starter` (based on upstream 8.8.0)
- Configuration: `application.yaml` registers interceptors via
  `custom-bean-packages` and `custom-interceptor-classes`
