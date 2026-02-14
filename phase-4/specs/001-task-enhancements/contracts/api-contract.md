# API Contract: Task Management Enhancements

## 1. Overview
This document defines the API contracts for the enhanced task management system with priorities, tags, search, filter, and sort functionality.

## 2. Base URL
```
https://api.example.com
```

## 3. Common Headers
```
Content-Type: application/json
Authorization: Bearer {token}
```

## 4. API Endpoints

### 4.1 Create Task
**Endpoint**: `POST /tasks`

**Description**: Creates a new task with optional priority and tags.

**Request Body**:
```json
{
  "title": "String, required",
  "description": "String, optional",
  "priority": "Enum('LOW', 'MEDIUM', 'HIGH'), optional, default: 'MEDIUM'",
  "tags": "Array of strings, optional, max 10, 2-20 chars each"
}
```

**Response Codes**:
- 201: Created - Task successfully created
- 400: Bad Request - Invalid input data
- 401: Unauthorized - Missing or invalid token

**Success Response (201)**:
```json
{
  "id": "String, unique identifier",
  "title": "String",
  "description": "String",
  "priority": "Enum('LOW', 'MEDIUM', 'HIGH')",
  "tags": "Array of strings",
  "completed": "Boolean, default: false",
  "createdAt": "ISO 8601 datetime string",
  "updatedAt": "ISO 8601 datetime string"
}
```

**Error Response (400)**:
```json
{
  "error": true,
  "message": "String, error description"
}
```

### 4.2 Get All Tasks
**Endpoint**: `GET /tasks`

**Description**: Retrieves all tasks with optional search, filter, and sort parameters.

**Query Parameters**:
- `search`: String, optional, max 100 chars - Search across title, description, tags
- `priority`: Enum('LOW', 'MEDIUM', 'HIGH'), optional - Filter by priority
- `tag`: String, optional - Filter by tag
- `completed`: Boolean, optional - Filter by completion status
- `sort`: Enum('createdAt', 'updatedAt', 'priority', 'title'), optional, default: 'createdAt' - Sort field
- `order`: Enum('asc', 'desc'), optional, default: 'desc' - Sort order

**Response Codes**:
- 200: OK - Successfully retrieved tasks
- 400: Bad Request - Invalid query parameters
- 401: Unauthorized - Missing or invalid token

**Success Response (200)**:
```json
{
  "tasks": [
    {
      "id": "String",
      "title": "String",
      "description": "String",
      "priority": "Enum('LOW', 'MEDIUM', 'HIGH')",
      "tags": "Array of strings",
      "completed": "Boolean",
      "createdAt": "ISO 8601 datetime string",
      "updatedAt": "ISO 8601 datetime string"
    }
  ]
}
```

### 4.3 Get Task by ID
**Endpoint**: `GET /tasks/{id}`

**Description**: Retrieves a specific task by its ID.

**Path Parameters**:
- `id`: String, required - Unique identifier of the task

**Response Codes**:
- 200: OK - Task found
- 401: Unauthorized - Missing or invalid token
- 404: Not Found - Task with given ID not found

**Success Response (200)**:
```json
{
  "id": "String",
  "title": "String",
  "description": "String",
  "priority": "Enum('LOW', 'MEDIUM', 'HIGH')",
  "tags": "Array of strings",
  "completed": "Boolean",
  "createdAt": "ISO 8601 datetime string",
  "updatedAt": "ISO 8601 datetime string"
}
```

### 4.4 Update Task
**Endpoint**: `PATCH /tasks/{id}`

**Description**: Updates an existing task with new information.

**Path Parameters**:
- `id`: String, required - Unique identifier of the task

**Request Body** (all fields optional):
```json
{
  "title": "String, optional",
  "description": "String, optional",
  "priority": "Enum('LOW', 'MEDIUM', 'HIGH'), optional",
  "tags": "Array of strings, optional",
  "completed": "Boolean, optional"
}
```

**Response Codes**:
- 200: OK - Task successfully updated
- 400: Bad Request - Invalid input data
- 401: Unauthorized - Missing or invalid token
- 404: Not Found - Task with given ID not found

**Success Response (200)**:
```json
{
  "id": "String",
  "title": "String",
  "description": "String",
  "priority": "Enum('LOW', 'MEDIUM', 'HIGH')",
  "tags": "Array of strings",
  "completed": "Boolean",
  "createdAt": "ISO 8601 datetime string",
  "updatedAt": "ISO 8601 datetime string"
}
```

### 4.5 Delete Task
**Endpoint**: `DELETE /tasks/{id}`

**Description**: Deletes a specific task by its ID.

**Path Parameters**:
- `id`: String, required - Unique identifier of the task

**Response Codes**:
- 204: No Content - Task successfully deleted
- 401: Unauthorized - Missing or invalid token
- 404: Not Found - Task with given ID not found

### 4.6 Get All Tags
**Endpoint**: `GET /tags`

**Description**: Retrieves all unique tags across all tasks.

**Response Codes**:
- 200: OK - Successfully retrieved tags
- 401: Unauthorized - Missing or invalid token

**Success Response (200)**:
```json
{
  "tags": ["String", "String", "..."]
}
```

## 5. Validation Rules

### 5.1 Task Creation/Update Validation
- `title`: Required, non-empty string
- `priority`: Must be one of "LOW", "MEDIUM", "HIGH"; case-sensitive
- `tags`: Max 10 elements, each 2-20 characters, will be trimmed and lowercased
- `completed`: Must be boolean value

### 5.2 Query Parameter Validation
- `search`: Max 100 characters
- `priority`: Must be one of "LOW", "MEDIUM", "HIGH"
- `sort`: Must be one of "createdAt", "updatedAt", "priority", "title"
- `order`: Must be one of "asc", "desc"

## 6. Error Handling

### 6.1 Common Error Format
```json
{
  "error": true,
  "message": "Human-readable error message",
  "code": "Machine-readable error code (optional)"
}
```

### 6.2 Specific Error Messages
- Invalid priority: "Invalid priority value. Must be one of: LOW, MEDIUM, HIGH."
- Invalid tags: "Each tag must be 2-20 characters long. Maximum 10 tags allowed."
- Invalid sort field: "Invalid sort field. Must be one of: createdAt, updatedAt, priority, title."
- Invalid order: "Invalid order value. Must be asc or desc."

## 7. Performance Requirements
- API response time should be under 300ms for local development
- Combined search/filter/sort operations should scale appropriately with data size