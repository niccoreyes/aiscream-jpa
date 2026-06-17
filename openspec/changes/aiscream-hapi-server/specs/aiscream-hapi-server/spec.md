## ADDED Requirements

---

### Requirement: IG preloading loads PH Core and PH eReferral packages

The system SHALL preload the following Implementation Guides as stored
StructureDefinitions at startup:

| Package | Version | Source |
|---------|---------|--------|
| `fhir.ph.core` | 0.2.0 | `https://build.fhir.org/ig/UP-Manila-SILab/ph-core/package.tgz` |
| `fhir.ph.ereferral` | 0.1.0 | `https://build.fhir.org/ig/ph-ereferral-organization/ph-ereferral/package.tgz` |

The system MUST install `fhir.ph.core` before `fhir.ph.ereferral` and SHALL
exclude `fhir.ph.core` from `fhir.ph.ereferral`'s dependency resolution to
avoid the `dev` version conflict. Installation mode is `STORE_AND_INSTALL`.

#### Scenario: PH Core IG loaded at startup
- **WHEN** the server starts with `installMode: STORE_AND_INSTALL`
- **THEN** `fhir.ph.core` 0.2.0 StructureDefinitions are stored and available
  for validation

#### Scenario: PH eReferral IG loaded after PH Core
- **WHEN** the server starts and `fhir.ph.core` is already loaded
- **THEN** `fhir.ph.ereferral` 0.1.0 StructureDefinitions are stored, with
  `fhir.ph.core` excluded from dependency resolution

---

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
(PH Core or PH eReferral) and SHALL pass validation against all declared
profiles.

#### Scenario: PH Core Patient with valid profile is accepted
- **WHEN** a Patient resource is POSTed with `meta.profile` containing
  `https://fhir.doh.gov.ph/phcore/StructureDefinition/ph-core-patient` and
  passes all PH Core constraints
- **THEN** the system returns HTTP 201 Created

#### Scenario: PH eReferral Patient with valid profile is accepted
- **WHEN** a Patient resource is POSTed with `meta.profile` containing the
  eReferral Patient profile URL and passes all eReferral constraints (including
  additional requirements like required `contact.name`, `contact.relationship`,
  `gender`, `birthDate`, and `name`)
- **THEN** the system returns HTTP 201 Created

---

### Requirement: RepositoryValidatingInterceptor enforces profile conformance

The system SHALL validate all stored resources against declared `meta.profile`
profiles using `RepositoryValidationInterceptorFactoryR4.buildUsingStoredStructureDefinitions()`.

The interceptor MUST:
1. Scan all stored `StructureDefinition` resources of `kind = resource`
2. Group them by FHIR resource type
3. For each type, require at least one stored profile in `meta.profile`
4. Validate each resource against all declared profiles

The interceptor SHALL hook into `STORAGE_PRESTORAGE_RESOURCE_CREATED` and
`STORAGE_PRESTORAGE_RESOURCE_UPDATED` pointcuts, intercepting HTTP POST/PUT,
Bundle entries, FHIR patches, and internal JPA API writes.

#### Scenario: Resource with valid profile is accepted
- **WHEN** a resource is POSTed with a valid PH Core or PH eReferral profile in
  `meta.profile` and passes all constraints
- **THEN** the system returns HTTP 201 Created and stores the resource

#### Scenario: Resource without meta.profile is rejected
- **WHEN** a resource is POSTed without `meta.profile`
- **THEN** the system returns HTTP 422 with OperationOutcome code HAPI-0575
  stating the resource does not declare conformance to any profile

#### Scenario: Resource fails profile constraints
- **WHEN** a resource is POSTed with a declared profile but fails constraint
  validation (e.g., missing required fields like gender or birthDate on Patient)
- **THEN** the system returns HTTP 422 with an OperationOutcome listing the
  specific constraint errors

#### Scenario: Empty meta.profile array is rejected
- **WHEN** a resource is POSTed with an empty `meta.profile` array
- **THEN** the system returns HTTP 422 with OperationOutcome code HAPI-0575

---

### Requirement: Bundle transaction validation is atomic

The system SHALL validate all entries in a Bundle transaction. If any entry
fails validation, the entire transaction SHALL be rolled back atomically.

