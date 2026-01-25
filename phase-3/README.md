# Todo Full-Stack Evolution with AI Chatbot Integration

## Overview

This project is a secure, multi-user full-stack web application with persistent storage and authentication. It allows users to manage their personal todo lists with features for creating, reading, updating, and deleting tasks while ensuring data privacy and preventing unauthorized access.

The application has been enhanced with AI chatbot capabilities that allow users to manage their tasks using natural language commands.

## Architecture

- **Frontend**: Next.js 16+ with TypeScript, Tailwind CSS, OpenAI ChatKit
- **Backend**: FastAPI with Python 3.11, SQLModel ORM
- **AI Framework**: OpenAI Agents SDK Integration with MCP (Model Context Protocol) SDK
- **Database**: PostgreSQL (Neon Serverless)
- **Authentication**: Better Auth with JWT tokens

## Features

### User Stories Implemented

1. **Multi-User Todo Management**: Users can create, read, update, and delete their personal tasks with proper data isolation
2. **Authentication & Authorization**: Secure user authentication with JWT tokens and proper authorization
3. **Task Completion & Management**: Users can mark tasks as complete/incomplete and manage task details
4. **User Preferences**: Users can set and manage their preferences (theme, notifications, etc.)
5. **AI-Powered Chatbot**: Users can manage tasks using natural language commands

## Project Structure

### Backend

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── api/
│   └── v1/
│       ├── __init__.py     # API router configuration
│       ├── auth.py         # Authentication endpoints
│       ├── tasks.py        # Task management endpoints
│       ├── conversations.py # Conversation management endpoints
│       └── chat.py         # AI chatbot endpoints
├── core/
│   ├── config.py          # Configuration settings
│   ├── security.py        # JWT authentication utilities
│   ├── ai_logging.py      # AI service logging
│   ├── rate_limiter.py    # Rate limiting for AI endpoints
│   ├── i18n_manager.py    # Internationalization manager
│   ├── performance_monitor.py # Performance monitoring
│   └── logging_config.py  # Logging configuration
├── database/
│   └── session.py         # Database session management
├── models/
│   ├── task.py            # Task model
│   ├── conversation.py    # Conversation model
│   ├── message.py         # Message model
│   └── user_preference.py # User preference model
├── services/
│   ├── ai_service.py      # AI service abstraction
│   ├── ai_chat_service.py # AI chat service
│   ├── task_service.py    # Task business logic
│   ├── analytics_service.py # Analytics service
│   ├── privacy_controls.py # Privacy controls
│   ├── chat_history_backup_manager.py # Chat history backup
│   ├── onboarding_manager.py # Onboarding manager
│   └── user_preference_service.py # User preference business logic
├── schemas/
│   ├── task.py            # Task schemas
│   ├── chat.py            # Chat schemas
│   ├── user.py            # User schemas
│   └── user_preference.py # User preference schemas
├── utils/
│   ├── nlp_parser.py      # NLP parsing utilities
│   ├── nlp_task_updates.py # NLP task update parsing
│   ├── nlp_task_deletion.py # NLP task deletion parsing
│   ├── nlp_task_completion.py # NLP task completion parsing
│   ├── intent_recognizer.py # Intent recognition
│   ├── fallback_responses.py # Fallback responses
│   ├── task_validator.py  # Task validation
│   ├── error_formatter.py # Error formatting
│   ├── context_manager.py # Context management
│   ├── task_behavior_aggregator.py # Task behavior aggregation
│   └── exceptions.py      # Custom exceptions
├── algorithms/
│   ├── task_creation_suggestion_algorithm.py # Task creation suggestions
│   ├── task_prioritization_suggestion_algorithm.py # Task prioritization
│   └── task_completion_suggestion_algorithm.py # Task completion suggestions
├── ai_models/
│   └── personalized_suggestions_model.py # Personalized suggestions AI model
└── tests/
    ├── test_tasks.py      # Task-related tests
    ├── test_auth.py       # Authentication tests
    ├── test_preferences.py # Preference tests
    ├── test_models.py     # Model validation tests
    ├── test_nlp_parsing.py # NLP parsing tests
    ├── test_nlp_task_operations.py # NLP task operations tests
    ├── test_ai_suggestions_effectiveness.py # AI suggestions tests
    └── test_e2e_ai_chatbot.py # End-to-end AI chatbot tests
