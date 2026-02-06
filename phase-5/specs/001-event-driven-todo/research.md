# Research Document: Event-Driven Todo Chatbot System

## Overview
This document captures research findings and resolves all "NEEDS CLARIFICATION" items from the technical context. It provides the technical decisions and rationale that will guide the implementation of the event-driven Todo Chatbot system. Building upon the AI-powered todo chatbot from Phase 3 and the Kubernetes deployment strategies from Phase 4, this research integrates event-driven architecture principles with real-world distributed systems using Kafka, Kubernetes, and Dapr.

## Technology Decisions

### 1. Language Selection: Python 3.11 and Go 1.21

**Decision**: Use Python 3.11 for most services and Go 1.21 for performance-critical components.

**Rationale**:
- Python 3.11 offers excellent ecosystem support for FastAPI, Kafka clients, and rapid development
- Go 1.21 provides superior performance for high-throughput services and low-latency requirements
- Both languages have strong Kubernetes and Dapr SDK support
- Builds upon the Python/FastAPI foundation established in Phase 3's AI-powered chatbot

**Alternatives considered**:
- Node.js: Considered but rejected due to potential performance limitations for high-throughput scenarios
- Java: More verbose, longer startup times which could impact container scaling
- Rust: Excellent performance but steeper learning curve and longer development time

### 2. Primary Dependencies

**Decision**: Use FastAPI, confluent-kafka-python, and Dapr SDK.

**Rationale**:
- FastAPI provides automatic API documentation, async support, and excellent developer experience (established in Phase 3)
- Confluent Kafka Python client is the industry standard with robust performance and reliability
- Dapr SDK simplifies distributed system challenges while maintaining loose coupling
- Leverages the FastAPI foundation from Phase 3's AI-powered todo chatbot

**Alternatives considered**:
- Flask vs FastAPI: FastAPI chosen for automatic OpenAPI generation and better async support
- aiokafka vs confluent-kafka: Confluent client chosen for better enterprise features and support
- Native Kubernetes API vs Dapr: Dapr chosen for simplified service-to-service communication and state management

### 3. Storage Solutions

**Decision**: PostgreSQL for primary data, Kafka for event streaming, Redis via Dapr for caching.

