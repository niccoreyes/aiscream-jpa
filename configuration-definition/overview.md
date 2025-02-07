# Overview

The `application.yaml` file configures a HAPI FHIR server using Spring Boot. It configures the database connection, the HAPI FHIR server, and the loading of the AU Core IG, including its dependencies (with specific exclusions) and the treatment of certain URLs as logical references. It sets up a complete HAPI FHIR environment ready to use the AU Core IG.

```yaml
spring:
  datasource:
    url: 'jdbc:postgresql://db:5432/hapi'
    username: admin
    password: admin
    driverClassName: org.postgresql.Driver
  jpa:
    properties:
      hibernate.dialect: ca.uhn.fhir.jpa.model.dialect.HapiFhirPostgresDialect
      hibernate.search.enabled: false

hapi:
  fhir:
    implementationguides:
      au_core:
        name: hl7.fhir.au.core
        version: 1.0.0
        reloadExisting: false
        installMode: STORE_AND_INSTALL
        fetchDependencies: true
        dependencyExcludes:
           - "hl7.fhir.uv.extensions"
           - "hl7.terminology.r5"
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
Let's break down each section:

**`spring` Section:**

*   `datasource`:** This section configures the connection to the PostgreSQL database.
    *   `url`: The JDBC URL for connecting to the database. It specifies that the database is hosted on a service named `db` (which would be defined in your Docker Compose file) at port 5432, and the database name is `hapi`.
    *   `username`: The database username (`admin`).
    *   `password`: The database password (`admin`).
    *   `driverClassName`: The fully qualified name of the PostgreSQL JDBC driver class.

*   `jpa`:** This section configures the Java Persistence API (JPA), which HAPI FHIR uses to interact with the database.
    *   `properties`:**  Additional JPA properties.
        *   `hibernate.dialect`: Specifies the Hibernate dialect to use, which is `ca.uhn.fhir.jpa.model.dialect.HapiFhirPostgresDialect`. This is a custom dialect specifically designed for HAPI FHIR's interaction with PostgreSQL, optimized for FHIR resources and data structures.
        *   `hibernate.search.enabled`: Disables Hibernate Search, a full-text search capability.  This is disabled for performance reasons.

**`hapi` Section:**

*   `fhir`:** This section configures the HAPI FHIR server itself.
    *   `implementationguides`:** This section defines the Implementation Guides (IGs) to be loaded.
        *   `au_core`:** Configuration for the AU Core IG.
            *   `name`: The name of the IG (`hl7.fhir.au.core`). This often corresponds to the NPM package name.
            *   `version`: The version of the IG (`1.0.0`).
            *   `reloadExisting`:  A boolean value. When `false`, the IG is only installed if it doesn't already exist. When `true`, it will be reinstalled on server startup, even if it is already present.
            *   `installMode`: Specifies how the IG should be installed. `STORE_AND_INSTALL` means that the IG's conformance resources (StructureDefinitions, ValueSets, etc.) will be stored and made available for validation, and any example resources included in the IG package will also be loaded into the server.  [See here for details](./store-mode.md).
            *   `fetchDependencies`:  A boolean value. When `true`, HAPI FHIR will automatically fetch and install any IGs that the `au_core` IG depends on.  [See here for details](./fetch-dependencies.md).
            *   `dependencyExcludes`: A list of regular expressions. Any dependency whose name matches one of these expressions will be excluded.  This is used to resolve dependency conflicts.  In this case, it excludes the `hl7.fhir.uv.extensions` and `hl7.terminology.r5` packages, because of version conflicts. [See here for details](./dependency-error.md).
    *   `logical_urls`:** This section defines which URLs should be treated as *logical references*. [See here for details](./logical-url.md).