```

### Frontend

```
frontend/
├── package.json           # Node.js dependencies
├── src/
│   ├── app/              # Next.js app router pages
│   │   ├── api/
│   │   │   └── chat/
│   │   │       └── route.ts      # Chat API route
│   │   ├── login/        # Login page
│   │   ├── signup/       # Signup page
│   │   ├── dashboard/    # Dashboard page
│   │   ├── chat/         # Chat page
│   │   └── preferences/  # Preferences page
│   ├── components/       # React components
│   │   ├── ChatInterface.tsx  # AI chat interface component
│   │   ├── AISuggestionsPanel.tsx # AI suggestions panel
│   │   ├── TaskList.tsx  # Task list component
│   │   ├── TaskItem.tsx  # Task item component
│   │   ├── TaskForm.tsx  # Task form component
│   │   ├── UserPreferences.tsx # User preferences component
│   │   ├── Navbar.tsx    # Navigation component
│   │   ├── AuthGuard.tsx # Authentication guard
│   │   └── ErrorBoundary.tsx # Error boundary component
│   ├── lib/
│   │   ├── auth.ts       # Better Auth configuration
│   │   └── api.ts        # API client with JWT handling
│   ├── types/
│   │   ├── task.ts       # TypeScript type definitions
│   │   └── chat.ts       # Chat type definitions
│   └── __tests__/        # Frontend tests
│       ├── ChatInterface.test.tsx
│       ├── TaskList.test.tsx
│       └── TaskItem.test.tsx
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory: `cd backend`
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - On Linux/Mac: `source venv/bin/activate`
   - On Windows: `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set environment variables in `.env` file:
   ```
   DATABASE_URL=postgresql://user:password@localhost/dbname
   BETTER_AUTH_SECRET=your-secret-key-here
   BETTER_AUTH_URL=http://localhost:3000
   JWT_SECRET=your-jwt-secret
   BASE_URL=http://localhost:3000
   OPENAI_API_KEY=your-openai-api-key
   OPENAI_MODEL=gpt-4-turbo-preview
   ```
6. Run the application: `uvicorn main:app --reload`

### Frontend Setup

1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Set environment variables in `.env.local` file:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_CHATKIT_API_URL=http://localhost:8000/api/chat
   ```
4. Run the development server: `npm run dev`

## AI Chatbot Usage Instructions

### Getting Started

1. Navigate to the dashboard after logging in
2. Find the chat interface panel
3. Start typing your requests in natural language
4. The AI will process your request and respond accordingly

### Supported Commands

#### Creating Tasks

- "Add a task to buy groceries"
- "Create a task to finish the report by Friday"
- "New task: schedule dentist appointment"
- "I need to call mom tomorrow"
- "Remind me to water plants next week"

#### Updating Tasks

- "Change the grocery task to include organic items"
- "Update the meeting task to include Zoom link"
- "Modify the workout task to be in the morning"

#### Completing Tasks

- "Mark the laundry task as complete"
- "Complete the dishes task"
- "Finish the vacuuming task"
- "Check off the shopping task"

#### Deleting Tasks

- "Delete the old meeting task"
- "Remove the cancelled appointment"
- "Get rid of the obsolete reminder"

#### Viewing Tasks

- "Show me my tasks"
- "List all my tasks"
- "What are my current tasks?"
- "Display my pending tasks"

#### Getting Suggestions

- "What should I work on today?"
- "Any suggestions for tasks?"
- "Recommend something productive to do"

### Natural Language Tips

The AI is designed to understand various ways of expressing your needs:

- **Be Specific**: "Add a high priority task to prepare presentation for Monday's meeting"
- **Include Dates**: "Create a task to call insurance company by end of week"
- **Mention Priority**: "I have an urgent task to follow up with client"
- **Contextual References**: After creating a task, you can refer to it as "it" or "that task"

