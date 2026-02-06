# Data Model: Event-Driven Todo Chatbot System

## Overview
This document defines the data structures and relationships for the event-driven Todo Chatbot system. It outlines the core entities, their attributes, validation rules, and state transitions as derived from the feature specification. Building upon the data models established in Phase 3 (AI-Powered Todo Chatbot) and enhanced with the deployment considerations from Phase 4 (Kubernetes Deployment), this model integrates event-driven architecture principles with real-world distributed systems using Kafka, Kubernetes, and Dapr.

## Core Entities

### 1. Task

**Description**: Represents a user's to-do item that can be managed via chat commands. This extends the basic task model from Phase 3 with additional event-driven attributes.

**Attributes**:
- `id` (UUID): Unique identifier for the task
- `title` (String, required): Brief description of the task
- `description` (String, optional): Detailed explanation of the task
- `priority` (Enum: LOW, MEDIUM, HIGH, CRITICAL): Importance level of the task (enhanced from Phase 3)
- `tags` (Array<String>): User-defined categories for organizing tasks
- `due_date` (DateTime, optional): Deadline for task completion
- `completed` (Boolean): Status indicating if the task is completed
- `completed_at` (DateTime, optional): Timestamp when the task was completed
- `recurrence_rule` (String, optional): Rule defining how the task repeats (e.g., "daily", "weekly on Tuesday")
- `created_at` (DateTime): Timestamp when the task was created
- `updated_at` (DateTime): Timestamp when the task was last modified
- `user_id` (UUID): Identifier of the user who owns the task
- `last_event_id` (UUID, optional): Reference to the last event that modified this task (for event sourcing)
- `version` (Integer): Optimistic locking version for concurrent updates

**Validation Rules**:
- Title must be between 1 and 255 characters
- Priority must be one of the defined enum values
- Due date cannot be in the past when creating/updating
- Recurrence rule must follow standard cron-like syntax if provided
- Tags array must not exceed 10 items
- Version must be incremented on each update (for optimistic locking)

**State Transitions**:
- `CREATED` → `ACTIVE` (when task is initially saved)
- `ACTIVE` → `COMPLETED` (when user marks task as complete)
- `COMPLETED` → `RECURRING_CREATED_NEXT` (when recurring task generates next occurrence)
- `COMPLETED` → `ARCHIVED` (after some time period or user action)

### 2. Event

**Description**: Immutable record of a task operation that flows through the system via Kafka. This replaces the simple API request model from Phase 3 with a full event sourcing approach.

**Attributes**:
- `event_id` (UUID): Unique identifier for the event
- `event_type` (Enum: TASK_CREATED, TASK_UPDATED, TASK_COMPLETED, TASK_DELETED, RECURRING_TRIGGERED, REMINDER_DUE, TASK_ASSIGNED, TASK_PRIORITY_CHANGED): Type of operation
- `aggregate_id` (UUID): ID of the entity the event relates to (usually Task.id)
- `aggregate_type` (String): Type of aggregate (e.g., "Task", "User")
- `payload` (JSON Object): Data associated with the event, varies by event_type
- `timestamp` (DateTime): When the event occurred
- `user_context` (Object): Information about the user who initiated the action
- `correlation_id` (UUID): Links related events together (from the same user command)
- `causation_id` (UUID): References the event that caused this event
- `version` (Integer): Version of the event schema
- `source_service` (String): Name of the service that generated the event

**Validation Rules**:
- Event type must be one of the defined enum values
- Payload must conform to the schema for the specific event type
- Timestamp must be current or recent (with tolerance for clock skew)
- Correlation ID should link related events in a workflow
- Causation ID must reference an existing event if provided

**State Transitions**:
- `CREATED` → `PUBLISHED_TO_KAFKA` → `PROCESSED_BY_CONSUMERS` → `ARCHIVED`

### 3. User

**Description**: Entity representing a person interacting with the system via chat commands. Enhanced from Phase 3 with event-driven attributes.

