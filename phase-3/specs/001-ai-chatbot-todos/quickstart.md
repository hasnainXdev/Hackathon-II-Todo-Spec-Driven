# Quickstart Guide: AI-Powered Todo Chatbot

## Overview
This guide provides step-by-step instructions to set up and run the AI-powered todo chatbot locally. The application uses OpenAI ChatKit for the frontend, Python FastAPI for the backend, and integrates with various services for AI processing and authentication.

## Prerequisites

Before getting started, ensure you have the following installed:

- Python 3.11+
- Node.js 18+ and npm/yarn
- Git
- Docker (optional, for local database)
- An OpenAI API key

## Environment Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Navigate to the phase-2 directory (which contains the existing foundation):
   ```bash
   cd phase-2
   ```

3. Set up the backend environment:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Set up the frontend environment:
   ```bash
   cd ../frontend
   npm install
   ```

## Configuration

1. Create a `.env` file in the backend directory with the following variables:
   ```env
   DATABASE_URL="postgresql://username:password@localhost:5432/todo_chatbot"
   OPENAI_API_KEY="your-openai-api-key"
   SECRET_KEY="your-secret-key-for-authentication"
   BETTER_AUTH_SECRET="your-better-auth-secret"
   NEON_DATABASE_URL="your-neon-database-url"
   ```

2. Create a `.env.local` file in the frontend directory:
   ```env
   NEXT_PUBLIC_BETTER_AUTH_URL="http://localhost:3000/api/auth"
   NEXT_PUBLIC_CHATKIT_API_URL="http://localhost:8000/api/chat"
   ```

## Database Setup

1. Ensure your Neon Serverless PostgreSQL database is created and accessible.

2. Run database migrations:
   ```bash
   cd backend
   source .venv/bin/activate
   python -m alembic upgrade head
   ```

## Running the Application

### Backend (FastAPI Server)

1. From the backend directory, run:
   ```bash
   source .venv/bin/activate
   uvicorn main:app --reload --port 8000
   ```

2. The backend will be available at `http://localhost:8000`

### Frontend (Next.js App)

1. From the frontend directory, run:
   ```bash
   npm run dev
   ```

2. The frontend will be available at `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user info

### Task Management
- `GET /api/tasks` - Get user's tasks
- `POST /api/tasks` - Create a new task
- `PUT /api/tasks/{id}` - Update a task
- `DELETE /api/tasks/{id}` - Delete a task
- `PATCH /api/tasks/{id}/complete` - Mark task as complete

### Chat Interface
- `POST /api/chat` - Send message to AI chatbot
- `GET /api/conversations` - Get user's conversations
- `GET /api/conversations/{id}/messages` - Get messages in a conversation

## Using the Chat Interface

1. Visit `http://localhost:3000` in your browser
2. Sign in or register for an account
3. Navigate to the chat interface
4. Start interacting with the AI by typing natural language commands like:
   - "Add a task to buy groceries"
   - "Show me my tasks"
   - "Mark task 3 as complete"
   - "Update the meeting task to include Zoom link"

## Development

### Adding New MCP Tools

1. Create a new tool in `backend/src/api/mcp/tools.py`:
   ```python
   @mcp.tool()
   async def create_task(description: str, ctx: Context[ServerSession, None]) -> dict:
       """Create a new task for the current user."""
       # Implementation here
       return {"status": "success", "task_id": task_id}
   ```

2. Register the tool with your MCP server instance

### Modifying Data Models

1. Update the model in `backend/src/models/`
2. Create a new Alembic migration:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```
3. Apply the migration:
   ```bash
   alembic upgrade head
   ```

## Testing

### Backend Tests
Run backend tests with pytest:
```bash
cd backend
source .venv/bin/activate
pytest
```

### Frontend Tests
Run frontend tests with Jest:
```bash
cd frontend
npm test
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**: Verify your Neon database URL is correct and accessible
2. **OpenAI API Errors**: Check that your API key is valid and has sufficient quota
3. **Authentication Issues**: Ensure your Better Auth configuration is correct
4. **CORS Errors**: Verify backend and frontend ports match your configuration

### Useful Commands

- Check backend API: `curl http://localhost:8000/health`
- View API docs: `http://localhost:8000/docs`
- Check frontend: `http://localhost:3000/api/health`

## Next Steps

1. Explore the API documentation at `/docs` endpoint
2. Customize the chat interface in the frontend
3. Add new MCP tools for additional functionality
4. Extend data models to support new features