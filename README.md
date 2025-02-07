# Overview

This code demonstrates how to start a HAPI FHIR server using Docker Compose and implicitly load an Implementation Guide (IG) upon startup.  The setup leverages both Docker Compose and Spring Boot configuration mechanisms to achieve this.  The code and accompanying configuration files provide a streamlined approach to deploying a HAPI FHIR server pre-configured with a specific IG, simplifying development and testing. The following sections will detail the process:

1.  [**Docker Compose and Configuration Injection (including Spring Boot):**](./configuration-injection/docker-config.md) This subsection explains how Docker Compose is used to mount the necessary configuration files, including those for Spring Boot, into the HAPI FHIR server container, enabling the server to load the IG on startup.

2.  [**HAPI FHIR Configuration Details:**](./configuration-definition/overview) This subsection delves into the specifics of the HAPI FHIR configuration files, explaining the structure and meaning of the settings used to define the IG and its loading behavior within the HAPI FHIR server.

# Running the Setup

1.  Make sure you have Docker and Docker Compose installed.
2.  Navigate to the directory containing the `docker-compose.yml` file in your terminal.
3.  Run `docker-compose up -d` to start the containers in detached mode.
4.  The HAPI FHIR server will start, connect to the Postgres database, and automatically install the AU Core IG based on your `application.yaml` configuration.

# Verification

1.  Access the HAPI FHIR server at `http://localhost:8080`.
2.  You should be able to see the AU Core IG in the CapabilityStatement or by querying the ImplementationGuide resources. You can use the HAPI FHIR test client or tools like Postman to interact with the server.

# Troubleshooting

*   **Logs:** Check the logs of the `hapi-fhir-server` container using `docker-compose logs hapi-fhir-server` for any errors during startup or IG installation.
*   **Database:** If you have issues with the database, ensure that the credentials in your `docker-compose.yml` and `application.yaml` match.
*   **IG URL:** Double-check the URL of your Implementation Guide. A typo or incorrect path will prevent installation.

This comprehensive example should help you experiment with the AU Core FHIR Implementation Guide using HAPI FHIR and Docker Compose. Remember to replace the placeholder values in the configuration files with your actual IG URL, version, and FHIR version.