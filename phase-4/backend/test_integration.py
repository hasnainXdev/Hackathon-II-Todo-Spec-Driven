#!/usr/bin/env python3
"""
Test script to verify the integration between OpenAI Agents SDK and MCP SDK
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.todo_agent import TodoAgent
from core.config import settings


def test_todo_agent():
    """Test the TodoAgent functionality"""
    print("Testing TodoAgent integration...")
    
    # Initialize the agent
    agent = TodoAgent()
    
    # Test cases
    test_cases = [
        "What can you help me with?",
        "Create a todo called 'Buy groceries' with high priority",
        "Show me my todos",
        "Update the todo 'Buy groceries' to have a description 'Need to buy milk and bread'",
        "Generate a productivity tip for work",
    ]
    
    print("\nRunning test cases:")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case}")
        
        try:
            # Test synchronous processing
            sync_result = agent.process_request_sync(test_case)
            print(f"Synchronous result: {sync_result}")
            
            # Test asynchronous processing
            async def async_test():
                return await agent.process_request(test_case)
            
            async_result = asyncio.run(async_test())
            print(f"Asynchronous result: {async_result}")
            
        except Exception as e:
            print(f"Error in test {i}: {str(e)}")


def test_with_gemini_api():
    """Test the integration with actual Gemini API if available"""
    print("\n" + "="*50)
    print("Testing with Gemini API (if configured)...")
    
    if not settings.GEMINI_API_KEY:
        print("GEMINI_API_KEY not found in settings. Skipping API tests.")
        print("To run these tests, set the GEMINI_API_KEY in your environment variables.")
        return
    
    print("GEMINI_API_KEY found. Testing API connectivity...")
    
    try:
        agent = TodoAgent()
        
        # Test a simple request
        result = agent.process_request_sync("Say hello!")
        print(f"Gemini API response: {result}")
        
        # Test a todo creation request
        todo_result = agent.process_request_sync("Create a todo called 'Test integration' with medium priority")
        print(f"Todo creation response: {todo_result}")
        
        # Test getting todos
        get_result = agent.process_request_sync("Show me my todos")
        print(f"Get todos response: {get_result}")
        
    except Exception as e:
        print(f"Error during API testing: {str(e)}")


if __name__ == "__main__":
    print("Starting integration tests for OpenAI Agents SDK and MCP SDK...")
    print(f"Gemini API Key configured: {'Yes' if settings.GEMINI_API_KEY else 'No'}")
    
    test_todo_agent()
    test_with_gemini_api()
    
    print("\nIntegration tests completed!")