**Attributes**:
- `user_id` (UUID): Unique identifier for the user
- `username` (String): Display name for the user
- `email` (String): Email address for the user (from Phase 3's auth system)
- `preferences` (Object): User-specific settings for the application
- `created_at` (DateTime): When the user account was created
- `last_active` (DateTime): When the user was last seen
- `timezone` (String): User's timezone for scheduling (important for reminders)

**Validation Rules**:
- Username must be unique and between 3 and 50 characters
- Email must be valid and unique
- Preferences object must conform to predefined schema
- Timezone must be a valid IANA timezone identifier

### 4. Service

**Description**: Represents an independent component that consumes events and performs specific business logic. This replaces the more monolithic service approach from Phase 3.

**Attributes**:
- `service_id` (String): Unique identifier for the service
- `service_name` (String): Human-readable name of the service
- `description` (String): Brief explanation of the service's purpose
- `consumes_topics` (Array<String>): List of Kafka topics the service subscribes to
- `produces_topics` (Array<String>): List of Kafka topics the service publishes to
- `status` (Enum: HEALTHY, DEGRADED, UNHEALTHY, OFFLINE): Current operational status
- `last_heartbeat` (DateTime): Timestamp of last health check
- `partition_assignment` (Array<Integer>): Kafka partitions this instance is responsible for

**Validation Rules**:
- Service ID must be unique across all services
- Topic names must follow the naming convention defined in the architecture
- Status must be one of the defined enum values

### 5. Conversation (from Phase 3 Integration)

**Description**: Represents a chat conversation thread between a user and the AI assistant. Carries forward the chat functionality from Phase 3 into the event-driven architecture.

**Attributes**:
- `conversation_id` (UUID): Unique identifier for the conversation
- `user_id` (UUID): Reference to the user participating in the conversation
- `title` (String): Auto-generated title for the conversation
- `created_at` (DateTime): When the conversation was started
- `updated_at` (DateTime): When the conversation was last updated
- `status` (Enum: ACTIVE, ARCHIVED): Current status of the conversation

**Validation Rules**:
- User ID must reference an existing user
- Status must be one of the defined enum values

### 6. Message (from Phase 3 Integration)

**Description**: Represents a single message in a conversation. Part of the chat interface carried forward from Phase 3.

**Attributes**:
- `message_id` (UUID): Unique identifier for the message
- `conversation_id` (UUID): Reference to the conversation this message belongs to
- `sender_type` (Enum: USER, SYSTEM, ASSISTANT): Who sent the message
- `sender_id` (UUID): Reference to the sender (user or system)
- `content` (String): The actual message content
- `created_at` (DateTime): When the message was sent
- `related_task_id` (UUID, optional): Reference to a task this message relates to

**Validation Rules**:
- Sender type must be one of the defined enum values
- Content must not be empty
- Related task ID must reference an existing task if provided

## Relationships

### Task Relationships
- A `User` can own many `Task`s (one-to-many)
- A `Task` belongs to one `User` (many-to-one)
- A `Task` can generate many `Event`s (one-to-many)
- An `Event` relates to one `Task` (many-to-one)
- A `Message` can relate to zero or one `Task`s (many-to-zero-or-one)

### Event Relationships
- An `Event` is produced by one `Service` (many-to-one)
- An `Event` can trigger processing in many `Service`s (many-to-many via Kafka topics)
- An `Event` causally connects to zero or one other `Event`s (many-to-zero-or-one)

### Conversation Relationships
- A `User` can have many `Conversation`s (one-to-many)
- A `Conversation` belongs to one `User` (many-to-one)
- A `Conversation` can have many `Message`s (one-to-many)
- A `Message` belongs to one `Conversation` (many-to-one)

## Data Lifecycle

### Task Lifecycle
1. User creates a task via chat command (Phase 3's chat interface)
2. Chat API validates and persists the task
3. TASK_CREATED event is published to Kafka
4. Downstream services consume the event and perform side effects
5. Task is updated as needed based on user actions
6. Corresponding events are published for each update
7. When completed, TASK_COMPLETED event is published
8. If recurring, Recurring Task Service creates next occurrence
9. Audit Service records all changes to the task history

### Event Lifecycle
1. An operation occurs in a service (e.g., task creation from chat command)
2. An event is constructed with appropriate payload
3. Event is published to the relevant Kafka topic
4. One or more consumers subscribe to the topic
5. Consumers process the event and perform their specific business logic
6. Consumers may publish additional events as needed
7. Events are retained in Kafka for replay and audit purposes

### Conversation Lifecycle
1. User initiates a conversation via the chat interface (from Phase 3)
2. Conversation is created and persisted
3. User sends a message to the chatbot
4. Message is stored and triggers AI processing event
5. AI processes the message and responds
6. Response is stored as a message in the conversation
7. If the message creates/modifies a task, events are generated (Phase 5 enhancement)

## Data Integrity

### Consistency Models
- Strong consistency for task state within the primary database
- Eventual consistency for derived data across services
- At-least-once delivery for Kafka events
- Event sourcing ensures complete audit trail

### Backup and Recovery
- Primary task data backed up regularly (following Phase 4's persistent storage implementation)
- Kafka logs serve as backup for event history
- Point-in-time recovery capabilities for primary database
- Conversation and message data backed up separately for chat functionality

## Performance Considerations

### Indexing Strategy
- Index on `user_id` for efficient user-specific queries
- Index on `due_date` for efficient reminder processing
- Composite index on `(user_id, completed, priority)` for common filtering operations
- Index on `conversation_id` for efficient conversation retrieval
- Index on `timestamp` for event querying

### Partitioning Strategy
- Kafka topics partitioned by user_id to ensure ordering within user contexts
- Database tables partitioned by creation date for efficient archival
- Conversation messages partitioned by conversation_id for efficient retrieval

## Schema Evolution

### Versioning Approach
- Event schemas versioned to support backward compatibility
- Database migrations managed through versioned scripts (following Phase 3's SQLModel approach)
- Consumer services designed to handle multiple event versions gracefully
- Backward-compatible changes only (no breaking changes to existing events)

## Integration with Previous Phases

### From Phase 3 (AI-Powered Todo Chatbot)
- Task model extended with event-driven attributes
- Conversation and Message entities carried forward for chat interface
- User model enhanced with timezone for scheduling
- Authentication and user isolation principles maintained
- SQLModel-based database schema preserved

### From Phase 4 (Kubernetes Deployment)
- Data model optimized for containerized deployment
- Health check and status attributes added to services
- Partition assignment attributes for Kafka consumers
- Persistent storage considerations integrated
- Scalability attributes added to support horizontal scaling