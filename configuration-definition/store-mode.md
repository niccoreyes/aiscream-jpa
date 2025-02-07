In the context of HAPI FHIR and Implementation Guide (IG) installation, the `installMode` setting determines how the IG's resources are handled by the server. Here's a breakdown of the difference between `STORE_AND_INSTALL` and `STORE_ONLY`:

**`STORE_ONLY`**

*   **Focus:** This mode primarily focuses on making the IG's *conformance artifacts* available to the HAPI FHIR validator.
*   **What it does:**
    *   It stores the IG's structure definitions, code systems, value sets, and other artifacts that define the IG's rules and constraints.
    *   These artifacts are used by the validator to check if resources conform to the IG's specifications.
    *   **It does not import the actual resource instances** (e.g., Patient, Observation, etc.) that might be included in the IG package.
*   **Use case:** You would use this mode if you want to:
    *   Validate resources against the IG.
    *   Use the IG's definitions for your own resource development or customization.
    *   **Not necessarily load the example resources provided in the IG.**

**`STORE_AND_INSTALL`**

*   **Focus:** This mode goes a step further by not only storing the conformance artifacts but also importing the actual resource instances from the IG package into the HAPI FHIR data store.
*   **What it does:**
    *   It performs all the actions of `STORE_ONLY` (makes conformance artifacts available for validation).
    *   **In addition, it imports the resource instances** included in the IG package. These resources become available for standard FHIR operations like search, read, update, etc.
*   **Use case:** You would use this mode if you want to:
    *   Validate resources against the IG.
    *   Use the IG's definitions.
    *   **Populate your HAPI FHIR server with the example resources provided in the IG.** This can be useful for testing, demonstration, or initial data loading.

**In summary:**

*   `STORE_ONLY`: Makes the IG's *definitions* available for validation.
*   `STORE_AND_INSTALL`: Makes the IG's *definitions and example resources* available.

The choice between these modes depends on your specific needs. If you only need the IG's structure and constraints for validation, `STORE_ONLY` is sufficient. If you also want to load the example resources into your server, `STORE_AND_INSTALL` is the mode to use.