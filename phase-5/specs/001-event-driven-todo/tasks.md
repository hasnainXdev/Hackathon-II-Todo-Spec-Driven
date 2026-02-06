# Implementation Tasks: Event-Driven Todo Chatbot System

**Feature**: Event-Driven Todo Chatbot System  
**Branch**: `001-event-driven-todo`  
**Generated**: 2026-02-05  
**Input**: Design artifacts from `/specs/001-event-driven-todo/`

## Overview

This document contains the implementation tasks for the event-driven Todo Chatbot system. The tasks are organized in dependency order to enable incremental development and verification. Building upon the AI-powered todo chatbot from Phase 3 and the Kubernetes deployment strategies from Phase 4, this system transforms the monolithic architecture into a fully event-driven system with Kafka, Dapr, and Kubernetes.

## Implementation Strategy

- **MVP First**: Complete User Story 1 (core task management) before advancing to other stories
- **Incremental Delivery**: Each phase delivers independently testable functionality
- **Event-Driven Focus**: Every task emphasizes event publishing and consumption
- **Architecture Depth**: Prioritize distributed systems concepts over UI completeness

## Dependencies

User stories are ordered by priority (P1, P2, P3). Story 1 must be completed before Story 2, and so on. Services can be developed in parallel once foundational components are in place.

## Parallel Execution Examples

- Service development can happen in parallel after foundational setup
- Contract-first API development can occur alongside consumer service implementation
- Infrastructure components can be developed in parallel with application services

---

## Phase 1: Setup

Setup tasks for initializing the project structure and foundational components.

### Phase Goal

Establish the repository structure, define required skills, and set up governance rules for the event-driven architecture.

### Independent Test Criteria

Repository structure exists and all foundational files are in place.

### Tasks

- [ ] T001 Create repository structure per implementation plan in /services /infrastructure /dapr /.github
- [ ] T002 Create skills.md defining mandatory skills: Primary Agent, Reviewer Agent, Kafka (native), Event-driven systems, Kubernetes, Dapr (state + secrets only)
- [ ] T003 Create agent rules file (AGENTS.md or CLAUDE.md) with "No manual coding" rule, Native Kafka requirement, Dapr usage boundaries
- [ ] T004 Set up project configuration files (requirements.txt, Dockerfiles, etc.)

---

## Phase 2: Foundational Components

Foundational tasks that block all user stories. These must be completed before starting user story work.

### Phase Goal

Deploy and configure the foundational infrastructure: Kafka, PostgreSQL, Dapr components, and the core data models.

### Independent Test Criteria

Kafka is running with required topics, PostgreSQL is accessible with task table, Dapr state and secret stores are configured.

### Tasks

- [ ] T010 [P] Deploy Kafka on Minikube with Strimzi operator
- [ ] T011 [P] Create Kafka topics: task-events, reminders, task-updates
- [ ] T012 [P] Provision PostgreSQL database (local) with task table/schema
- [ ] T013 [P] Configure Dapr state store component for cached task state and conversation state
- [ ] T014 [P] Configure Dapr secrets store for DB and Kafka credentials
- [ ] T015 [P] Implement Task model in services/chat-api/src/models/task.py based on data-model.md
- [ ] T016 [P] Implement Event model in services/chat-api/src/models/event.py based on data-model.md
- [ ] T017 [P] Implement User model in services/chat-api/src/models/user.py based on data-model.md
- [ ] T018 [P] Implement Conversation model in services/chat-api/src/models/conversation.py based on data-model.md
- [ ] T019 [P] Implement Message model in services/chat-api/src/models/message.py based on data-model.md
- [ ] T020 [P] Set up Kafka producer utilities in services/chat-api/src/kafka/producer.py
- [ ] T021 [P] Set up Kafka consumer utilities in services/chat-api/src/kafka/consumer.py
- [ ] T022 [P] Create database connection and initialization utilities in services/chat-api/src/database/
- [ ] T022.1 [P] Implement handling for Kafka temporary unavailability in services/chat-api/src/kafka/
- [ ] T022.2 [P] Implement optimistic locking for concurrent task updates in services/chat-api/src/models/task.py
- [ ] T022.3 [P] Implement database retry logic for temporary unavailability in services/chat-api/src/database/

