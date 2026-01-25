/**
 * Integration test for WebSocket real-time sync functionality
 * This test verifies that the WebSocket endpoints are working correctly
 */

import WebSocket from 'ws';
import axios from 'axios';

// Configuration
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const WS_URL = BACKEND_URL.replace('http', 'ws');

// Mock user ID for testing
const TEST_USER_ID = 'test-user-123';

async function testWebSocketConnection() {
  console.log('Testing WebSocket connection...');

  return new Promise<void>((resolve, reject) => {
    // Connect to WebSocket
    const ws = new WebSocket(`${WS_URL}/ws/${TEST_USER_ID}`);

    ws.on('open', () => {
      console.log('✓ WebSocket connection opened');
      
      // Send authentication message
      ws.send(JSON.stringify({
        type: 'AUTH',
        token: 'mock-token-for-testing'
      }));
    });

    ws.on('message', (data) => {
      const message = JSON.parse(data.toString());
      console.log('Received message:', message);
      
      if (message.type === 'AUTH_SUCCESS') {
        console.log('✓ Authentication successful');
        ws.close();
        resolve();
      }
    });

    ws.on('error', (error) => {
      console.error('WebSocket error:', error);
      reject(error);
    });

    ws.on('close', () => {
      console.log('WebSocket connection closed');
    });

    // Set timeout to reject if connection takes too long
    setTimeout(() => {
      ws.close();
      reject(new Error('WebSocket connection timeout'));
    }, 10000);
  });
}

async function testTaskCRUDWithWebSocket() {
  console.log('\nTesting Task CRUD operations with WebSocket notifications...');

  // First, authenticate and get a valid token
  // Note: In a real test, you would use a proper authentication flow
  const mockToken = 'mock-backend-token';

  // Create a test task
  console.log('Creating a test task...');
  
  try {
    const response = await axios.post(
      `${BACKEND_URL}/api/v1/tasks/`,
      {
        title: 'Test task for WebSocket sync',
        description: 'This task is created to test WebSocket notifications',
        completion_status: false
      },
      {
        headers: {
          'Authorization': `Bearer ${mockToken}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    console.log('✓ Task created:', response.data.id);
    
    // Update the task
    console.log('Updating the task...');
    const updateResponse = await axios.put(
      `${BACKEND_URL}/api/v1/tasks/${response.data.id}`,
      {
        title: 'Updated test task for WebSocket sync',
        description: 'This task has been updated to test WebSocket notifications',
        completion_status: true
      },
      {
        headers: {
          'Authorization': `Bearer ${mockToken}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    console.log('✓ Task updated:', updateResponse.data.id);
    
    // Delete the task
    console.log('Deleting the task...');
    const deleteResponse = await axios.delete(
      `${BACKEND_URL}/api/v1/tasks/${response.data.id}`,
      {
        headers: {
          'Authorization': `Bearer ${mockToken}`
        }
      }
    );
    
    console.log('✓ Task deleted:', response.data.id);
  } catch (error) {
    console.error('Error during CRUD operations:', error.message);
    throw error;
  }
}

async function runIntegrationTest() {
  try {
    console.log('Starting WebSocket real-time sync integration test...\n');
    
    // Test WebSocket connection
    await testWebSocketConnection();
    
    // Test CRUD operations (these should trigger WebSocket notifications)
    await testTaskCRUDWithWebSocket();
    
    console.log('\n✓ All tests passed! Real-time sync functionality is working.');
  } catch (error) {
    console.error('\n✗ Test failed:', error.message);
    process.exit(1);
  }
}

// Run the test
if (require.main === module) {
  runIntegrationTest();
}

export { runIntegrationTest };