#### Scenario: Valid Bundle with all entries declaring profiles
- **WHEN** a Bundle transaction is POSTed where all entries have valid profiles
  and pass constraints
- **THEN** the system returns HTTP 200 OK and stores all resources

#### Scenario: Bundle with mixed valid and invalid entries
- **WHEN** a Bundle transaction is POSTed containing some entries with valid
  profiles and some entries missing profiles or failing constraints
- **THEN** the system returns HTTP 422 with OperationOutcome errors and
  performs an atomic rollback (no resources are stored)

---

### Requirement: Remote terminology validation

The system SHALL delegate all code system validation to the remote terminology
service at `https://tx.fhirlab.net/fhir` for all code systems (`system: '*'`).

#### Scenario: Terminology code lookup succeeds
- **WHEN** a resource contains a code from a known code system (e.g., SNOMED
  CT, LOINC)
- **THEN** the code is validated against the remote terminology server at
  tx.fhirlab.net/fhir

#### Scenario: Unknown code system produces validation warning
- **WHEN** a resource contains a code from a code system not recognized by the
  remote terminology server
- **THEN** a warning-level OperationOutcome issue is returned indicating the
  code could not be validated

---

### Requirement: Invalid or unresolvable terminology codes SHALL be rejected

The system SHALL reject any resource write that contains a coded value which
cannot be validated against its declared CodeSystem or bound ValueSet. This
applies to all coded elements in PH Core and PH eReferral profiles (e.g., PSGC,
PSOC, PSCED, disability type, medication codes, etc.).

The validation behavior MUST:
1. Validate every coded value against its declared `system` and any bound
   ValueSet
2. Treat a non-existent or invalid code as an `ERROR`-severity validation issue
3. Treat an unresolvable or unknown code system as an `ERROR`-severity
   validation issue
4. Reject the resource write when any such `ERROR` is present

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

---

### Requirement: Strict terminology validation is enforced via custom interceptor

The system SHALL provide a custom `RepositoryValidatingInterceptor` configured
to reject on `WARNING` severity for terminology-related issues. This is
implemented by modifying `buildUsingStoredStructureDefinitions()` in
`RepositoryValidationInterceptorFactoryR4.java` to chain
`.rejectOnSeverity(WARNING)`, `.suppressNoBindingMessage()`, and
`.suppressWarningForExtensibleValueSetValidation()`.

#### Scenario: Unknown code system produces error
- **WHEN** the validator encounters a code system it cannot resolve
- **THEN** the issue severity is raised to ERROR before the
  `RepositoryValidatingInterceptor` decision
- **AND** the resource write is rejected

---

### Requirement: Custom interceptor registration order

The system SHALL register custom interceptors before the built-in
`RepositoryValidatingInterceptor` so that pre-processing logic (e.g., dedup
merging) runs before validation. This is implemented in `StarterJpaConfig.java`
by placing `registerCustomInterceptors()` before the
`repositoryValidatingInterceptor` registration.

The `SERVER_INCOMING_REQUEST_PRE_HANDLED` hook is used (not
`STORAGE_PRESTORAGE_RESOURCE_CREATED`) because storage-level resource
modifications are not visible to the validator in HAPI 8.8.0.

#### Scenario: Dedup interceptor runs before validation
- **WHEN** a duplicate Patient is POSTed
- **THEN** the deduplication interceptor merges the resource before the
  `RepositoryValidatingInterceptor` validates it
- **AND** no duplicate resource is created

---

### Requirement: Identifier-based deduplication on individual POST

The system SHALL detect and auto-merge duplicate resources on individual
`POST /Patient`, `POST /Practitioner`, and `POST /Organization` by matching
identifiers.

The deduplication behavior MUST:
1. Search for existing resources with identical identifier system+value pairs
2. Match Patient by PhilHealth ID or PhilSys ID (either one suffices)
3. Match Practitioner and Organization by any identifier system+value pair
4. Pick the newest existing resource if multiple matches exist (by
   `meta.lastUpdated`)
5. Merge using "incoming wins, keep existing non-empty fields" strategy
6. Union identifier lists (no duplicate identifiers after merge)
7. Return HTTP 200 with the merged resource

DAO searches use `setLoadSynchronous(true)` and `SystemRequestDetails` for
reliable results. The interceptor hooks `SERVER_INCOMING_REQUEST_PRE_HANDLED`
for `RestOperationTypeEnum.CREATE`.

