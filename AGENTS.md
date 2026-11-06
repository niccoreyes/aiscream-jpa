# AGENTS.md — aiscream-jpa

## Operations

### Start HAPI (builds interceptor first; preserves data)
```bash
./up.sh
```
`up.sh` removes the prior one-shot builder container, then runs Compose for `fhir`.
The `depends_on` condition makes Compose run the `interceptor` builder first: it mounts
`hapi-extra-classes/` at `/src`, removes stale `ext/`, runs `mvn -q -B clean package`,
and removes Maven's `target/` directory on exit. The generated runtime class is copied
back into `ext/` in the same folder. HAPI is force-recreated only after compilation
succeeds, so it loads the new class. Maven redownloads dependencies on each build; there
is no persistent Maven cache volume.

Run `./up.sh` after Java changes. A plain `docker compose up` builds first on a clean
start, but may reuse the successful one-shot builder after later source changes. If you
need to start HAPI without rebuilding, use `docker compose up -d --wait fhir`.

After a successful build, `hapi-extra-classes/ext/RepositoryValidationInterceptorFactoryR4.class`
is the required runtime artifact. The `target/` directory is temporary and removed after
the build; `ext/` is recreated cleanly each time.

### Restart normally (preserves data)
```bash
docker compose down && ./up.sh
```

### Restart fresh (wipes database, clean slate) 
Avoid doing this unless you are on a repeated error, or if the changes necessitate starting from scratch
```bash
docker compose down -v && rm -rf hapi.postgress.data && ./up.sh
```

## Debugging

### Check Docker logs
```bash
docker compose logs --tail=2000 | grep -i "error\|exception\|FAILED\"
```

### Verify remote terminology service
```bash
# Check if tx.fhirlab.net has a CodeSystem
curl -s "https://tx.fhirlab.net/fhir/CodeSystem?url=<CODESYSTEM_URL>" | python3 -m json.tool

# List all CodeSystems
curl -s "https://tx.fhirlab.net/fhir/CodeSystem?_count=5&_summary=true" | python3 -m json.tool

# Delete a resource from tx.fhirlab.net
curl -s -X DELETE "https://tx.fhirlab.net/fhir/CodeSystem/<ID>" -H "Content-Type: application/fhir+json"
```

### Test local FHIR server
```bash
curl -s http://localhost:8080/fhir/metadata | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('software',{}).get('name'), d.get('software',{}).get('version'))"
```

## Configuration lookups

### HAPI FHIR JPA starter — reference application.yaml
Always check the canonical starter config for property structure:
```
https://raw.githubusercontent.com/hapifhir/hapi-fhir-jpaserver-starter/refs/heads/master/src/main/resources/application.yaml
```

Consider `gh cli` to navigate.

### HAPI FHIR docs
- Root: `https://hapifhir.io/hapi-fhir/docs/`
- JPA config: `https://hapifhir.io/hapi-fhir/docs/server_jpa/configuration.html`
- Lucene/Elasticsearch: `https://hapifhir.io/hapi-fhir/docs/server_jpa/elastic.html`
- Terminology: `https://hapifhir.io/hapi-fhir/docs/server_jpa/terminology.html`
- Validation support: `https://hapifhir.io/hapi-fhir/docs/validation/validation_support_modules.html`
- Package registry: `https://hapifhir.io/hapi-fhir/docs/server_jpa/packages.html`

### GitHub repos (use `gh` CLI or raw.githubusercontent.com)
- HAPI FHIR core: `hapifhir/hapi-fhir`
- HAPI JPA starter: `hapifhir/hapi-fhir-jpaserver-starter`
