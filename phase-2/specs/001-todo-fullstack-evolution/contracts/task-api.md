# Task Management API Contract

## Base URL
`https://api.todoapp.com/v1`

## Authentication
All endpoints require a valid JWT token in the Authorization header:
`Authorization: Bearer <JWT_TOKEN>`

## Endpoints

### 1. Create Task
- **Method**: `POST`
- **Path**: `/tasks`
- **Description**: Creates a new task for the authenticated user
- **Request Headers**:
  - `Authorization: Bearer <JWT_TOKEN>`
  - `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "title": "string (required, 1-200 characters)",
    "description": "string (optional)"
  }
  ```
- **Success Response** (201 Created):
  ```json
  {
    "id": "UUID",
    "title": "string",
    "description": "string",
    "completed": false,
    "user_id": "UUID",
    "created_at": "ISO 8601 datetime",
    "updated_at": "ISO 8601 datetime"
  }
  ```
- **Error Responses**:
  - 400: Invalid input (e.g., title too long/short)
  - 401: Unauthorized (invalid/expired JWT)
  - 422: Validation error

### 2. Get User's Tasks
- **Method**: `GET`
- **Path**: `/tasks`
- **Description**: Retrieves all tasks belonging to the authenticated user
- **Request Headers**:
  - `Authorization: Bearer <JWT_TOKEN>`
- **Success Response** (200 OK):
  ```json
  {
    "tasks": [
      {
        "id": "UUID",
        "title": "string",
        "description": "string",
        "completed": boolean,
        "user_id": "UUID",
        "created_at": "ISO 8601 datetime",
        "updated_at": "ISO 8601 datetime"
      }
    ]
  }
  ```
- **Error Responses**:
  - 401: Unauthorized (invalid/expired JWT)

### 3. Get Single Task
- **Method**: `GET`
- **Path**: `/tasks/{task_id}`
- **Description**: Retrieves a specific task by ID if it belongs to the authenticated user
- **Path Parameters**:
  - `task_id`: UUID of the task to retrieve
- **Request Headers**:
  - `Authorization: Bearer <JWT_TOKEN>`
- **Success Response** (200 OK):
  ```json
  {
    "id": "UUID",
    "title": "string",
    "description": "string",
    "completed": boolean,
    "user_id": "UUID",
    "created_at": "ISO 8601 datetime",
    "updated_at": "ISO 8601 datetime"
  }
  ```
- **Error Responses**:
  - 401: Unauthorized (invalid/expired JWT)
  - 403: Forbidden (task doesn't belong to user)
  - 404: Task not found

### 4. Update Task
- **Method**: `PUT`
- **Path**: `/tasks/{task_id}`
- **Description**: Updates an existing task if it belongs to the authenticated user
- **Path Parameters**:
  - `task_id`: UUID of the task to update
- **Request Headers**:
  - `Authorization: Bearer <JWT_TOKEN>`
  - `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "title": "string (1-200 characters)",
    "description": "string (optional)",
    "completed": boolean
  }
  ```
- **Success Response** (200 OK):
  ```json
  {
    "id": "UUID",
    "title": "string",
    "description": "string",
    "completed": boolean,
    "user_id": "UUID",
    "created_at": "ISO 8601 datetime",
    "updated_at": "ISO 8601 datetime"
  }
  ```
- **Error Responses**:
  - 400: Invalid input
  - 401: Unauthorized (invalid/expired JWT)
  - 403: Forbidden (task doesn't belong to user)
  - 404: Task not found
  - 422: Validation error

### 5. Toggle Task Completion
- **Method**: `PATCH`
- **Path**: `/tasks/{task_id}/toggle-completion`
- **Description**: Toggles the completion status of a task
- **Path Parameters**:
  - `task_id`: UUID of the task to update
- **Request Headers**:
  - `Authorization: Bearer <JWT_TOKEN>`
- **Success Response** (200 OK):
  ```json
  {
    "id": "UUID",
    "title": "string",
    "description": "string",
    "completed": boolean,
    "user_id": "UUID",
    "created_at": "ISO 8601 datetime",
    "updated_at": "ISO 8601 datetime"
  }
  ```
- **Error Responses**:
  - 401: Unauthorized (invalid/expired JWT)
  - 403: Forbidden (task doesn't belong to user)
  - 404: Task not found

### 6. Delete Task
- **Method**: `DELETE`
- **Path**: `/tasks/{task_id}`
- **Description**: Deletes a task if it belongs to the authenticated user
- **Path Parameters**:
  - `task_id`: UUID of the task to delete
- **Request Headers**:
  - `Authorization: Bearer <JWT_TOKEN>`
- **Success Response** (204 No Content)
- **Error Responses**:
  - 401: Unauthorized (invalid/expired JWT)
  - 403: Forbidden (task doesn't belong to user)
  - 404: Task not found

## Error Response Format
All error responses follow this format:
```json
{
  "detail": "Error message explaining what went wrong"
}
```

## Validation Rules
- Task titles must be between 1 and 200 characters
- All endpoints require valid JWT authentication
- Users can only access their own tasks
- Requests with invalid data return 422 status codes