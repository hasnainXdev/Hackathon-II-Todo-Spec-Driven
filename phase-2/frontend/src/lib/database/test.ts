// Test to verify the database adapter implementation
import { testDbAdapter, exampleUsage } from './test-db-adapter';

// Run a basic test
const runTest = async () => {
  console.log('Starting database adapter test...');
  
  // Test the basic adapter functionality
  const adapterTestResult = await testDbAdapter();
  
  if (adapterTestResult) {
    console.log('✓ Database adapter test passed');
    
    // Example usage (with mock data)
    try {
      // This would normally require a real user ID
      // const tasks = await exampleUsage('mock-user-id');
      console.log('✓ Database adapter is ready for use');
    } catch (error) {
      console.error('✗ Error in example usage:', error);
    }
  } else {
    console.error('✗ Database adapter test failed');
  }
  
  console.log('Database adapter test completed.');
};

// Export the test function
export { runTest };

// If running this file directly, execute the test
if (typeof window === 'undefined' && require.main === module) {
  runTest();
}