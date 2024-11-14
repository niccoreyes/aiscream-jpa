This project exists as a means to guide implementers to use the HAPI FHIR JPA Starter project as a vehicle to create reference implementations for testing FHIR IGs. This is [motivated by the need to have solid test coverage for all aspects FHIR IG development, including dynamic ones](https://gitlab.com/australian-e-health-research-centre/akkadakka/-/wikis/Motivation). The HAPI server, [deployed locally or in a container offers a good solution](https://gitlab.com/australian-e-health-research-centre/akkadakka/-/wikis/solution) to this challenge.

# Intended Use

This project is intended to support the Actors in IG development with their typical use cases.

## Actors

Below is the list of actors in the scope of IG development.

| Persona | Activity |
| --- | --- |
| Tracey (Trace)| Test-Kit Developer |
| Igor | IG Author |
| Sven | Server Vendor |
| Conny | Connectathon Participant |
| David (Davo) | DevOps |

## Use Cases

We assume that there will be a number of use cases. For the moment, we want to cover the following, which we believe all personas above will require:

* **Start the server:** Set up the server in different situations.
* **Identify the server:** Ensure that your browser or test is connected to the correct server version.
* **Test Custom Operations:** Check the expected functionality of an operation.
* **Test Narrative Generation:** Check the expected functionality of narrative generation.

# Setup and workflow

Below is what you need to use this project.

## Required / Know How

To carry out these steps, you will need to know how to install and use the following on your local operating system. We are using Eclipse and Ubuntu. Your mileage may vary. But not by much.

* Docker
* Java
* Java IDE
* Git

## Process

0. [define your issue, create your feature branch and MR](https://about.gitlab.com/blog/2020/03/05/what-is-gitlab-flow/)
1. check out the branch
2. activate maven in your IDE
3. build and test with Maven (sanity test)
4. test with your IDE (see detail description of developments below)
5. package as docker container
6. test container
7. push to CI
8. test container from CI repo
9. have someone review and merge the MR

# Contributing / Future Use Cases



There are a number of Use Cases that will be important in the future:

* David, testing the implementation with the server.
* Finding out what Conny is trying during a Connectathon.

# Naming

[Akkadakka](https://www.urbandictionary.com/define.php?term=Akka%20Dakka) puns on the name of [CSIRO's Sparked FHIR Incubator](https://sparked.csiro.au/). It marks it as a powerful, fun, but somewhat unrefined type of spark. It also plays at the prominent nature that [reference injection and inversion of control](https://en.wikipedia.org/wiki/Inversion_of_control) play in the HAPI container, which can make the approach to the HAPI codebase difficult.