**Rationale**:
- PostgreSQL provides ACID compliance and complex query capabilities needed for task management (consistent with Phase 3's Neon Serverless PostgreSQL choice)
- Kafka serves as the event backbone ensuring reliable message delivery
- Redis via Dapr provides fast caching for frequently accessed data
- Builds upon the SQLModel and PostgreSQL foundation established in Phase 3

**Alternatives considered**:
- MongoDB vs PostgreSQL: PostgreSQL chosen for relational integrity requirements
- RabbitMQ vs Kafka: Kafka chosen for better scalability and event replay capabilities (required by Phase 5 constitution)
- Direct Redis access vs Dapr Redis: Dapr chosen to maintain consistency in infrastructure abstractions

### 4. Testing Framework

**Decision**: Use pytest for unit and integration tests, k6 for load testing.

**Rationale**:
- Pytest is the de facto standard for Python testing with excellent plugin ecosystem
- K6 provides modern, scriptable load testing with good metrics collection
- Consistent with Python-based testing approaches from Phase 3

**Alternatives considered**:
- unittest vs pytest: Pytest chosen for more concise syntax and better fixtures
- Locust vs k6: K6 chosen for better JavaScript-based scripting and metrics

### 5. Target Platform

**Decision**: Linux containers orchestrated by Kubernetes.

**Rationale**:
- Linux provides optimal container performance and compatibility
- Kubernetes offers industry-standard orchestration with scaling, networking, and service discovery
- Aligns with the requirement for deployment on both Minikube and cloud platforms (established in Phase 4)
- Builds upon the Kubernetes deployment strategies from Phase 4

### 6. Performance Goals

**Decision**: Handle 1000 concurrent users with <5 second event processing latency.

**Rationale**:
- Based on the success criteria in the specification (SC-001 to SC-008)
- Ensures responsive user experience while maintaining system stability
- Achievable with proper event-driven architecture and async processing
- Considers the performance requirements identified in Phase 3's AI processing pipeline

### 7. Constraints

**Decision**: <200ms p95 API response time, <10MB memory per service, fault-tolerant operation.

**Rationale**:
- 200ms p95 response time ensures perceived performance for users
- 10MB memory limit keeps costs reasonable and enables efficient scaling
- Fault tolerance is essential for an event-driven system where services operate independently
- Addresses the performance risks identified in Phase 3's research

### 8. Scale/Scope

**Decision**: Support 10k users, 1M tasks, 5 services with independent scaling.

**Rationale**:
- Based on realistic requirements for a demonstration system
- Allows for independent scaling of services based on their specific load patterns
- Enables proper testing of the event-driven architecture under load
- Considers the scalability risks identified in Phase 3's research

## Architecture Research

### Event-Driven Patterns

**Research Findings**:
- Event sourcing and CQRS patterns are well-suited for the requirements
- Saga pattern may be needed for complex operations spanning multiple services
- Circuit breaker pattern essential for resilience in distributed systems
- Builds upon the AI processing pipeline concept from Phase 3, transforming it into an event-driven architecture

**Implementation Approach**:
- Use Kafka topics for event sourcing
- Implement consumer groups for horizontal scaling of services
- Apply backpressure mechanisms to prevent system overload
- Transform the Phase 3 AI processing pipeline into an event-driven flow

### Kafka Deployment Options

**Research Findings**:
- Strimzi operator provides the most Kubernetes-native Kafka deployment
- Redpanda offers lower resource usage and faster startup times
- Managed solutions (Confluent Cloud, AWS MSK) simplify operations but may not satisfy "real Kafka" requirement
- Consistent with Phase 5's constitutional requirement for real Kafka usage

**Decision**: Use Strimzi for local Minikube deployment (building upon Phase 4's Minikube configuration), evaluate managed options for cloud based on cost and observability requirements.

### Dapr Usage Boundaries

**Research Findings**:
- Dapr state stores provide consistent interfaces across different storage backends
- Dapr secret stores centralize credential management
- Dapr pubsub components must be avoided per constitution requirements (critical distinction from Phase 3's MCP SDK)
- Dapr complements the PostgreSQL and Kafka architecture rather than replacing it

**Implementation Approach**:
- Use Dapr state stores for caching and temporary data
- Use Dapr secret stores for database credentials and API keys
- Maintain direct Kafka integration to comply with constitution
- Dapr handles state and secrets only, unlike Phase 3's MCP SDK which handled broader communication

## Deployment Research

### Local Development (Minikube)

**Research Findings**:
- Minikube provides a Kubernetes environment that closely mirrors cloud deployments
- Resource constraints require careful configuration for running all services
- Port forwarding and ingress controllers facilitate local testing
- Phase 4 established best practices for Minikube configuration

**Implementation Approach**:
- Use lightweight configurations for local development (based on Phase 4 recommendations)
- Implement health checks to ensure service readiness
- Create scripts for easy setup and teardown
- Leverage Phase 4's Minikube configuration strategies

### Cloud Deployment

**Research Findings**:
- Oracle OKE, AKS, and GKE all provide production-ready Kubernetes
- Each platform has specific considerations for Kafka deployment
- Network policies and security contexts need adjustment for cloud environments
- Phase 4 established foundational deployment strategies

**Decision**: Target Oracle OKE as recommended by the specification, with AKS/GKE as alternatives. Build upon Phase 4's deployment strategies.

## Security Considerations

**Research Findings**:
- Service mesh patterns enhance security in microservice architectures
- TLS encryption required for all inter-service communication
- Proper authentication and authorization patterns needed even though not in scope
- Phase 3's Better Auth implementation provides insights for user isolation

**Implementation Approach**:
- Use Dapr for secure secret management
- Implement mutual TLS for service-to-service communication
- Prepare for future security feature integration
- Apply user isolation principles similar to Phase 3's auth implementation

## Observability Research

**Research Findings**:
- Structured logging is essential for debugging distributed systems
- Distributed tracing would be beneficial but is out of scope per constitution
- Metrics collection should focus on business-relevant KPIs
- Phase 4 established monitoring and logging foundations

**Implementation Approach**:
- Implement structured JSON logging with correlation IDs
- Log all Kafka produce/consume operations for verification
- Use Kubernetes-native monitoring tools for infrastructure metrics
- Build upon Phase 4's monitoring and logging configurations

## Integration with Previous Phases

### From Phase 3 (AI-Powered Todo Chatbot)
- Leverage the FastAPI backend and SQLModel database layer
- Transform the OpenAI Agents SDK processing into event-driven Kafka flows
- Adapt the Better Auth authentication approach for user isolation
- Use the Neon Serverless PostgreSQL foundation (compatible with our PostgreSQL choice)

### From Phase 4 (Kubernetes Deployment)
- Apply the Minikube configuration strategies for local development
- Implement the internal service communication patterns
- Utilize the persistent storage implementation approaches
- Incorporate the security configuration best practices
- Build upon the monitoring and logging foundations

## Risks and Mitigations

### Performance Risks
- **Risk**: Event processing latency could exceed requirements
- **Mitigation**: Optimize Kafka configurations and implement caching via Dapr state stores

### Scalability Risks  
- **Risk**: Concurrent user load could overwhelm system components
- **Mitigation**: Use Kafka consumer groups for horizontal scaling and Neon's connection pooling features

### Event Consistency Risks
- **Risk**: Event ordering and delivery guarantees may be compromised
- **Mitigation**: Use Kafka partitioning strategies and idempotent consumer implementations

### Architecture Complexity Risks
- **Risk**: Event-driven architecture adds complexity compared to direct API calls
- **Mitigation**: Maintain clear event contracts and comprehensive logging for observability