---

## Phase 3: User Story 1 - Create and Manage Tasks via Chat (P1)

### Story Goal

Enable users to interact with the system through a chat interface to create, update, complete, and delete tasks. Each task can have a title, description, priority, tags, due date, and optional recurrence rule.

### Independent Test Criteria

Can be fully tested by sending chat commands to create, update, complete, and delete tasks, verifying that these operations complete successfully and persist in the system.

### Tasks

- [ ] T023 [P] [US1] Scaffold Chat API service with basic FastAPI structure in services/chat-api/
- [ ] T024 [P] [US1] Implement health check endpoint in services/chat-api/src/api/health.py
- [ ] T025 [P] [US1] Implement task creation endpoint in services/chat-api/src/api/tasks.py
- [ ] T026 [P] [US1] Implement task retrieval endpoint in services/chat-api/src/api/tasks.py
- [ ] T027 [P] [US1] Implement task update endpoint in services/chat-api/src/api/tasks.py
- [ ] T028 [P] [US1] Implement task completion endpoint in services/chat-api/src/api/tasks.py
- [ ] T029 [P] [US1] Implement task deletion endpoint in services/chat-api/src/api/tasks.py
- [ ] T030 [P] [US1] Implement chat command processing endpoint in services/chat-api/src/api/chat.py
- [ ] T031 [P] [US1] Implement task service layer in services/chat-api/src/services/task_service.py
- [ ] T032 [P] [US1] Implement chat command parsing logic in services/chat-api/src/chat/command_parser.py
- [ ] T033 [P] [US1] Implement Kafka event publishing for TASK_CREATED in services/chat-api/src/kafka/publishers.py
- [ ] T034 [P] [US1] Implement Kafka event publishing for TASK_UPDATED in services/chat-api/src/kafka/publishers.py
- [ ] T035 [P] [US1] Implement Kafka event publishing for TASK_COMPLETED in services/chat-api/src/kafka/publishers.py
- [ ] T036 [P] [US1] Implement Kafka event publishing for TASK_DELETED in services/chat-api/src/kafka/publishers.py
- [ ] T036.1 [P] [US1] Implement retry mechanism for Kafka publishing in services/chat-api/src/kafka/publishers.py
- [ ] T036.2 [P] [US1] Implement circuit breaker pattern for database connections in services/chat-api/src/database/
- [ ] T036.3 [P] [US1] Implement graceful degradation when Kafka is unavailable in services/chat-api/src/api/tasks.py
- [ ] T037 [P] [US1] Create Dockerfile for Chat API service in services/chat-api/Dockerfile
- [ ] T038 [P] [US1] Create Kubernetes deployment for Chat API in infrastructure/k8s/base/chat-api-deployment.yaml
- [ ] T039 [P] [US1] Create Kubernetes service for Chat API in infrastructure/k8s/base/chat-api-service.yaml
- [ ] T040 [P] [US1] Implement basic tests for task operations in services/chat-api/tests/

---

## Phase 4: User Story 2 - Set Up Recurring Tasks and Reminders (P2)

### Story Goal

Enable users to configure tasks to recur (daily, weekly, etc.) and set due dates with reminders that trigger asynchronously without blocking the user's workflow.

### Independent Test Criteria

Can be fully tested by creating a recurring task, completing it once, and verifying that the next occurrence is automatically created by the background service.

### Tasks

