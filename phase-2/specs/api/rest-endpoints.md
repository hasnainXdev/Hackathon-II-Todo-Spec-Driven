# REST API Specification: Todo Application Endpoints

**Feature Branch**: `001-todo-fullstack-evolution`
**Created**: 2026-01-08
**Status**: Draft
**Input**: Define API endpoints, authentication requirements, request/response schemas, and status codes for the todo application.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Listing and Creation (Priority: P1)

As an authenticated user, I need to list my tasks and create new ones, so that I can view my current todos and add new items to track.

**Why this priority**: These are the most commonly used operations that form the foundation of the todo application.

**Independent Test**: Can be fully tested by authenticating, creating tasks, and verifying they appear in the task list while ensuring other users' tasks don't appear.

**Acceptance Scenarios**:

1. **Given** a user is authenticated, **When** they make a GET request to /api/tasks, **Then** they receive their task list in JSON format with 200 OK status
2. **Given** a user is authenticated, **When** they make a POST request to /api/tasks with valid task data, **Then** a new task is created and returned with 201 Created status
3. **Given** a user has no tasks, **When** they make a GET request to /api/tasks, **Then** they receive an empty array with 200 OK status

---

### User Story 2 - Individual Task Operations (Priority: P2)

As an authenticated user, I need to retrieve, update, and delete individual tasks, so that I can manage specific items in my todo list.

**Why this priority**: Essential for detailed task management allowing users to modify or remove specific tasks.

**Independent Test**: Can be tested by creating a task, retrieving it, updating its details, and finally deleting it, verifying each operation works correctly.

**Acceptance Scenarios**:

1. **Given** a user owns a task, **When** they make a GET request to /api/tasks/{id}, **Then** they receive the task details with 200 OK status
2. **Given** a user owns a task, **When** they make a PUT request to /api/tasks/{id} with updated data, **Then** the task is updated and returned with 200 OK status
3. **Given** a user owns a task, **When** they make a DELETE request to /api/tasks/{id}, **Then** the task is deleted with 204 No Content status

---

### User Story 3 - Task Completion Management (Priority: P3)

As an authenticated user, I need to toggle the completion status of my tasks, so that I can track which items I've completed.

**Why this priority**: Core functionality for task management that allows users to mark progress.

**Independent Test**: Can be tested by creating a task, toggling its completion status multiple times, and verifying the status updates correctly.

**Acceptance Scenarios**:

1. **Given** a user owns an incomplete task, **When** they make a PATCH request to /api/tasks/{id}/complete, **Then** the task becomes complete with 200 OK status
2. **Given** a user owns a complete task, **When** they make a PATCH request to /api/tasks/{id}/complete, **Then** the task becomes incomplete with 200 OK status
3. **Given** a user attempts to access a non-existent task, **When** they make any request to /api/tasks/{id}, **Then** they receive 404 Not Found status

### Edge Cases

- What happens when a user sends malformed JSON in a POST/PUT request?
- How does the API handle requests with valid JWTs but for tasks owned by different users?
- What occurs when a user attempts to create a task with an empty title?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: All API endpoints MUST require Authorization header with Bearer JWT token
- **FR-002**: GET /api/tasks endpoint MUST return user's tasks filtered by their user ID
- **FR-003**: POST /api/tasks endpoint MUST create a new task associated with the authenticated user
- **FR-004**: GET /api/tasks/{id} endpoint MUST return only tasks owned by the authenticated user
- **FR-005**: PUT /api/tasks/{id} endpoint MUST update only tasks owned by the authenticated user
- **FR-006**: DELETE /api/tasks/{id} endpoint MUST delete only tasks owned by the authenticated user
- **FR-007**: PATCH /api/tasks/{id}/complete endpoint MUST toggle completion status of user-owned tasks
- **FR-008**: All endpoints MUST return appropriate HTTP status codes as specified
- **FR-009**: All endpoints MUST return JSON responses with consistent structure
- **FR-010**: API MUST handle authentication and authorization before processing requests

### Base API Path

- **BAP-001**: All API endpoints MUST be prefixed with `/api/`
- **BAP-002**: API versioning is not required for this implementation
- **BAP-003**: All endpoints MUST use HTTPS in production environments

### Authentication Requirement for Every Endpoint

- **ARE-001**: Every endpoint MUST validate the presence of Authorization header
- **ARE-002**: Every endpoint MUST validate the JWT token format (Bearer <token>)
- **ARE-003**: Every endpoint MUST verify the JWT token signature using shared secret
- **ARE-004**: Every endpoint MUST check that the JWT token has not expired
- **ARE-005**: Invalid authentication MUST result in 401 Unauthorized response
- **ARE-006**: Missing authentication MUST result in 401 Unauthorized response

