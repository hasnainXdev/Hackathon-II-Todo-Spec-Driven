import { neon } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';
import * as schema from './better-auth-schema';

// Initialize the Neon HTTP client and Drizzle ORM instance only when needed
let dbInstance: ReturnType<typeof drizzle> | null = null;

export const getDb = () => {
  if (!dbInstance) {
    if (!process.env.NEXT_PUBLIC_DATABASE_URL) {
      throw new Error('NEXT_PUBLIC_DATABASE_URL is not set');
    }

    const sql = neon(process.env.NEXT_PUBLIC_DATABASE_URL);
    dbInstance = drizzle(sql, { schema });
  }

  return dbInstance;
};