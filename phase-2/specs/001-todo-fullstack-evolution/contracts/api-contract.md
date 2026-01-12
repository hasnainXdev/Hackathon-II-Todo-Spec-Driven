# API Contract: Todo Application

**Date**: 2026-01-08  
**Feature**: Todo Full-Stack Evolution  
**Branch**: 001-todo-fullstack-evolution

## Overview

This document defines the API contract for the Todo application, specifying endpoints, request/response formats, authentication requirements, and error handling.

## Base URL

All API endpoints are rooted at:
`https://api.yourdomain.com/api` (production)
`http://localhost:8000/api` (development)

## Authentication

All endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <JWT_TOKEN>
```

## Common Response Format

All API responses follow this structure:
```json
{
  "success": true,
  "data": { /* endpoint-specific data */ },
  "message": "Optional message"
}
```

For errors:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  }
}
```

## Endpoints

### 1. List User Tasks
**Endpoint**: `GET /tasks`

**Description**: Retrieve the authenticated user's task list

**Authentication Required**: Yes

**Query Parameters**:
- `limit` (optional): Number of tasks to return (default: 20, max: 100)
- `offset` (optional): Number of tasks to skip (for pagination)

**Request Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Successful Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "user_id": "user-uuid-string",
      "title": "Sample task",
      "description": "Task description",
      "completed": false,
      "created_at": "2023-01-01T10:00:00Z",
      "updated_at": "2023-01-01T10:00:00Z"
    }
  ],
  "message": "Tasks retrieved successfully"
}
```

**Possible Error Responses**:
- 401: Unauthorized (invalid/missing JWT)
- 500: Internal Server Error

### 2. Create Task
**Endpoint**: `POST /tasks`

**Description**: Create a new task for the authenticated user

**Authentication Required**: Yes

**Request Headers**:
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "New task title",
  "description": "Optional task description"
}
```

**Validation**:
- `title` is required and must be 1-200 characters
- `description` is optional and must be ≤ 1000 characters

**Successful Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "id": 1,
    "user_id": "user-uuid-string",
    "title": "New task title",
    "description": "Optional task description",
    "completed": false,
    "created_at": "2023-01-01T10:00:00Z",
    "updated_at": "2023-01-01T10:00:00Z"
  },
  "message": "Task created successfully"
}
```

**Possible Error Responses**:
- 400: Bad Request (validation errors)
- 401: Unauthorized (invalid/missing JWT)
- 422: Unprocessable Entity (semantic validation errors)
- 500: Internal Server Error

### 3. Get Specific Task
**Endpoint**: `GET /tasks/{id}`

**Description**: Retrieve a specific task by ID

**Authentication Required**: Yes

**Path Parameter**:
- `id` (required): Task ID

**Request Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Successful Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": 1,
    "user_id": "user-uuid-string",
    "title": "Sample task",
    "description": "Task description",
    "completed": false,
    "created_at": "2023-01-01T10:00:00Z",
    "updated_at": "2023-01-01T10:00:00Z"
  },
  "message": "Task retrieved successfully"
}
```

**Possible Error Responses**:
- 401: Unauthorized (invalid/missing JWT)
- 403: Forbidden (attempting to access another user's task)
- 404: Not Found (task doesn't exist)
- 500: Internal Server Error

### 4. Update Task
**Endpoint**: `PUT /tasks/{id}`

**Description**: Update an existing task

**Authentication Required**: Yes

**Path Parameter**:
- `id` (required): Task ID

**Request Headers**:
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Updated task title",
  "description": "Updated task description"
}
```

**Validation**:
- `title` is required and must be 1-200 characters
- `description` is optional and must be ≤ 1000 characters

**Successful Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": 1,
    "user_id": "user-uuid-string",
    "title": "Updated task title",
    "description": "Updated task description",
    "completed": false,
    "created_at": "2023-01-01T10:00:00Z",
    "updated_at": "2023-01-01T11:00:00Z"
  },
  "message": "Task updated successfully"
}
```

**Possible Error Responses**:
- 400: Bad Request (validation errors)
- 401: Unauthorized (invalid/missing JWT)
- 403: Forbidden (attempting to access another user's task)
- 404: Not Found (task doesn't exist)
- 422: Unprocessable Entity (semantic validation errors)
- 500: Internal Server Error

### 5. Delete Task
**Endpoint**: `DELETE /tasks/{id}`

**Description**: Delete a specific task

**Authentication Required**: Yes

**Path Parameter**:
- `id` (required): Task ID

**Request Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Successful Response** (204 No Content):
```
(Empty response body)
```

**Possible Error Responses**:
- 401: Unauthorized (invalid/missing JWT)
- 403: Forbidden (attempting to access another user's task)
- 404: Not Found (task doesn't exist)
- 500: Internal Server Error

### 6. Toggle Task Completion
**Endpoint**: `PATCH /tasks/{id}/complete`

**Description**: Toggle the completion status of a task

**Authentication Required**: Yes

**Path Parameter**:
- `id` (required): Task ID

**Request Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Request Body**: (Empty)

**Successful Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": 1,
    "user_id": "user-uuid-string",
    "title": "Sample task",
    "description": "Task description",
    "completed": true,
    "created_at": "2023-01-01T10:00:00Z",
    "updated_at": "2023-01-01T11:00:00Z"
  },
  "message": "Task completion status updated"
}
```

**Possible Error Responses**:
- 401: Unauthorized (invalid/missing JWT)
- 403: Forbidden (attempting to access another user's task)
- 404: Not Found (task doesn't exist)
- 500: Internal Server Error

## Error Codes

| Code | Description |
|------|-------------|
| AUTH_001 | Invalid JWT token |
| AUTH_002 | Expired JWT token |
| AUTH_003 | Missing JWT token |
| VALIDATION_001 | Invalid request parameters |
| VALIDATION_002 | Validation failed for request body |
| RESOURCE_001 | Resource not found |
| RESOURCE_002 | Insufficient permissions for resource |
| SYSTEM_001 | Internal server error |

## Rate Limiting

All authenticated endpoints are subject to rate limiting:
- 1000 requests per hour per user
- 100 requests per minute per user for write operations

## Versioning

This API contract follows the versioning scheme defined in the project specifications. Future changes will be introduced with appropriate versioning to maintain backward compatibility where possible.