### Request/Response Schemas

#### Common Response Structure
```json
{
  "success": true,
  "data": { /* endpoint-specific data */ },
  "message": "Optional message"
}
```

#### Task Object Schema
```json
{
  "id": "integer",
  "user_id": "string",
  "title": "string (1-200 characters)",
  "description": "string (optional)",
  "completed": "boolean",
  "created_at": "ISO 8601 datetime string",
  "updated_at": "ISO 8601 datetime string"
}
```

#### GET /api/tasks Response Schema
```json
{
  "success": true,
  "data": [
    { /* Array of task objects */ }
  ],
  "message": "Optional message"
}
```

#### POST /api/tasks Request Schema
```json
{
  "title": "string (required, 1-200 characters)",
  "description": "string (optional)"
}
```

#### POST /api/tasks Response Schema
```json
{
  "success": true,
  "data": { /* Single task object */ },
  "message": "Task created successfully"
}
```

#### PUT /api/tasks/{id} Request Schema
```json
{
  "title": "string (required, 1-200 characters)",
  "description": "string (optional)"
}
```

#### PUT /api/tasks/{id} Response Schema
```json
{
  "success": true,
  "data": { /* Updated task object */ },
  "message": "Task updated successfully"
}
```

#### PATCH /api/tasks/{id}/complete Response Schema
```json
{
  "success": true,
  "data": { /* Updated task object */ },
  "message": "Task completion status updated"
}
```

### HTTP Status Codes

- **HSC-001**: 200 OK - Successful GET, PUT, PATCH requests
- **HSC-002**: 201 Created - Successful POST request
- **HSC-003**: 204 No Content - Successful DELETE request
- **HSC-004**: 400 Bad Request - Invalid request data or format
- **HSC-005**: 401 Unauthorized - Missing or invalid authentication
- **HSC-006**: 403 Forbidden - Valid authentication but insufficient permissions
- **HSC-007**: 404 Not Found - Requested resource does not exist
- **HSC-008**: 422 Unprocessable Entity - Valid request format but semantic errors
- **HSC-009**: 500 Internal Server Error - Unexpected server error

### Filtering Behavior (user-scoped only)

- **FBU-001**: GET /api/tasks MUST return only tasks belonging to authenticated user
- **FBU-002**: All individual task endpoints MUST verify task ownership before operations
- **FBU-003**: Requests for other users' tasks MUST result in 403 Forbidden or 404 Not Found
- **FBU-004**: No user should be able to access, modify, or delete another user's tasks
- **FBU-005**: Task creation MUST automatically associate the task with the authenticated user

### Required Endpoints

#### GET /api/tasks
- **Purpose**: Retrieve the authenticated user's task list
- **Authentication**: Required
- **Response**: Array of task objects
- **Status Codes**: 200, 401, 500

#### POST /api/tasks
- **Purpose**: Create a new task for the authenticated user
- **Authentication**: Required
- **Request Body**: Task data (title, description)
- **Response**: Created task object
- **Status Codes**: 201, 400, 401, 422, 500

#### GET /api/tasks/{id}
- **Purpose**: Retrieve a specific task by ID
- **Authentication**: Required
- **Parameters**: Task ID in URL path
- **Response**: Single task object
- **Status Codes**: 200, 401, 403, 404, 500

#### PUT /api/tasks/{id}
- **Purpose**: Update a specific task by ID
- **Authentication**: Required
- **Parameters**: Task ID in URL path
- **Request Body**: Updated task data
- **Response**: Updated task object
- **Status Codes**: 200, 400, 401, 403, 404, 422, 500

#### DELETE /api/tasks/{id}
- **Purpose**: Delete a specific task by ID
- **Authentication**: Required
- **Parameters**: Task ID in URL path
- **Response**: No content
- **Status Codes**: 204, 401, 403, 404, 500

#### PATCH /api/tasks/{id}/complete
- **Purpose**: Toggle the completion status of a specific task
- **Authentication**: Required
- **Parameters**: Task ID in URL path
- **Response**: Updated task object
- **Status Codes**: 200, 401, 403, 404, 500

### Key Entities *(include if feature involves data)*

- **Task**: Represents a user's todo item with id, title, description, completion status, user_id, created_at, updated_at
- **User**: Represents an authenticated user whose ID is used for task ownership verification
- **JWT Token**: Contains user identity used for authentication and authorization

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of API requests return the correct HTTP status code as specified
- **SC-002**: 100% of users can only access their own tasks, with zero cross-user data access
- **SC-003**: API endpoints respond within 2 seconds for 95% of requests under normal load
- **SC-004**: Authentication is enforced on 100% of endpoints with appropriate error responses
- **SC-005**: All API responses conform to the specified JSON schema 99% of the time