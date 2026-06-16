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
to reject on `WARNING` severity for terminology-related issues. This is
implemented by modifying `buildUsingStoredStructureDefinitions()` in
`RepositoryValidationInterceptorFactoryR4.java` to chain `.rejectOnSeverity(WARNING)`,
`.suppressNoBindingMessage()`, and `.suppressWarningForExtensibleValueSetValidation()`.

#### Scenario: Unknown code system produces error
- **WHEN** the validator encounters a code system it cannot resolve
- **THEN** the issue severity is raised to ERROR before the
  `RepositoryValidatingInterceptor` decision
- **AND** the resource write is rejected

### Requirement: Identifier-based deduplication on POST

The system SHALL detect duplicate resources on POST operations for Patient,
Practitioner, and Organization by matching identifiers. When a duplicate is
found, the incoming resource SHALL be merged into the existing resource and
the existing resource SHALL be updated via the JPA DAO layer.

The deduplication behavior MUST:
1. Search for existing resources with identical identifier system+value pairs.
2. Match Patient by PhilHealth ID or PhilSys ID (either one suffices).
3. Match Practitioner and Organization by any identifier system+value pair.
4. Pick the newest existing resource if multiple matches exist.
5. Merge using "incoming wins, keep existing non-empty fields" strategy.
6. Union identifier lists (no duplicate identifiers after merge).
7. Return HTTP 200 with the merged resource.

The deduplication interceptor hooks `SERVER_INCOMING_REQUEST_PRE_HANDLED` (not
STORAGE level) to ensure it runs before validation. DAO searches use
`setLoadSynchronous(true)` and `SystemRequestDetails` for reliable results.
Registration order in `StarterJpaConfig` places custom interceptors before the
`RepositoryValidatingInterceptor`.

#### Scenario: Duplicate Patient by PhilHealth ID is merged
- **WHEN** a Patient is POSTed with a PhilHealth ID that matches an existing Patient
- **THEN** the incoming fields overwrite existing fields where present
- **AND** existing non-empty fields are preserved where incoming has no value
- **AND** identifier lists from both are unioned
- **AND** HTTP 200 is returned with a dedup OperationOutcome
- **AND** no duplicate resource is created

#### Scenario: Duplicate Practitioner by any identifier is merged
- **WHEN** a Practitioner is POSTed with any identifier matching an existing Practitioner
- **THEN** merge proceeds as described for Patient

#### Scenario: No duplicate found, normal create
- **WHEN** a resource is POSTed with identifiers not matching any existing resource
- **THEN** normal creation proceeds (HTTP 201)
