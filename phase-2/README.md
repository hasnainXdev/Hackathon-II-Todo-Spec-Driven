# Todo Full-Stack Evolution

## Overview
This project is a secure, multi-user full-stack web application with persistent storage and authentication. It allows users to manage their personal todo lists with features for creating, reading, updating, and deleting tasks while ensuring data privacy and preventing unauthorized access.

## Architecture
- **Frontend**: Next.js 16+ with TypeScript, Tailwind CSS
- **Backend**: FastAPI with Python 3.11, SQLModel ORM
- **Database**: PostgreSQL (Neon Serverless)
- **Authentication**: Better Auth with JWT tokens

## Features

### User Stories Implemented
1. **Multi-User Todo Management**: Users can create, read, update, and delete their personal tasks with proper data isolation
2. **Authentication & Authorization**: Secure user authentication with JWT tokens and proper authorization
3. **Task Completion & Management**: Users can mark tasks as complete/incomplete and manage task details
4. **User Preferences**: Users can set and manage their preferences (theme, notifications, etc.)

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
│       └── tasks.py        # Task management endpoints
├── core/
│   ├── config.py          # Configuration settings
│   ├── security.py        # JWT authentication utilities
│   └── logging_config.py  # Logging configuration
├── database/
│   └── session.py         # Database session management
├── models/
│   ├── task.py            # Task model
│   └── user_preference.py # User preference model
├── services/
│   ├── task_service.py    # Task business logic
│   └── user_preference_service.py # User preference business logic
├── schemas/
│   ├── task.py            # Task schemas
│   ├── user.py            # User schemas
│   └── user_preference.py # User preference schemas
├── utils/
│   └── exceptions.py      # Custom exceptions
└── tests/
    ├── test_tasks.py      # Task-related tests
    ├── test_auth.py       # Authentication tests
    ├── test_preferences.py # Preference tests
    └── test_models.py     # Model validation tests
```

### Frontend
```
frontend/
├── package.json           # Node.js dependencies
├── src/
│   ├── app/              # Next.js app router pages
│   │   ├── login/        # Login page
│   │   ├── signup/       # Signup page
│   │   ├── dashboard/    # Dashboard page
│   │   └── preferences/  # Preferences page
│   ├── components/       # React components
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
│   │   └── task.ts       # TypeScript type definitions
│   └── __tests__/        # Frontend tests
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
   ```
6. Run the application: `uvicorn main:app --reload`

### Frontend Setup
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Set environment variables in `.env.local` file:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
4. Run the development server: `npm run dev`

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

## Security Features
- JWT token-based authentication
- User data isolation (users can only access their own data)
- Rate limiting to prevent abuse
- Input validation and sanitization
- Optimistic locking for concurrent updates

## Testing
- Backend: Run `pytest` in the backend directory
- Frontend: Run `npm test` in the frontend directory

## Environment Variables
- `DATABASE_URL`: PostgreSQL database connection string
- `BETTER_AUTH_SECRET`: Secret key for Better Auth
- `BETTER_AUTH_URL`: Base URL for Better Auth
- `JWT_SECRET`: Secret key for JWT token signing
- `BASE_URL`: Base URL for the application
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

## Performance Considerations
- Optimized database queries with proper indexing
- Efficient API endpoints with pagination where appropriate
- Client-side caching where beneficial
- Optimized bundle sizes for frontend

## Future Enhancements
- Real-time updates using WebSockets
- Email notifications for task updates
- Advanced filtering and search capabilities
- Task categorization and tagging
- Sharing tasks with other users
- Mobile app using React Native