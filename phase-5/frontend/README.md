# Event-Driven Todo Chatbot - Frontend

This is the frontend for the event-driven todo chatbot system. It provides a user interface to interact with the backend services that communicate via Kafka events.

## Features

- **Task Management**: Create, read, update, and delete tasks
- **Natural Language Processing**: Interact with the system using natural language commands
- **Real-time Updates**: Receive live updates via WebSocket connections
- **Task History**: View the complete history of changes to your tasks
- **Search & Filter**: Search and filter tasks by various criteria

## Architecture

The frontend communicates with multiple backend services:

- **Chat API**: Handles user requests and chat commands, publishes events to Kafka
- **Notification Service**: Processes reminder events from Kafka
- **Recurring Task Service**: Handles recurring task logic based on completion events
- **Audit Service**: Maintains immutable audit trail of all operations
- **Sync Service**: Provides real-time updates via WebSockets

## Setup

1. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env.local
   ```
   
   Update the `.env.local` file with your configuration:
   - `NEXT_PUBLIC_FASTAPI_API_URL`: URL of the Chat API backend service
   - `NEXT_PUBLIC_BASE_URL`: Base URL of the frontend
   - `BETTER_AUTH_URL`: URL of the authentication service
   - `BETTER_AUTH_SECRET`: Secret for authentication

3. Run the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   ```

## Environment Variables

- `NEXT_PUBLIC_FASTAPI_API_URL`: The URL of the backend API (e.g., `http://localhost:8000/api/v1`)
- `NEXT_PUBLIC_BASE_URL`: The base URL of the frontend application
- `BETTER_AUTH_URL`: The URL of the authentication service
- `BETTER_AUTH_SECRET`: The secret key for authentication
- `NEXT_PUBLIC_BETTER_AUTH_URL`: The public URL for authentication API
- `NEXT_PUBLIC_CHATKIT_API_URL`: The URL for chat functionality

## Key Components

- `TaskList`: Displays tasks with real-time updates via WebSocket
- `TaskForm`: Form for creating new tasks
- `ChatInterface`: Natural language interface for task management
- `websocket-service`: Custom hook for real-time updates from the sync service

## Event-Driven Architecture

The frontend interacts with the backend services in an event-driven manner:

1. User performs an action (e.g., creates a task)
2. Frontend sends request to Chat API
3. Chat API publishes event to Kafka (e.g., TASK_CREATED)
4. Various services consume the event and perform their specific business logic
5. Sync service broadcasts updates to connected clients via WebSocket
6. Frontend receives real-time updates and updates the UI

## API Client

The `event-driven-api-client.ts` file contains functions to interact with the backend services:

- `createTask`: Creates a new task
- `getTasks`: Retrieves tasks with optional filtering and sorting
- `getTaskById`: Retrieves a specific task
- `updateTask`: Updates a task
- `deleteTask`: Deletes a task
- `completeTask`: Marks a task as complete
- `getTaskHistory`: Retrieves the history of events for a task
- `processChatCommand`: Processes natural language commands

## WebSocket Integration

The frontend uses WebSockets to receive real-time updates from the sync service:

- Task creation, updates, and deletions are reflected immediately
- Reminder notifications are displayed in real-time
- Connection status is shown in the UI

## Running with Docker

To run the frontend in a container:

```bash
# Build the image
docker build -t todo-frontend .

# Run the container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_FASTAPI_API_URL=http://backend:8000/api/v1 \
  -e NEXT_PUBLIC_BASE_URL=http://localhost:3000 \
  -e BETTER_AUTH_URL=http://auth:3000 \
  -e BETTER_AUTH_SECRET=your-secret-key \
  todo-frontend
```

## Learn More

To learn more about the event-driven architecture and the backend services, check out the backend documentation.