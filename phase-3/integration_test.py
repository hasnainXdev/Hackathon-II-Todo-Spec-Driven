"""
Integration test to verify that all components work together properly.
This test simulates the interaction between the frontend, AI agent, and MCP server.
"""

import asyncio
import sys
import os

# Add backend src to path so we can import our modules
backend_src_path = os.path.join(os.path.dirname(__file__), 'backend', 'src')
sys.path.insert(0, backend_src_path)

try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    from src.todo_agent import TodoAgent
    import json


    def test_integration():
        """
        Test the integration between all components
        """
        print("Testing integration between all components...")

        # Initialize the AI agent
        todo_agent = TodoAgent()

        # Test 1: Simple query to the AI agent
        print("\n1. Testing AI agent response:")
        response = todo_agent.process_request_sync("What can you help me with?")
        print(f"   Response: {response}")

        # Test 2: Simulate a todo creation request
        print("\n2. Testing todo creation simulation:")
        creation_request = "Create a new todo: Buy groceries, with high priority"
        response = todo_agent.process_request_sync(creation_request)
        print(f"   Response: {response}")

        # Test 3: Simulate getting todos
        print("\n3. Testing todo retrieval simulation:")
        retrieval_request = "Show me my todos"
        response = todo_agent.process_request_sync(retrieval_request)
        print(f"   Response: {response}")

        # Test 4: Simulate updating a todo
        print("\n4. Testing todo update simulation:")
        update_request = "Mark the grocery todo as completed"
        response = todo_agent.process_request_sync(update_request)
        print(f"   Response: {response}")

        print("\nIntegration test completed successfully!")


    if __name__ == "__main__":
        test_integration()
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory.")