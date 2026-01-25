# MCP Tools Contract: AI-Powered Todo Chatbot

## Overview
This document defines the Model Context Protocol (MCP) tools that will be exposed to the AI agent for interacting with the todo management system.

## Tool Definitions

### 1. create_task
**Description**: Creates a new task for the user.

**Parameters**:
```json
{
  "title": {
    "type": "string",
    "description": "Title of the task",
    "maxLength": 200
  },
  "description": {
    "type": "string",
    "description": "Detailed description of the task",
    "maxLength": 1000,
    "optional": true
  }
}
```

**Returns**:
```json
{
  "success": {
    "type": "boolean",
    "description": "Whether the operation was successful"
  },
  "task": {
    "type": "object",
    "description": "The created task object",
    "properties": {
      "id": {"type": "string"},
      "title": {"type": "string"},
      "description": {"type": "string"},
      "completed": {"type": "boolean"},
      "created_at": {"type": "string", "format": "date-time"}
    }
  },
  "message": {
    "type": "string",
    "description": "Human-readable message about the operation"
  }
}
```

**Example Usage**:
- User: "Add a task to buy groceries"
- Tool Call: `create_task(title="buy groceries")`
- Result: `{ "success": true, "task": {...}, "message": "Task 'buy groceries' has been added to your list." }`

---

### 2. get_tasks
**Description**: Retrieves all tasks for the current user.

**Parameters**: None

**Returns**:
```json
{
  "success": {
    "type": "boolean",
    "description": "Whether the operation was successful"
  },
  "tasks": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "completed": {"type": "boolean"},
        "created_at": {"type": "string", "format": "date-time"}
      }
    }
  },
  "message": {
    "type": "string",
    "description": "Human-readable message about the operation"
  }
}
```

**Example Usage**:
- User: "Show me my tasks"
- Tool Call: `get_tasks()`
- Result: `{ "success": true, "tasks": [...], "message": "Here are your current tasks:" }`

---

### 3. update_task
**Description**: Updates an existing task.

**Parameters**:
```json
{
  "task_id": {
    "type": "string",
    "description": "ID of the task to update"
  },
  "title": {
    "type": "string",
    "description": "New title for the task",
    "optional": true,
    "maxLength": 200
  },
  "description": {
    "type": "string",
    "description": "New description for the task",
    "optional": true,
    "maxLength": 1000
  },
  "completed": {
    "type": "boolean",
    "description": "New completion status for the task",
    "optional": true
  }
}
```

**Returns**:
```json
{
  "success": {
    "type": "boolean",
    "description": "Whether the operation was successful"
  },
  "task": {
    "type": "object",
    "description": "The updated task object",
    "properties": {
      "id": {"type": "string"},
      "title": {"type": "string"},
      "description": {"type": "string"},
      "completed": {"type": "boolean"},
      "updated_at": {"type": "string", "format": "date-time"}
    }
  },
  "message": {
    "type": "string",
    "description": "Human-readable message about the operation"
  }
}
```

**Example Usage**:
- User: "Update the grocery task to include organic items"
- Tool Call: `update_task(task_id="task-123", description="Include organic items")`
- Result: `{ "success": true, "task": {...}, "message": "The grocery task has been updated to include organic items." }`

---

### 4. complete_task
**Description**: Marks a task as completed.

**Parameters**:
```json
{
  "task_id": {
    "type": "string",
    "description": "ID of the task to mark as completed"
  }
}
```

**Returns**:
```json
{
  "success": {
    "type": "boolean",
    "description": "Whether the operation was successful"
  },
  "task": {
    "type": "object",
    "description": "The completed task object",
    "properties": {
      "id": {"type": "string"},
      "title": {"type": "string"},
      "completed": {"type": "boolean"},
      "updated_at": {"type": "string", "format": "date-time"}
    }
  },
  "message": {
    "type": "string",
    "description": "Human-readable message about the operation"
  }
}
```

**Example Usage**:
- User: "Mark task 3 as complete"
- Tool Call: `complete_task(task_id="task-456")`
- Result: `{ "success": true, "task": {...}, "message": "Task 'walk the dog' has been marked as complete." }`

---

### 5. delete_task
**Description**: Deletes a task.

**Parameters**:
```json
{
  "task_id": {
    "type": "string",
    "description": "ID of the task to delete"
  }
}
```

**Returns**:
```json
{
  "success": {
    "type": "boolean",
    "description": "Whether the operation was successful"
  },
  "message": {
    "type": "string",
    "description": "Human-readable message about the operation"
  }
}
```

**Example Usage**:
- User: "Delete the meeting task"
- Tool Call: `delete_task(task_id="task-789")`
- Result: `{ "success": true, "message": "The meeting task has been deleted." }`

---

## Error Handling

All tools follow a consistent error response format:

```json
{
  "success": false,
  "error": {
    "type": "string",
    "description": "Type of error that occurred"
  },
  "message": {
    "type": "string",
    "description": "Human-readable error message"
  }
}
```

Common error types:
- `invalid_input`: Parameters provided were invalid
- `not_found`: Requested resource (task, etc.) does not exist
- `unauthorized`: User does not have permission to perform the action
- `server_error`: Internal server error occurred

## Authentication
All MCP tools require a valid user context to be established before execution. The MCP server will validate user authentication and ensure that operations only affect resources owned by the authenticated user.