- [ ] T041 [P] [US2] Define Reminder Event schema in specs/001-event-driven-todo/contracts/
- [ ] T042 [P] [US2] Define Task Update Event schema in specs/001-event-driven-todo/contracts/
- [ ] T042.1 [P] [US2] Implement Reminder Event schema definition in specs/001-event-driven-todo/contracts/reminder-event-schema.json
- [ ] T042.2 [P] [US2] Implement Task Update Event schema definition in specs/001-event-driven-todo/contracts/task-update-event-schema.json
- [ ] T043 [P] [US2] Scaffold Recurring Task service in services/recurring-task-service/
- [ ] T044 [P] [US2] Implement Kafka consumer for task completion events in services/recurring-task-service/src/consumers/
- [ ] T045 [P] [US2] Implement recurring task processing logic in services/recurring-task-service/src/processors/
- [ ] T046 [P] [US2] Implement next recurring task generation in services/recurring-task-service/src/processors/
- [ ] T047 [P] [US2] Implement Kafka event publishing for new recurring tasks in services/recurring-task-service/src/kafka/
- [ ] T048 [P] [US2] Create Dockerfile for Recurring Task service in services/recurring-task-service/Dockerfile
- [ ] T049 [P] [US2] Create Kubernetes deployment for Recurring Task service in infrastructure/k8s/base/recurring-task-deployment.yaml
- [ ] T050 [P] [US2] Scaffold Notification service in services/notification-service/
- [ ] T051 [P] [US2] Implement Kafka consumer for reminder events in services/notification-service/src/consumers/
- [ ] T052 [P] [US2] Implement notification delivery logic in services/notification-service/src/notifiers/
- [ ] T053 [P] [US2] Implement retry logic for transient failures in services/notification-service/src/notifiers/
- [ ] T054 [P] [US2] Create Dockerfile for Notification service in services/notification-service/Dockerfile
- [ ] T055 [P] [US2] Create Kubernetes deployment for Notification service in infrastructure/k8s/base/notification-deployment.yaml
- [ ] T056 [P] [US2] Enhance task creation to publish reminder events when due date is set in services/chat-api/src/kafka/publishers.py
- [ ] T057 [P] [US2] Implement tests for recurring task functionality in services/recurring-task-service/tests/
- [ ] T058 [P] [US2] Implement tests for notification functionality in services/notification-service/tests/

---

## Phase 5: User Story 3 - Search, Filter, and Sort Tasks (P3)

### Story Goal

Allow users to search their tasks by content, filter by priority/tags/completion state, and sort by date or priority.

### Independent Test Criteria

Can be fully tested by creating multiple tasks with different attributes and verifying that search, filter, and sort operations return the correct results.

### Tasks

- [ ] T059 [P] [US3] Implement search endpoint in services/chat-api/src/api/tasks.py
- [ ] T060 [P] [US3] Implement filtering logic in services/chat-api/src/services/task_service.py
- [ ] T061 [P] [US3] Implement sorting logic in services/chat-api/src/services/task_service.py
- [ ] T062 [P] [US3] Add search, filter, and sort parameters to GET /api/v1/tasks in services/chat-api/src/api/tasks.py
- [ ] T063 [P] [US3] Implement database indexing strategy for efficient queries in services/chat-api/src/database/
- [ ] T064 [P] [US3] Implement tests for search, filter, and sort functionality in services/chat-api/tests/
- [ ] T065 [P] [US3] Update API documentation to reflect new search/filter/sort capabilities

---

## Phase 6: User Story 4 - View Task History and Audit Trail (P3)

### Story Goal

Enable users to view the complete history of changes to their tasks, with all operations captured as immutable events.

### Independent Test Criteria

Can be fully tested by performing various operations on a task and then requesting its history to verify all changes are recorded.

### Tasks

- [ ] T066 [P] [US4] Scaffold Audit service in services/audit-service/
- [ ] T067 [P] [US4] Implement Kafka consumer for task events in services/audit-service/src/consumers/
- [ ] T068 [P] [US4] Implement audit log storage in services/audit-service/src/storage/
- [ ] T069 [P] [US4] Implement immutable audit record persistence in services/audit-service/src/storage/
- [ ] T070 [P] [US4] Create Dockerfile for Audit service in services/audit-service/Dockerfile
- [ ] T071 [P] [US4] Create Kubernetes deployment for Audit service in infrastructure/k8s/base/audit-deployment.yaml
- [ ] T072 [P] [US4] Implement task history endpoint in services/chat-api/src/api/tasks.py that retrieves task history from audit service
- [ ] T072.1 [P] [US4] Implement user-facing task history retrieval in services/chat-api/src/services/task_history_service.py
- [ ] T073 [P] [US4] Implement audit service client in services/chat-api/src/services/audit_client.py
- [ ] T074 [P] [US4] Implement WebSocket/real-time sync service in services/sync-service/
- [ ] T075 [P] [US4] Implement consumer for task-update events in services/sync-service/src/consumers/
- [ ] T076 [P] [US4] Implement broadcast updates to connected clients in services/sync-service/src/websocket/
- [ ] T077 [P] [US4] Create Dockerfile for Sync service in services/sync-service/Dockerfile
- [ ] T078 [P] [US4] Create Kubernetes deployment for Sync service in infrastructure/k8s/base/sync-deployment.yaml
- [ ] T079 [P] [US4] Implement tests for audit functionality in services/audit-service/tests/
- [ ] T080 [P] [US4] Implement tests for real-time sync functionality in services/sync-service/tests/