#### Scenario: Duplicate Patient by PhilHealth ID is merged
- **WHEN** a Patient is POSTed with a PhilHealth ID that matches an existing
  Patient
- **THEN** the incoming fields overwrite existing fields where present
- **AND** existing non-empty fields are preserved where incoming has no value
- **AND** identifier lists from both are unioned
- **AND** HTTP 200 is returned with a dedup Bundle
- **AND** no duplicate resource is created

#### Scenario: Duplicate Practitioner by any identifier is merged
- **WHEN** a Practitioner is POSTed with any identifier matching an existing
  Practitioner
- **THEN** merge proceeds as described for Patient

#### Scenario: Duplicate Organization by any identifier is merged
- **WHEN** an Organization is POSTed with any identifier matching an existing
  Organization
- **THEN** merge proceeds as described for Patient

#### Scenario: No duplicate found, normal create
- **WHEN** a resource is POSTed with identifiers not matching any existing
  resource
- **THEN** normal creation proceeds (HTTP 201)

---

### Requirement: Identifier-based deduplication in transaction Bundles

The system SHALL detect and merge duplicate Patient, Practitioner, and
Organization resources within transaction `Bundle` POSTs by matching
identifiers.

When a transaction Bundle entry matches an existing resource:
1. Read the existing resource via DAO
2. Merge the incoming resource into the existing resource in-memory (incoming
   wins, preserve existing non-empty fields, union identifiers)
3. Replace the Bundle entry's resource with the merged resource
4. Set the merged resource's `id` to the existing resource ID
5. Change the entry's `request.method` from `POST` to `PUT` and
   `request.url` to `{resourceType}/{existingId}`
6. **Preserve the entry's `fullUrl`** so that other entries in the same Bundle
   can resolve references (e.g., `Observation.subject` referencing
   `urn:uuid:patient-bt-bundle`)

The transaction then proceeds normally — HAPI processes the converted `PUT` as
an update and creates other entries (e.g., Observations) as normal.

#### Scenario: Transaction Bundle with existing Patient deduped
- **WHEN** a transaction Bundle is POSTed containing a Patient with an
  identifier matching an existing Patient, plus Observations referencing that
  Patient
- **THEN** the Patient entry is converted from `POST` to `PUT` against the
  existing resource ID
- **AND** the `fullUrl` is preserved so Observations can resolve their subject
  references
- **AND** the transaction response shows the Patient entry as updated
  (`200 OK`) and Observation entries as created (`201 Created`)
- **AND** no duplicate Patient resource is created

#### Scenario: Transaction Bundle with no matches proceeds normally
- **WHEN** a transaction Bundle is POSTed with all new resources (no identifier
  matches)
- **THEN** the Bundle is processed normally with no entry conversions

---

### Requirement: De-duplicated response format for individual POST

The system SHALL return a consistent response format for individual dedup
operations: HTTP 200 with a `Bundle` of type `collection` containing the
merged resource and an informational `OperationOutcome`.

This is implemented via:
- `SERVER_INCOMING_REQUEST_PRE_HANDLED`: detect duplicate, merge via DAO, store
  merged resource in `RequestDetails.getUserData()`, throw
  `DeduplicationMatchedException extends BaseServerResponseException`
  (HTTP 200) with a `Location` header
- `SERVER_OUTGOING_FAILURE_OPERATIONOUTCOME`: retrieve the merged resource from
  user data, build the response Bundle, replace
  `ResponseDetails.responseResource`

#### Scenario: Individual dedup returns Bundle with merged resource
- **WHEN** a duplicate resource is POSTed individually
- **THEN** the response is a `Bundle` of type `collection` containing:
  - Entry 0: the merged resource with `response.status = "200"`
  - Entry 1: an `OperationOutcome` with `severity = information` describing
    the merge
- **AND** the HTTP status code is `200`
- **AND** a `Location` header points to the merged resource

#### Scenario: Transaction dedup response is standard transaction-response
- **WHEN** dedup occurs within a transaction `Bundle`
- **THEN** the response is a standard transaction-response `Bundle` (generated
  by HAPI)
- **AND** the deduped entry shows `response.status = "200 OK"` (update) while
  new entries show `201 Created`
- **AND** no duplicate resources are created

---

### Requirement: Merge strategy preserves existing data

