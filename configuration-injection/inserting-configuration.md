In the Docker Compose configuration, the `configs` top-level element is used to inject an external Spring application configuration file (e.g., `application.yaml`) into the HAPI FHIR server container. This mechanism allows services to adapt their behavior without requiring a rebuild of the Docker image.  Similar to volumes, configs are mounted as files into the container's filesystem.

The `configs` top-level element defines or references configuration data granted to services.  In this case, we use the `file` source to create a config from our local `application.yaml` file.  This config is then explicitly granted to the HAPI FHIR server service using the `configs` attribute within the service definition.

Inside the container, the config file is mounted at a default location (e.g., `/application.yaml` in Linux containers), effectively overlaying the default Spring Boot configuration.  Critically, Spring Boot automatically finds and loads `application.properties` and `application.yaml` files located in the `config/` subdirectory of the current directory from which the application starts. By mounting our external `application.yaml` file to the `config/` directory within the container, we leverage this Spring Boot feature.

The start instruction of the container [is here](https://github.com/hapifhir/hapi-fhir-jpaserver-starter/blob/d6359e1561cf49d928c203e2a8ab716f74d3601b/Dockerfile#L50), and it's working directory is [`/app` as shown here](https://github.com/hapifhir/hapi-fhir-jpaserver-starter/blob/d6359e1561cf49d928c203e2a8ab716f74d3601b/Dockerfile#L45). So a configuration file in `/app/config/` is found and used as an override by the server. 

This mimics Spring Boot's built-in mechanism for loading external properties from specific file system locations. By using Docker Compose's `configs` mechanism, we can customize the Spring Boot properties (and consequently HAPI FHIR settings) without modifying the default configuration files within the HAPI FHIR server image.  This approach promotes clean base images and simplifies configuration management outside the container.  It also facilitates easy configuration changes without requiring image rebuilds.

References:
* https://docs.docker.com/reference/compose-file/configs/#example-1
* https://docs.spring.io/spring-boot/reference/features/external-config.html#features.external-config.files