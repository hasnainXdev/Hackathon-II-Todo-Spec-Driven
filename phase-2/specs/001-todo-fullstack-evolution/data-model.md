# Data Model: Todo Full-Stack Evolution

## Entities

### Task
Represents a user's todo item with the following fields:
- id: UUID (primary key)
- title: String (required, 1-200 characters)
- description: String (optional, nullable)
- completion_status: Boolean (default: false)
- user_id: UUID (foreign key to User)
- created_at: DateTime (auto-generated)
- updated_at: DateTime (auto-generated, updates on change)

### User
Represents an authenticated user (managed externally by Better Auth system):
- id: UUID (primary key, from Better Auth)
- email: String (unique, from Better Auth)
- created_at: DateTime (from Better Auth)
- updated_at: DateTime (from Better Auth)

### UserPreference
Represents user-specific preferences stored in the database:
- id: UUID (primary key)
- user_id: UUID (foreign key to User)
- preference_key: String (e.g., "theme", "notifications_enabled", "language")
- preference_value: String (the value for the preference key)
- created_at: DateTime (auto-generated)
- updated_at: DateTime (auto-generated, updates on change)

## Relationships
- Task belongs to one User (many-to-one)
- User can have many Tasks (one-to-many)
- User can have many UserPreferences (one-to-many)
- UserPreference belongs to one User (many-to-one)

## Validation Rules
- Task.title: Required, length 1-200 characters
- Task.description: Optional, max length 1000 characters
- Task.completion_status: Boolean, defaults to false
- Task.user_id: Required, must reference existing User
- UserPreference.user_id: Required, must reference existing User
- UserPreference.preference_key: Required, non-empty string
- UserPreference.preference_value: Required, non-empty string

## State Transitions
- Task: Incomplete (completion_status=false) ↔ Complete (completion_status=true)