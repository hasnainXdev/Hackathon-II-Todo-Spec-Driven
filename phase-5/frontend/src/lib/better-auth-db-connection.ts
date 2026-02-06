import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';
import * as schema from './database/better-auth-schema';

// Initialize PostgreSQL pool for Better Auth
let authDbPool: Pool | null = null;
let authDbInstance: ReturnType<typeof drizzle> | null = null;

export const getAuthDb = () => {
  if (!authDbInstance) {
    if (!process.env.NEXT_PUBLIC_DATABASE_URL) {
      throw new Error('NEXT_PUBLIC_DATABASE_URL is not set');
    }

    // Create a new pool instance if one doesn't exist
    if (!authDbPool) {
      authDbPool = new Pool({
        connectionString: process.env.NEXT_PUBLIC_DATABASE_URL,
      });
    }

    // Create the Drizzle instance with the pool
    authDbInstance = drizzle(authDbPool, { schema });
  }

  return authDbInstance;
};