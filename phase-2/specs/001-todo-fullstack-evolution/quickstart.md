# Quickstart Guide: Todo Full-Stack Evolution

## Prerequisites
- Node.js 20+ installed
- Python 3.11+ installed
- PostgreSQL (local or cloud instance)
- Git

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your database URL and other settings
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set environment variables
cp .env.example .env
# Edit .env with your API URL and other settings
```

### 4. Database Setup
```bash
# From backend directory with activated virtual environment
cd backend
alembic upgrade head
```

### 5. Running the Application

#### Backend (API Server)
```bash
cd backend
uvicorn main:app --reload
```

#### Frontend (Development Server)
```bash
cd frontend
npm run dev
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (.env)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Endpoints
- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:3000`

## First Steps
1. Register a new user account
2. Log in to obtain JWT token
3. Create your first task
4. View your task list
5. Mark tasks as complete
6. Set user preferences (theme, notifications, etc.)