import { getDb } from './connection';
import { tasks, userPreferences, user } from './better-auth-schema';
import { eq, and } from 'drizzle-orm';

// User operations
export const getUserById = async (userId: string) => {
  const db = getDb();
  return await db.select().from(user).where(eq(user.id, userId)).then(result => result[0]);
};

export const getUserByEmail = async (email: string) => {
  const db = getDb();
  return await db.select().from(user).where(eq(user.email, email)).then(result => result[0]);
};

export const createUser = async (userData: typeof user.$inferInsert) => {
  const db = getDb();
  return await db.insert(user).values(userData).returning();
};

export const updateUser = async (userId: string, userData: Partial<typeof user.$inferInsert>) => {
  const db = getDb();
  return await db.update(user).set(userData).where(eq(user.id, userId)).returning();
};

export const deleteUser = async (userId: string) => {
  const db = getDb();
  return await db.delete(user).where(eq(user.id, userId)).returning();
};

// Task operations
export const getAllTasks = async (userId: string) => {
  const db = getDb();
  return await db.select().from(tasks).where(eq(tasks.userId, userId));
};

export const getTaskById = async (taskId: string, userId: string) => {
  const db = getDb();
  return await db.select().from(tasks).where(and(eq(tasks.id, taskId), eq(tasks.userId, userId))).then(result => result[0]);
};

export const createTask = async (taskData: typeof tasks.$inferInsert) => {
  const db = getDb();
  return await db.insert(tasks).values(taskData).returning();
};

export const updateTask = async (taskId: string, userId: string, taskData: Partial<typeof tasks.$inferInsert>) => {
  const db = getDb();
  return await db.update(tasks).set(taskData).where(and(eq(tasks.id, taskId), eq(tasks.userId, userId))).returning();
};

export const deleteTask = async (taskId: string, userId: string) => {
  const db = getDb();
  return await db.delete(tasks).where(and(eq(tasks.id, taskId), eq(tasks.userId, userId))).returning();
};

// User Preference operations
export const getUserPreferences = async (userId: string) => {
  const db = getDb();
  return await db.select().from(userPreferences).where(eq(userPreferences.userId, userId));
};

export const getUserPreferenceByKey = async (userId: string, preferenceKey: string) => {
  const db = getDb();
  return await db.select().from(userPreferences).where(and(
    eq(userPreferences.userId, userId),
    eq(userPreferences.preferenceKey, preferenceKey)
  )).then(result => result[0]);
};

export const createUserPreference = async (preferenceData: typeof userPreferences.$inferInsert) => {
  const db = getDb();
  return await db.insert(userPreferences).values(preferenceData).returning();
};

export const updateUserPreference = async (userId: string, preferenceKey: string, preferenceValue: string) => {
  const db = getDb();
  return await db.update(userPreferences).set({ preferenceValue })
    .where(and(
      eq(userPreferences.userId, userId),
      eq(userPreferences.preferenceKey, preferenceKey)
    ))
    .returning();
};

export const deleteUserPreference = async (userId: string, preferenceKey: string) => {
  const db = getDb();
  return await db.delete(userPreferences).where(and(
    eq(userPreferences.userId, userId),
    eq(userPreferences.preferenceKey, preferenceKey)
  )).returning();
};