The merge strategy SHALL follow these rules across all supported resource types
(Patient, Practitioner, Organization):

| Field category | Behavior |
|---|---|
| Identifiers | Union; no duplicate system+value pairs |
| Name (HumanName for Patient/Practitioner, string for Org) | Incoming wins; use existing only if incoming is absent/empty |
| Gender | Incoming wins; use existing only if incoming not set |
| Birth date | Incoming wins; use existing only if incoming not set |
| Address | Incoming wins; use existing only if incoming absent/empty |
| Telecom | Incoming wins; use existing only if incoming absent/empty |
| Contact (Patient) | Incoming wins; use existing only if incoming absent/empty |
| Active | Incoming wins; use existing only if incoming not explicitly set |
| Organization name | Incoming wins; use existing only if incoming absent |

For the `active` field specifically: if neither resource explicitly sets
`active`, the merged resource SHALL NOT force it to `false`. The serialized
output omits the field (as if never set).

#### Scenario: Fields properly preserved and overwritten
- **WHEN** a merge occurs between an existing Patient (gender=male,
  birthDate=1990-06-15, name=Original) and an incoming Patient (gender=female,
  no birthDate, name=Incoming)
- **THEN** the merged result has gender=female (incoming wins), name=Incoming
  (incoming wins), and birthDate=1990-06-15   (existing preserved)

---

### Requirement: Built-in HAPI MDM enabled with PH-specific rules

The system SHALL enable HAPI's built-in MDM (`hapi.fhir.mdm_enabled: true`)
and load `mdm-rules.json` from the host filesystem at
`/app/config/mdm-rules.json` mounted via `docker-compose.yml`.

The rules SHALL:
1. Apply to `Patient`, `Practitioner`, `Organization` (`mdmTypes`)
2. Use only `IDENTIFIER` matchers matching PH Core v0.2.0 identifier slices
3. Map every identifier match to `MATCH` (not `POSSIBLE_MATCH`) — all matches
   are auto-linked; no manual review queue
4. Search candidates on `identifier` to minimize database scans
5. Declare EID systems:
   - `Patient` → `https://fhir.doh.gov.ph/phcore/identifier/philsys`
   - `Practitioner` → wildcard (`*`) — any identifier system is considered an EID
   - `Organization` → wildcard (`*`) — any identifier system is considered an EID
6. Be a JSON file hosted at the `aiscream-jpa` repository root and mounted
   read‑only into the container — not baked into the JAR classpath

#### Scenario: Patient matched on PhilSys gains Golden Resource
- **WHEN** a Patient is POSTed with a PhilSys identifier matching an
  existing Patient
- **THEN** HAPI MDM asynchronously links both source Patients to the same
  Golden Patient resource (tagged `HAPI-MDM`)
- **AND** the Golden Patient acquires the merged attributes from both sources
  via the interceptor's in-place merge

#### Scenario: Practitioner matched on any identifier
- **WHEN** a Practitioner is POSTed with an identifier matching an
  existing Practitioner
- **THEN** MDM creates/links a Golden Practitioner

#### Scenario: Organization matched on PH Core identifier slices
- **WHEN** an Organization is POSTed with an NHFR, HCPN, PAN, or PEN
  identifier matching an existing Organization
- **THEN** MDM creates/links a Golden Organization

#### Scenario: No identifier match — Golden still created
- **WHEN** a Patient/Practitioner/Organization is POSTed with no
  matching identifier
- **THEN** HAPI MDM creates a new Golden for the source resource
  (standard 1:1 initialization) — no duplicate source resources exist

---

### Requirement: Resthook subscription enables async MDM

The system SHALL enable `hapi.fhir.subscription.resthook_enabled: true`.
MDM depends on subscriptions to deliver resource-create and resource-update
events to the internal `mdm-patient`, `mdm-practitioner`, and
`mdm-organization` channels via the in-memory message broker.

#### Scenario: Subscriptions started on boot
- **WHEN** the server starts with `subscription.resthook_enabled: true`
  and `mdm_enabled: true`
- **THEN** the MDM subscriptions are registered with the subscription
  engine
- **AND** resource writes are delivered to the internal `mdm` queue

