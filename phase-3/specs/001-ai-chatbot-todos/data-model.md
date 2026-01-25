# Data Model: AI-Powered Todo Chatbot

## Overview
This document defines the data models for the AI-powered todo chatbot, including entities, relationships, and validation rules based on the feature requirements.

## Entity Models

### 1. User
Represents the application user with authentication information.

```python
class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(sa_column=Column("email", String, unique=True, index=True, nullable=False))
    name: str = Field(sa_column=Column("name", String, nullable=False))
    password_hash: Optional[str] = Field(default=None, sa_column=Column("password_hash", String))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column("created_at", DateTime(timezone=True)))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column("updated_at", DateTime(timezone=True)))
    
    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user")
    conversations: List["Conversation"] = Relationship(back_populates="user")
    messages: List["Message"] = Relationship(back_populates="user")
```

**Validation Rules**:
- Email must be a valid email address
- Email must be unique
- Name cannot be empty

### 2. Task
Represents a user's todo task with status and metadata.

```python
class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    due_date: Optional[datetime] = Field(default=None)
    priority: str = Field(default="medium", sa_column=Column("priority", String, default="medium"))  # low, medium, high

class Task(TaskBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column("created_at", DateTime(timezone=True)))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column("updated_at", DateTime(timezone=True)))
    
    # Relationships
    user: User = Relationship(back_populates="tasks")
    messages: List["Message"] = Relationship(back_populates="task")
```

**Validation Rules**:
- Title is required and must be 1-255 characters
- Description is optional, max 1000 characters
- Priority must be one of: "low", "medium", "high"
- Due date must be in the future if provided

### 3. Conversation
Represents a conversation session between user and AI chatbot.

```python
class Conversation(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    title: str = Field(default="New Conversation", max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column("created_at", DateTime(timezone=True)))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column("updated_at", DateTime(timezone=True)))
    
    # Relationships
    user: User = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")
```

**Validation Rules**:
- User ID is required
- Title defaults to "New Conversation" if not provided
- Title max length is 255 characters

### 4. Message
Represents a message in a conversation, either from user or AI assistant.

```python
class Message(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    conversation_id: UUID = Field(foreign_key="conversation.id", nullable=False)
    task_id: Optional[UUID] = Field(default=None, foreign_key="task.id")
    role: str = Field(sa_column=Column("role", String, nullable=False))  # "user" or "assistant"
    content: str = Field(sa_column=Column("content", Text, nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column("created_at", DateTime(timezone=True)))
    
    # Relationships
    user: User = Relationship(back_populates="messages")
    conversation: Conversation = Relationship(back_populates="messages")
    task: Optional[Task] = Relationship(back_populates="messages")
```

**Validation Rules**:
- Role must be either "user" or "assistant"
- Content is required
- User and conversation IDs are required

## State Transitions

### Task State Transitions
- `active` → `completed`: When user marks task as complete
- `completed` → `active`: When user reopens completed task
- `active` → `deleted`: When user deletes task (soft delete)

### Message State Transitions
- `created` → `processed`: When AI processes user message
- `processed` → `responded`: When AI generates response

## Database Indexes

### Primary Indexes
- User.id (UUID, Primary Key)
- Task.id (UUID, Primary Key)
- Conversation.id (UUID, Primary Key)
- Message.id (UUID, Primary Key)

### Secondary Indexes
- User.email (Unique, Indexed)
- Task.user_id (Foreign Key, Indexed)
- Conversation.user_id (Foreign Key, Indexed)
- Message.conversation_id (Foreign Key, Indexed)
- Message.user_id (Foreign Key, Indexed)
- Message.task_id (Foreign Key, Indexed)
- Task.created_at (Indexed)
- Message.created_at (Indexed)

## Relationships

### One-to-Many Relationships
- User → Tasks (One user has many tasks)
- User → Conversations (One user has many conversations)
- User → Messages (One user has many messages)
- Conversation → Messages (One conversation has many messages)
- Task → Messages (One task associated with many messages)

### Many-to-One Relationships
- Tasks → User (Many tasks belong to one user)
- Conversations → User (Many conversations belong to one user)
- Messages → User (Many messages belong to one user)
- Messages → Conversation (Many messages belong to one conversation)
- Messages → Task (Many messages may reference one task)

## Constraints

### Data Integrity
- Foreign key constraints ensure referential integrity
- Unique constraint on user email
- Non-null constraints on required fields

### Business Logic
- Users can only access their own tasks and conversations
- Messages must belong to an existing conversation
- Tasks must belong to an existing user