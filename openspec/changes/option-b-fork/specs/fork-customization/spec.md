## ADDED Requirements

### Requirement: Custom interceptor registration order
The system SHALL register custom interceptors before the built-in
RepositoryValidatingInterceptor so that pre-processing logic (e.g. dedup
merging) runs before validation.

#### Scenario: Dedup interceptor runs before validation
- **WHEN** a duplicate Patient is POSTed
- **THEN** the deduplication interceptor merges the resource before the
  RepositoryValidatingInterceptor validates it
- **AND** no duplicate resource is created

### Requirement: Stricter validation severity
The RepositoryValidatingInterceptor SHALL reject resources on WARNING severity
to catch unknown code systems and invalid terminology codes.

#### Scenario: Unknown code system rejected
- **WHEN** a resource references a code system not known to the terminology service
- **THEN** the resource write is rejected with an ERROR-level validation issue
- **AND** the resource is not stored

### Requirement: Identifier-based auto-merge interceptor
The system SHALL include a custom interceptor that detects duplicate resources
by matching identifiers and merges incoming data into existing resources
before storage.

#### Scenario: Duplicate detected by matching identifier
- **WHEN** a Patient is POSTed with a PhilHealth ID that matches an existing Patient
- **THEN** the incoming Patient is merged into the existing Patient
- **AND** HTTP 200 is returned with the merged resource
