import { pgTable, serial, varchar, boolean, timestamp, uuid } from 'drizzle-orm/pg-core';

// Define the users table
export const users = pgTable('users', {
  id: uuid('id').defaultRandom().primaryKey(),
  name: varchar('name', { length: 255 }).notNull(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  password: varchar('password', { length: 255 }), // Optional if using OAuth
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
  emailVerified: boolean('email_verified').default(false),
  avatar: varchar('avatar', { length: 500 }), // URL to user's avatar
});

// Define the tasks table
export const tasks = pgTable('tasks', {
  id: uuid('id').defaultRandom().primaryKey(),
  title: varchar('title', { length: 200 }).notNull(),
  description: varchar('description', { length: 1000 }),
  completionStatus: boolean('completion_status').default(false).notNull(),
  userId: varchar('user_id', { length: 255 }).notNull(), // UUID of the user from Better Auth
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
  version: serial('version').default(1).notNull(), // For optimistic locking
});

// Define the user_preferences table
export const userPreferences = pgTable('user_preferences', {
  id: uuid('id').defaultRandom().primaryKey(),
  userId: varchar('user_id', { length: 255 }).notNull(), // UUID of the user from Better Auth
  preferenceKey: varchar('preference_key', { length: 100 }).notNull(),
  preferenceValue: varchar('preference_value', { length: 500 }).notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});