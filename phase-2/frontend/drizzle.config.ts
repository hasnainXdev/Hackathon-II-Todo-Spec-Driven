import { defineConfig } from 'drizzle-kit';
export default defineConfig({
  schema: './src/lib/database/better-auth-schema.ts',
  out: './drizzle',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.NEXT_PUBLIC_DATABASE_URL || '',
  }
});