---

## Phase 7: Local End-to-End Verification

### Phase Goal

Verify the complete event-driven flow from task creation to completion, recurrence, and reminders in the local environment.

### Independent Test Criteria

Logs show full async chain with no synchronous coupling between services.

### Tasks

- [ ] T081 Verify full event flow (local): Create task → completion → recurrence → reminder
- [ ] T082 Test all services in local Kubernetes (Minikube) environment
- [ ] T083 Validate Kafka event publishing and consumption across all services
- [ ] T084 Verify audit trail captures all task operations
- [ ] T085 Test real-time synchronization between clients
- [ ] T086 Document the verification process and expected outcomes
- [ ] T086.1 Verify SC-001: Task creation timing (<5 seconds) in performance tests
- [ ] T086.2 Verify SC-002: Recurring task timing (<10 seconds) in integration tests
- [ ] T086.3 Verify SC-003: Reminder delivery timing (<1 minute) in notification tests
- [ ] T086.4 Verify SC-004: Audit trail completeness in audit service tests
- [ ] T086.5 Verify SC-005: System availability during service failures in chaos tests
- [ ] T086.6 Verify SC-006: Real-time sync timing (<3 seconds) in WebSocket tests
- [ ] T086.7 Verify SC-008: Event-driven behavior verification via logs in verification scripts

---

## Phase 8: Cloud Deployment

### Phase Goal

Deploy the complete event-driven system to a cloud Kubernetes environment.

### Independent Test Criteria

All services run successfully in cloud environment with proper async behavior verified via logs.

### Tasks

- [ ] T087 Provision cloud Kubernetes cluster (Oracle OKE, AKS, or GKE)
- [ ] T088 Deploy Kafka (cloud) - either self-hosted or managed
- [ ] T089 Deploy all services to cloud Kubernetes
- [ ] T090 Configure cloud-specific infrastructure components
- [ ] T091 Cloud end-to-end verification of event-driven flows
- [ ] T092 Performance testing in cloud environment
- [ ] T093 Security hardening for cloud deployment

---

## Phase 9: CI/CD Pipeline

### Phase Goal

Set up automated build, test, and deployment pipeline for the event-driven system.

### Independent Test Criteria

Pipeline runs successfully, builds container images, pushes to registry, and deploys manifests.

### Tasks

- [ ] T094 Create GitHub Actions pipeline for build and test
- [ ] T095 Set up container image building and pushing to registry
- [ ] T096 Implement deployment to Kubernetes clusters
- [ ] T097 Add security scanning to pipeline
- [ ] T098 Set up automated testing in pipeline

---

## Phase 10: Polish & Cross-Cutting Concerns

### Phase Goal

Final touches, documentation, and verification that the system meets all success criteria.

### Independent Test Criteria

System is ready for evaluation and meets all defined success criteria.

### Tasks

- [ ] T099 Create Judge Verification Guide with step-by-step instructions
- [ ] T100 Implement demo script for 90-second verification
- [ ] T101 Write comprehensive documentation for the event-driven architecture
- [ ] T102 Perform final testing to ensure all success criteria are met
- [ ] T103 Clean up code, remove debug statements, optimize performance
- [ ] T104 Prepare final presentation materials
- [ ] T105 Verify all constitutional requirements are met (Kafka, Dapr for state/secrets only, etc.)