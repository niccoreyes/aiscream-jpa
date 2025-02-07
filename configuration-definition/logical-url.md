The `logical_urls` section in HAPI FHIR's configuration defines which URLs the server should treat as [*logical references*](https://hapifhir.io/hapi-fhir/docs/server_jpa/configuration.html#logical-references). This is crucial for distinguishing between URLs that are identifiers (logical references) and those that are network locations (literal references).  This setting instructs the server on how to interpret references within FHIR resources.  It's particularly common and important for FHIR *conformance resources*, such as CodeSystems, ValueSets, and Mappings.

Below is the part of the configuration pertaining to the logical URLs of the configuration:



```yaml
hapi:
  fhir:
    logical_urls:
      - http://terminology.hl7.org/*
      - https://terminology.hl7.org/*
      - http://snomed.info/*
      - https://snomed.info/*
      - http://unitsofmeasure.org/*
      - https://unitsofmeasure.org/*
      - http://loinc.org/*
      - https://loinc.org/*
      - http://hl7.org.au/*
      - https://hl7.org.au/*
```

The `logical_urls` configuration advises the server that any references found in resources with a base URL matching an entry in this section should be treated as *logical references*, not as URLs to be fetched. This configuration [passes its parameters](https://github.com/hapifhir/hapi-fhir-jpaserver-starter/blob/d6359e1561cf49d928c203e2a8ab716f74d3601b/src/main/java/ca/uhn/fhir/jpa/starter/common/FhirServerConfigCommon.java#L176) to the [`setTreatReferencesAsLogical()` method in `ca.uhn.fhir.jpa.model.entity.StorageSettings`](https://hapifhir.io/hapi-fhir/apidocs/hapi-fhir-jpaserver-model/ca/uhn/fhir/jpa/model/entity/StorageSettings.html#setTreatReferencesAsLogical(java.util.Set)), which controls how HAPI FHIR handles references.

A *logical reference* is an *identifier* for a resource *within the current FHIR server*.  It does *not* resolve to a real-world URL.  It's a key HAPI FHIR uses to find the resource in its database.  A *literal reference* is a full URL pointing to a resource on a different server.

CodeSystems, ValueSets, and Mappings are often referenced logically.  For example, a resource might refer to a ValueSet using its canonical URL as an identifier (e.g., `ValueSet/valueset-quantity-comparator`).  This is a logical reference.  The server should *not* try to fetch the ValueSet from that URL.  Instead, it should find the ValueSet within its own storage based on that identifier.

By including the base URLs for CodeSystems, ValueSets, and Mappings (e.g., `http://hl7.org/fhir/ValueSet/`, `http://hl7.org/fhir/CodeSystem/`, `http://hl7.org/fhir/Mapping/`) in the `logical_urls` configuration, you tell HAPI FHIR to treat references starting with those URLs as logical.  This is essential because these conformance resources are typically managed within the FHIR server itself.

The `logical_urls` configuration is vital for performance and data integrity.  It prevents unnecessary network requests and ensures the server works with its own resources.  By defining which URLs are logical, you give HAPI FHIR the context it needs to handle references correctly, especially for conformance resources that are core to FHIR's functionality.