### AI-Powered Features

#### Smart Suggestions

The AI learns from your patterns and suggests:

- Tasks you might want to create based on your history
- Priorities for your existing tasks
- Optimal times to complete certain tasks

#### Context Awareness

The AI remembers:

- Previous interactions in the same conversation
- Your task completion patterns
- Recurring tasks you tend to create

#### Intelligent Prioritization

Based on:

- Due dates
- Keywords in task titles
- Historical patterns
- Urgency indicators

### Accessibility Features

The chat interface includes several accessibility features:

- Screen reader support with proper ARIA labels
- Keyboard navigation support
- Adjustable text size options
- Text-to-speech functionality for messages

### Privacy Controls

You have full control over your data:

- **Analytics Sharing**: Choose whether to share usage data to improve the AI
- **AI Profiling**: Control if your behavior is used to personalize suggestions
- **Data Retention**: Manage how long your data is stored

To update your privacy settings, visit the Settings page from your dashboard.

## API Endpoints

### Authentication

- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/logout` - Logout user

### Tasks

- `GET /api/v1/tasks` - Get all tasks for current user
- `POST /api/v1/tasks` - Create a new task
- `GET /api/v1/tasks/{id}` - Get a specific task
- `PUT /api/v1/tasks/{id}` - Update a specific task
- `DELETE /api/v1/tasks/{id}` - Delete a specific task
- `PATCH /api/v1/tasks/{id}/complete` - Toggle task completion status

### Preferences

- `GET /api/v1/preferences` - Get all user preferences
- `GET /api/v1/preferences/{key}` - Get a specific preference
- `PUT /api/v1/preferences/{key}` - Create or update a preference
- `DELETE /api/v1/preferences/{key}` - Delete a specific preference

### Chatbot

- `POST /api/v1/chat` - Send message to AI chatbot
- `GET /api/v1/conversations` - Get user's conversations
- `GET /api/v1/conversations/{id}/messages` - Get messages in a conversation

## Security Features

- JWT token-based authentication
- User data isolation (users can only access their own data)
- Rate limiting to prevent abuse of AI endpoints
- Input validation and sanitization
- Optimistic locking for concurrent updates
- Encrypted communication with AI provider

## Testing

- Backend: Run `pytest` in the backend directory
- Frontend: Run `npm test` in the frontend directory
- End-to-end: Run `pytest tests/test_e2e_ai_chatbot.py` for AI chatbot tests

## Environment Variables

- `DATABASE_URL`: PostgreSQL database connection string
- `BETTER_AUTH_SECRET`: Secret key for Better Auth
- `BETTER_AUTH_URL`: Base URL for Better Auth
- `JWT_SECRET`: Secret key for JWT token signing
- `BASE_URL`: Base URL for the application
- `GEMINI_API_KEY`: API key for OpenAI services
- `NEXT_PUBLIC_API_URL`: Frontend environment variable for backend API URL

## Deployment

The application can be deployed to any platform that supports both Python (for the backend) and Node.js (for the frontend). For example:

- Backend: Deploy to platforms like Heroku, Railway, or AWS
- Frontend: Deploy to platforms like Vercel, Netlify, or AWS Amplify

## Error Handling

- Proper error responses with appropriate HTTP status codes
- Logging of errors for debugging
- Frontend error boundaries to prevent crashes
- Loading and error states in UI components
- AI service error handling and fallback responses

## Performance Considerations

- Optimized database queries with proper indexing
- Efficient API endpoints with pagination where appropriate
- Client-side caching where beneficial
- Optimized bundle sizes for frontend
- Rate limiting for AI service endpoints
- Performance monitoring for AI operations

## Future Enhancements

- Real-time updates using WebSockets
- Email notifications for task updates
- Advanced filtering and search capabilities
- Task categorization and tagging
- Sharing tasks with other users
- Mobile app using React Native
- Enhanced AI capabilities with custom models