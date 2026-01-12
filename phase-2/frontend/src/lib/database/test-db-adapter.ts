// Simple test file to verify database adapter functionality
import { getDb } from './connection';
import { tasks } from './schema';
import { eq } from 'drizzle-orm';

// Mock function to simulate testing the database adapter
// This would typically be run in a test environment
export const testDbAdapter = async () => {
  try {
    // Attempt to connect and run a simple query
    // Note: This is just a test to ensure the adapter is properly set up
    console.log('Testing database adapter...');

    // This would normally execute a simple query to verify connection
    // Since we don't have actual data, we'll just verify the connection object can be created
    try {
      const db = getDb();
      if (db) {
        console.log('✓ Database adapter initialized successfully');
        return true;
      } else {
        console.error('✗ Database adapter initialization failed');
        return false;
      }
    } catch (initError) {
      console.error('✗ Error initializing database adapter:', initError);
      return false;
    }
  } catch (error) {
    console.error('✗ Error testing database adapter:', error);
    return false;
  }
};

// Example of how to use the database adapter in a component
export const exampleUsage = async (userId: string) => {
  try {
    // Fetch all tasks for a specific user
    const db = getDb();
    const userTasks = await db
      .select()
      .from(tasks)
      .where(eq(tasks.userId, userId));

    console.log(`Found ${userTasks.length} tasks for user ${userId}`);
    return userTasks;
  } catch (error) {
    console.error('Error fetching tasks:', error);
    throw error;
  }
};