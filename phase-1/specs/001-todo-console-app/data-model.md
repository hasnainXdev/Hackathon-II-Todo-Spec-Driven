# Data Model: Todo Console Application

## Task Entity

### Fields
- **id** (int): Unique identifier for the task, auto-incremented
- **title** (str): Title of the task (required)
- **description** (str): Description of the task (optional, can be empty)
- **completed** (bool): Completion status of the task (default: False)

### Relationships
- No relationships with other entities (standalone entity)

### Validation Rules
- `id` must be a positive integer
- `title` must not be empty or None
- `title` and `description` must be strings
- `completed` must be a boolean value

### State Transitions
- `completed` field can transition from `False` to `True` (mark complete)
- `completed` field can transition from `True` to `False` (mark incomplete)

## Example Task Representation
```python
{
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, bread, eggs, fruits",
    "completed": False
}
```

## In-Memory Storage Structure
Tasks will be stored in a dictionary with the task ID as the key and the task object as the value:
```python
{
    1: {
        "id": 1,
        "title": "Buy groceries",
        "description": "Milk, bread, eggs, fruits",
        "completed": False
    },
    2: {
        "id": 2,
        "title": "Walk the dog",
        "description": "",
        "completed": True
    }
}
```