# Quickstart Guide: Task Management Enhancements

## Overview

This guide provides instructions for implementing the task management enhancements including priorities, tags, search, filter, and sort functionality.

## Prerequisites

- Backend application with existing task management functionality
- Database access and migration capabilities
- Understanding of the current task API and data model
- Development environment with necessary tools installed

## Step 1: Update Data Model

### 1.1 Modify Task Entity

Add the following fields to your Task entity/model:

- `priority` (Enum: LOW, MEDIUM, HIGH, default: MEDIUM)
- `tags` (Array of strings, max 10 elements, each 2-20 characters)

### 1.2 Database Migration

Create and run a database migration to add these fields to your tasks table:

```sql
-- Example for PostgreSQL
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) DEFAULT 'MEDIUM' NOT NULL;
ALTER TABLE tasks ADD COLUMN tags TEXT[] DEFAULT '{}';

-- Update existing tasks with default values
UPDATE tasks SET priority = 'MEDIUM' WHERE priority IS NULL;
UPDATE tasks SET tags = '{}' WHERE tags IS NULL;
```

## Step 2: Update API Endpoints

### 2.1 Enhanced GET /tasks Endpoint

Modify the existing GET /tasks endpoint to support query parameters:

- `search`: Search term to match against title, description, and tags
- `priority`: Filter by priority level (LOW, MEDIUM, HIGH)
- `tag`: Filter by specific tag
- `completed`: Filter by completion status (true/false)
- `sort`: Field to sort by (createdAt, updatedAt, priority, title)
- `order`: Sort order (asc, desc)

### 2.2 Update POST /tasks Endpoint

Modify the POST /tasks endpoint to accept priority and tags in the request body:

```json
{
  "title": "New task",
  "description": "Task description",
  "priority": "HIGH",
  "tags": ["work", "important"],
  "completed": false
}
```

### 2.3 Update PATCH /tasks/{id} Endpoint

Modify the PATCH /tasks/{id} endpoint to allow updating priority and tags:

```json
{
  "priority": "MEDIUM",
  "tags": ["personal", "low-priority"]
}
```

## Step 3: Implement Business Logic

### 3.1 Validation

Implement validation for the new fields:

- Priority must be one of: LOW, MEDIUM, HIGH
- Tags array must not exceed 10 elements
- Each tag must be 2-20 characters in length
- Each tag must match the pattern: ^[a-z0-9_-]+$
- Tags should be automatically converted to lowercase

### 3.2 Search Implementation

Implement search functionality that looks across title, description, and tags:

```javascript
// Example pseudo-code
const searchTerm = req.query.search.toLowerCase();
const matchingTasks = tasks.filter(task => 
  task.title.toLowerCase().includes(searchTerm) ||
  task.description.toLowerCase().includes(searchTerm) ||
  task.tags.some(tag => tag.includes(searchTerm))
);
```

### 3.3 Filter Implementation

Implement filtering by priority, tags, and completion status:

```javascript
// Example pseudo-code
let filteredTasks = tasks;

if (req.query.priority) {
  filteredTasks = filteredTasks.filter(task => task.priority === req.query.priority);
}

if (req.query.tag) {
  filteredTasks = filteredTasks.filter(task => task.tags.includes(req.query.tag));
}

if (req.query.completed !== undefined) {
  const completed = req.query.completed === 'true';
  filteredTasks = filteredTasks.filter(task => task.completed === completed);
}
```

### 3.4 Sort Implementation

Implement sorting by different fields:

```javascript
// Example pseudo-code
const sortBy = req.query.sort || 'createdAt';
const sortOrder = req.query.order === 'asc' ? 1 : -1;

filteredTasks.sort((a, b) => {
  if (sortBy === 'priority') {
    // Define priority order: LOW < MEDIUM < HIGH
    const priorityOrder = { LOW: 0, MEDIUM: 1, HIGH: 2 };
    return (priorityOrder[a.priority] - priorityOrder[b.priority]) * sortOrder;
  } else {
    // Sort by other fields (createdAt, updatedAt, title)
    if (a[sortBy] < b[sortBy]) return -1 * sortOrder;
    if (a[sortBy] > b[sortBy]) return 1 * sortOrder;
    return 0;
  }
});
```

## Step 4: Handle Edge Cases

Implement handling for the following edge cases:

- Empty search string → return all tasks
- Non-existent tag filter → return empty list
- Invalid sort field → fallback to default sorting (createdAt)
- Duplicate tag inputs → automatically deduplicate
- More than 10 tags → reject extra tags with error
- Invalid enum values → return 400 error

## Step 5: Testing

### 5.1 Unit Tests

Write unit tests for:

- Creating tasks with priority and tags
- Updating task priority and tags
- Search functionality
- Filter by priority
- Filter by tag
- Filter by completion status
- Sort by different fields
- Validation of inputs
- Edge case handling

### 5.2 Integration Tests

Write integration tests for:

- Combined search, filter, and sort operations
- End-to-end task creation with new fields
- Migration of existing tasks
- Performance testing with 100+ tasks

## Step 6: Performance Optimization

### 6.1 Database Indexes

Add database indexes to support efficient querying:

- Index on `priority` field
- Index on `completed` field
- Index on `createdAt` and `updatedAt` fields
- Full-text index on `title` and `description` fields
- Index on `tags` array elements (if supported by your database)

### 6.2 Query Optimization

Optimize queries to ensure performance:

- Use LIMIT and OFFSET for pagination
- Implement efficient search algorithms
- Consider caching for frequently accessed data
- Monitor query performance after implementation

## Step 7: Frontend Integration

### 7.1 Update UI Components

Update frontend components to:

- Display task priority with visual indicators
- Show and edit task tags
- Implement search input field
- Add filter controls for priority, tags, and completion status
- Add sort controls for different fields

### 7.2 API Integration

Update frontend API calls to:

- Send priority and tags when creating/updating tasks
- Use query parameters for search, filter, and sort
- Handle new response fields appropriately

## Step 8: Deployment

### 8.1 Database Migration

Deploy the database migration to production before deploying the application code.

### 8.2 Application Deployment

Deploy the application code with the new features.

### 8.3 Verification

Verify that:

- All existing functionality continues to work
- New features work as expected
- Performance meets requirements
- Error handling works correctly

## Troubleshooting

### Common Issues

1. **Validation errors**: Ensure all validation rules are properly implemented
2. **Performance issues**: Check that database indexes are properly set up
3. **Migration problems**: Test database migrations in a staging environment first
4. **API compatibility**: Ensure backward compatibility with existing clients

### Useful Queries

```sql
-- Check for tasks with invalid priorities
SELECT * FROM tasks WHERE priority NOT IN ('LOW', 'MEDIUM', 'HIGH');

-- Check for tasks with too many tags
SELECT * FROM tasks WHERE ARRAY_LENGTH(tags, 1) > 10;

-- Check for tags with invalid length
SELECT * FROM tasks WHERE EXISTS (
  SELECT 1 FROM UNNEST(tags) AS tag 
  WHERE LENGTH(tag) < 2 OR LENGTH(tag) > 20
);
```