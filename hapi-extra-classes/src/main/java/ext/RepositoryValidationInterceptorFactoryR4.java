/*
 * Adapted from the HAPI FHIR JPA starter's RepositoryValidationInterceptorFactoryR4:
 * https://github.com/hapifhir/hapi-fhir-jpaserver-starter/blob/master/src/main/java/ca/uhn/fhir/jpa/starter/common/validation/RepositoryValidationInterceptorFactoryR4.java
 */
package ext;

import ca.uhn.fhir.context.FhirContext;
import ca.uhn.fhir.jpa.api.dao.DaoRegistry;
import ca.uhn.fhir.jpa.api.dao.IFhirResourceDao;
import ca.uhn.fhir.jpa.interceptor.validation.IRepositoryValidatingRule;
import ca.uhn.fhir.jpa.interceptor.validation.RepositoryValidatingInterceptor;
import ca.uhn.fhir.jpa.interceptor.validation.RepositoryValidatingRuleBuilder;
import ca.uhn.fhir.jpa.searchparam.SearchParameterMap;
import ca.uhn.fhir.rest.api.server.IBundleProvider;
import ca.uhn.fhir.rest.param.TokenParam;
import org.hl7.fhir.r4.model.StructureDefinition;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

@Configuration
public class RepositoryValidationInterceptorFactoryR4 {

	private static final String PH_CORE_PROFILE_PREFIX =
			"https://fhir.doh.gov.ph/phcore/StructureDefinition/";

	@Bean
	@Primary
	public RepositoryValidatingInterceptor phCoreRepositoryValidatingInterceptor(
			FhirContext fhirContext, DaoRegistry daoRegistry, RepositoryValidatingRuleBuilder ruleBuilder) {

		// --- original US Core example, kept for reference (inactive) ---
		// Customize the ruleBuilder here to have the rules you want! We will give a simple example
		// of enabling validation for all Patient resources
//		repositoryValidatingRuleBuilder
//				.forResourcesOfType("Patient")
//				.requireAtLeastProfile("http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient")
//				.and()
//				.requireValidationToDeclaredProfiles();

		IFhirResourceDao structureDefinitionDao = daoRegistry.getResourceDao("StructureDefinition");
		IBundleProvider bundle = structureDefinitionDao.search(new SearchParameterMap()
				.setLoadSynchronous(true)
				.add(StructureDefinition.SP_KIND, new TokenParam("resource")));

		Map<String, List<StructureDefinition>> phCoreProfiles = bundle.getResources(0, bundle.size()).stream()
				.map(StructureDefinition.class::cast)
				.filter(sd -> sd.getUrl() != null && sd.getUrl().startsWith(PH_CORE_PROFILE_PREFIX))
				.collect(Collectors.groupingBy(StructureDefinition::getType));

		phCoreProfiles.forEach((resourceType, definitions) -> {
			Set<String> profileUrls = definitions.stream()
					.map(StructureDefinition::getUrl)
					.collect(Collectors.toSet());
			List<StructureDefinition> baselineProfiles = definitions.stream()
					.filter(sd -> !profileUrls.contains(sd.getBaseDefinition()))
					.toList();

			if (baselineProfiles.size() != 1) {
				throw new IllegalStateException("Expected exactly one root PH Core profile for " + resourceType
						+ " but found " + baselineProfiles.size() + ". Configure a baseline explicitly for this resource type.");
			}

			// Default to the PH Core baseline when no profile is declared.
			ruleBuilder
					.forResourcesOfType(resourceType)
					.impliedProfileIfNotExplicit(baselineProfiles.get(0).getUrl());
		});

		List<IRepositoryValidatingRule> rules = ruleBuilder.build();
		return new RepositoryValidatingInterceptor(fhirContext, rules);
	}
}
