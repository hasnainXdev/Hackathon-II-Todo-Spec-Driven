# Neon Serverless PostgreSQL Database Adapter

This project includes a database adapter for Neon Serverless PostgreSQL using Drizzle ORM. The adapter is located in `frontend/src/lib/database/` and provides a type-safe way to interact with the database from the frontend.

## Important Note About Better Auth Integration

This database adapter is designed for application data (tasks, user preferences, etc.) and is separate from Better Auth's internal database needs. Better Auth handles user authentication and manages its own user/session data in the backend database.

## Setup

1. Add your Neon database URL to your environment variables:

   ```bash
   NEXT_PUBLIC_DATABASE_URL=your_neon_database_url_here
   ```

2. The adapter is already integrated into the project and can be imported as follows:
   ```javascript
   import { getDb } from "@/lib/database";
   import { tasks, userPreferences } from "@/lib/database/schema";
   ```

## Usage

The adapter provides both direct database access through Drizzle ORM and convenience functions for common operations:

### Direct Database Access

```javascript
import { getDb } from "@/lib/database";
import { tasks } from "@/lib/database/schema";
import { eq } from "drizzle-orm";

// Example: Fetch tasks for a user
const db = getDb(); // Gets the database instance when needed
const userTasks = await db.select().from(tasks).where(eq(tasks.userId, userId));
```

### Using Convenience Functions

```javascript
import { getAllTasks, createTask } from "@/lib/database";

// Example: Get all tasks for a user
const userTasks = await getAllTasks(userId);

// Example: Create a new task
const newTask = await createTask({
  title: "New Task",
  description: "Task description",
  userId: userId,
});
```

## Schema

The database schema is defined in `frontend/src/lib/database/schema.ts` and matches the backend models:

- `users` table: Stores user information including name, email, password, etc.
- `tasks` table: Stores user tasks with fields like title, description, completion status, etc.
- `userPreferences` table: Stores user preferences with key-value pairs

## Components

An example component (`TaskList.tsx`) is provided in `frontend/src/components/` that demonstrates how to use the database adapter in a Next.js component.

## Environment Variables

Make sure to set the following environment variable:

- `NEXT_PUBLIC_DATABASE_URL`: Your Neon Serverless PostgreSQL connection string

## Separation of Concerns

- **Better Auth**: Handles user authentication, registration, login, sessions, etc. This uses the backend database.
- **Application Database Adapter**: Handles application-specific data like tasks and user preferences. This uses the frontend-accessible database connection.
