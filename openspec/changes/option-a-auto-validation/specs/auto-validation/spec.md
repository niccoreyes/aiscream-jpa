## ADDED Requirements

### Requirement: RepositoryValidatingInterceptor enforces profile conformance
The system SHALL validate all stored resources against declared `meta.profile`
profiles using `RepositoryValidationInterceptorFactoryR4.buildUsingStoredStructureDefinitions()`.

The interceptor MUST:
1. Scan all stored `StructureDefinition` resources of `kind = resource`
2. Group them by FHIR resource type
3. For each type, require at least one stored profile in `meta.profile`
4. Validate each resource against all declared profiles

The interceptor SHALL hook into STORAGE_PRESTORAGE_RESOURCE_CREATED and
STORAGE_PRESTORAGE_RESOURCE_UPDATED pointcuts, intercepting HTTP POST/PUT,
Bundle entries, FHIR patches, and internal JPA API writes.

#### Scenario: Resource with valid profile is accepted
- **WHEN** a resource is POSTed with a valid PH Core or PH eReferral profile in `meta.profile` and passes all constraints
- **THEN** the system returns HTTP 201 Created and stores the resource

#### Scenario: Resource without meta.profile is rejected
- **WHEN** a resource is POSTed without `meta.profile`
- **THEN** the system returns HTTP 422 with OperationOutcome code HAPI-0575 stating the resource does not declare conformance to any profile

#### Scenario: Resource fails profile constraints
- **WHEN** a resource is POSTed with a declared profile but fails constraint validation (e.g., missing required fields like gender or birthDate on Patient)
- **THEN** the system returns HTTP 422 with an OperationOutcome listing the specific constraint errors

#### Scenario: Empty meta.profile array is rejected
- **WHEN** a resource is POSTed with an empty `meta.profile` array
- **THEN** the system returns HTTP 422 with OperationOutcome code HAPI-0575

### Requirement: RequestValidatingInterceptor provides HTTP-layer validation
The system SHALL enable `validation.requests_enabled: true` to add HTTP-layer
validation that rejects invalid incoming payloads at the request level, before
they reach the repository layer.

#### Scenario: Invalid payload rejected at request level
- **WHEN** a malformed or invalid FHIR payload is sent via HTTP POST
- **THEN** the system rejects it at the HTTP request layer with an appropriate error response

### Requirement: IG preloading loads PH Core and PH eReferral packages
The system SHALL preload the following Implementation Guides as stored
StructureDefinitions at startup:

| Package | Version | Source |
|---------|---------|--------|
| `fhir.ph.core` | 0.2.0 | `https://build.fhir.org/ig/UP-Manila-SILab/ph-core/package.tgz` |
| `fhir.ph.ereferral` | 0.1.0 | `https://build.fhir.org/ig/ph-ereferral-organization/ph-ereferral/package.tgz` |

The system MUST install `fhir.ph.core` before `fhir.ph.ereferral` and SHALL
exclude `fhir.ph.core` from `fhir.ph.ereferral`'s dependency resolution to
avoid the `dev` version conflict.

#### Scenario: PH Core IG loaded at startup
- **WHEN** the server starts with `installMode: STORE_AND_INSTALL`
- **THEN** `fhir.ph.core` 0.2.0 StructureDefinitions are stored and available for validation

#### Scenario: PH eReferral IG loaded after PH Core
- **WHEN** the server starts and `fhir.ph.core` is already loaded
- **THEN** `fhir.ph.ereferral` 0.1.0 StructureDefinitions are stored, with `fhir.ph.core` excluded from dependency resolution

### Requirement: Enforced profiles cover PH Core and PH eReferral resources
The system SHALL store and enforce validation for the following
StructureDefinitions:

**PH Core**: AllergyIntolerance, Claim, Condition, Encounter, HealthcareService,
Immunization, Location, Medication, MedicationAdministration, MedicationDispense,
MedicationRequest, MedicationStatement, Observation, Organization, Patient,
Practitioner, PractitionerRole, Procedure, Provenance, RelatedPerson,
ServiceRequest, Task

**PH eReferral**: Condition, Encounter, Immunization, MedicationAdministration,
Observation, Patient, PractitionerRole, Procedure, Provenance, RelatedPerson,
ServiceRequest, Task

Each resource type MUST declare at least one profile from the combined set
(PH Core or PH eReferral) and SHALL pass validation against all declared profiles.

#### Scenario: PH Core Patient with valid profile is accepted
- **WHEN** a Patient resource is POSTed with `meta.profile` containing `https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-patient` and passes all PH Core constraints
- **THEN** the system returns HTTP 201 Created

#### Scenario: PH eReferral Patient with valid profile is accepted
- **WHEN** a Patient resource is POSTed with `meta.profile` containing the eReferral Patient profile URL and passes all eReferral constraints (including additional requirements like required `contact.name`, `contact.relationship`, `gender`, `birthDate`, and `name`)
- **THEN** the system returns HTTP 201 Created

### Requirement: Bundle transaction validation is atomic
The system SHALL validate all entries in a Bundle transaction. If any entry
fails validation, the entire transaction SHALL be rolled back atomically.

#### Scenario: Valid Bundle with all entries declaring profiles
- **WHEN** a Bundle transaction is POSTed where all entries have valid profiles and pass constraints
- **THEN** the system returns HTTP 200 OK and stores all resources

#### Scenario: Bundle with mixed valid and invalid entries
- **WHEN** a Bundle transaction is POSTed containing some entries with valid profiles and some entries missing profiles or failing constraints
- **THEN** the system returns HTTP 422 with OperationOutcome errors and performs an atomic rollback (no resources are stored)

### Requirement: Remote terminology validation
The system SHALL delegate all code system validation to the remote terminology
service at `https://tx.fhirlab.net/fhir` for all code systems (`system: '*'`).

#### Scenario: Terminology code lookup succeeds
- **WHEN** a resource contains a code from a known code system (e.g., SNOMED CT, LOINC)
- **THEN** the code is validated against the remote terminology server at tx.fhirlab.net/fhir

#### Scenario: Unknown code system produces validation warning
- **WHEN** a resource contains a code from a code system not recognized by the remote terminology server
- **THEN** a warning-level OperationOutcome issue is returned indicating the code could not be validated