#### Scenario: Resource write triggers MDM processing
- **WHEN** a Patient is POSTed (individual or within a transaction Bundle)
- **THEN** the `mdm-patient` subscription delivers the resource to the
  MDM consumer within the polling interval (5000 ms default)
- **AND** MDM evaluates candidate matches, creates or links Golden
  resources, and populates the `MPI_LINK` table

---

### Requirement: Survivorship propagates merged source data to Golden

The system SHALL configure `MdmSettings.setPreventEidUpdates(false)` and
`MdmSettings.setPreventMultipleEids(false)` so that Golden Resources may
accumulate EIDs and receive field updates from linked source resources.

The PhCoreDeduplicationInterceptor handles in-place merging synchronously
(identifier match found → merged into existing source → source persisted).
MDM reads the already-merged source and applies default field-by-field
survivorship: non-null source fields populate the Golden, and EIDs flow
from source to Golden.

#### Scenario: Merged source feeds Golden
- **WHEN** the interceptor merges an incoming Patient into an existing
  Patient (in-place merge via DAO), and the merged source is then
  delivered to the `mdm-patient` subscription
- **THEN** the Golden Patient reflects the merged source's attributes
  — name, gender, birthDate, address, etc. — as populated from the
  richer merged source

#### Scenario: Subsequent update propagates new fields
- **WHEN** a linked source Patient is updated (via individual PUT or
  transaction Bundle PUT from the interceptor's POST→PUT conversion)
- **THEN** the Golden Patient's fields that were previously empty
  are populated from the updated source
- **AND** the Golden's EID (PhilSys) remains stable

---

### Requirement: mdm-rules.json loaded from host-mounted volume

The system SHALL load `mdm-rules.json` from the host filesystem via
docker-compose `volumes` binding (`./mdm-rules.json:/app/config/mdm-rules.json:ro`),
not from the JAR classpath. The fork's `application.yaml` declares
`mdm_rules_json_location: "file:/app/config/mdm-rules.json"`.

Operators can edit the file on the host and restart the container to
apply rule changes without rebuilding the Docker image.

#### Scenario: Host file read on startup
- **WHEN** the `hapi` container starts with the host file present
  at `./mdm-rules.json`
- **THEN** MDM rules are loaded and applied

#### Scenario: Missing file triggers startup error
- **WHEN** the `hapi` container starts without a valid
  `mdm-rules.json` at the configured path
- **THEN** MDM fails to initialize and the server reports a
  configuration error

---

### Requirement: PhCoreDeduplicationInterceptor works alongside MDM

The existing `PhCoreDeduplicationInterceptor` SHALL remain active
alongside built-in HAPI MDM, providing **synchronous** identifier-match
feedback to clients (HTTP 200 with collection Bundle). MDM provides
**asynchronous** Golden-Resource coordination via subscriptions.

The two layers MUST NOT conflict:
1. Interceptor merges in-place via DAO (sync, PRE_HANDLED)
2. Validator checks PH Core profile conformance on the merged resource
3. Merged source is persisted
4. MDM subscription fires → link source to Golden, apply survivorship

#### Scenario: POST returns 200 immediately; Golden appears async
- **WHEN** a duplicate Patient is POSTed individually
- **THEN** the interceptor returns HTTP 200 with a collection Bundle
  (synchronous dedup feedback)
- **AND** within the polling interval (~5 s), MDM creates/links the
  Golden Patient with `HAPI-MDM` tag

#### Scenario: Transaction Bundle entry deduped, then linked
- **WHEN** a transaction `Bundle` is POSTed containing a Patient
  matching an existing Patient
- **THEN** the interceptor converts the entry from `POST` to `PUT`
  against the existing Patient ID (`fullUrl` preserved)
- **AND** MDM links the canonical Patient to its Golden (no duplicate
  Golden if one already exists with the same EID)

---

### Requirement: MPI_LINK table generated and queryable

The system SHALL create the `MPI_LINK` table on startup when
`mdm_enabled: true` and make link records queryable via
`GET /$mdm/links?resourceType=Patient&goldenResourceId={id}`.

#### Scenario: Matching sources share one Golden
- **WHEN** two Patients with the same PhilSys identifier are POSTed at
  different times
- **THEN** both source Patient records have an `MPI_LINK` row pointing
  to the same Golden Patient
- **AND** each link's `matchResult` is `MATCH`
- **AND** each link's `linkSource` is `AUTO`

