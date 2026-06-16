## ADDED Requirements

### Requirement: Invalid or unresolvable terminology codes SHALL be rejected

The system SHALL reject any resource write that contains a coded value which
cannot be validated against its declared CodeSystem or bound ValueSet. This
applies to all coded elements in PH Core and PH eReferral profiles (e.g. PSGC,
PSOC, PSCED, disability type, medication codes, etc.).

The validation behavior MUST:
1. Validate every coded value against its declared `system` and any bound ValueSet.
2. Treat a non-existent or invalid code as an `ERROR`-severity validation issue.
3. Treat an unresolvable or unknown code system as an `ERROR`-severity validation
   issue.
4. Reject the resource write when any such `ERROR` is present.

#### Scenario: Invalid code value is rejected
- **WHEN** a resource is submitted with a code value that does not exist in its
  declared CodeSystem or bound ValueSet
- **THEN** the system returns HTTP 422 with an OperationOutcome describing the
  invalid code
- **AND** the resource is not stored

#### Scenario: Unresolvable code system is rejected
- **WHEN** a resource references a code system that cannot be resolved by the
  configured terminology service
- **THEN** the system returns HTTP 422 with an OperationOutcome describing the
  unresolvable code system
- **AND** the resource is not stored

### Requirement: Strict terminology validation is enforced via custom interceptor

The system SHALL provide a custom `RepositoryValidatingInterceptor` configured
to reject on `WARNING` severity for terminology-related issues, or a custom
post-processing interceptor that promotes terminology warnings to errors.

#### Scenario: Unknown code system produces error
- **WHEN** the validator encounters a code system it cannot resolve
- **THEN** the issue severity is raised to ERROR before the
  `RepositoryValidatingInterceptor` decision
- **AND** the resource write is rejected
