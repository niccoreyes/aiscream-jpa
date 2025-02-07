# Overview

The Docker Compose file defines a two-service application: a HAPI FHIR server and a PostgreSQL database.  

In summary, this Docker Compose file sets up a HAPI FHIR server connected to a PostgreSQL database.  The `application.yaml` file, containing the server's configuration, is injected into the container using Docker Compose's `configs` mechanism.  This keeps the configuration separate from the image, making it easy to manage and modify. Please [read here for the details of the injection mechanism](./inserting-configuration).

The `depends_on` clause makes sure that the database is running before the HAPI FHIR server attempts to start. The persistent volume for the database ensures that your data is not lost when the container is stopped.

Let's break down the configuration:

```yaml
services:  # Defines the services that make up the application.

  fhir:  # Defines the HAPI FHIR server service.
    container_name: hapi  # Sets the container name for easy identification.
    image: "hapiproject/hapi:v7.6.0"  # Specifies the Docker image to use for the HAPI FHIR server. This pulls the hapiproject/hapi image tagged with version v7.6.0.
    ports:
      - "8080:8080"  # Maps port 8080 on the host machine to port 8080 in the container, making the HAPI FHIR server accessible.
    configs:  # Grants access to configuration files.
      - source: hapi  # Refers to the config named "hapi" defined below.
        target: /app/config/application.yaml  # Mounts the "hapi" config file inside the container at /app/config/application.yaml.  This is a standard location where Spring Boot looks for configuration files.
    depends_on:  # Specifies that the "fhir" service depends on the "db" service. Docker Compose will start the "db" service before the "fhir" service.

  db:  # Defines the PostgreSQL database service.
    image: "postgres:17.2-bookworm"  # Specifies the Docker image to use for PostgreSQL (version 17.2).
    restart: always  # Ensures that the database container restarts if it crashes.
    environment:  # Sets environment variables for the database.
      POSTGRES_PASSWORD: admin  # Sets the PostgreSQL root password.
      POSTGRES_USER: admin  # Sets the PostgreSQL user.
      POSTGRES_DB: hapi  # Sets the database name.
    volumes:  # Mounts a volume for persistent database storage.
      - ./hapi.postgress.data:/var/lib/postgresql/data  # Maps the local directory "./hapi.postgress.data" to the PostgreSQL data directory in the container. This ensures that database data is persisted even if the container is stopped or removed.

configs:  # Defines the configuration files to be used by the services.
  hapi:  # Defines a config named "hapi".
    file: ./application.yaml  # Specifies that the source of the "hapi" config is the local file "./application.yaml".  This file contains the Spring Boot and HAPI FHIR server configuration.
```

Reference:

* https://docs.docker.com/reference/compose-file/
