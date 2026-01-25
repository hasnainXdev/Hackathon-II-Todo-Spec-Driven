import asyncio
from agents import (
    Agent,
    Runner,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
    function_tool,
)
from openai import AsyncOpenAI
from core.config import settings
from typing import Dict, Any
import json
import sys
from pathlib import Path

# Add the project root to the path to import MCP tools
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.todo_mcp_server import (
    create_todo,
    get_todos,
    update_todo,
    delete_todo,
    generate_productivity_tip,
)

set_tracing_disabled(disabled=True)

# Configure the AsyncOpenAI client for OpenRouter API
e_client = AsyncOpenAI(
    api_key=settings.OPEN_ROUTER_KEY,
    base_url="https://openrouter.ai/api/v1",
)

# Use a free model with higher rate limits
model = OpenAIChatCompletionsModel(
    model="google/gemini-2.0-flash-001",  # Free model with higher rate limits
    openai_client=e_client,
)


# Define the tools using the @function_tool decorator
@function_tool
def create_todo_tool(
    title: str, description: str = "", priority: str = "medium", category: str = ""
) -> str:
    """
    Creates a new todo item with the given parameters.
    """
    return create_todo(
        title=title, description=description, priority=priority, category=category
    )


@function_tool
def get_todos_tool(
    filter_by: str = "all", category: str = "", priority: str = "", search: str = ""
) -> str:
    """
    Retrieves a list of todo items based on optional filters.
    """
    return get_todos(filter_by=filter_by, category=category, priority=priority, search=search)


@function_tool
def update_todo_tool(
    todo_id: str = None,
    title: str = None,
    description: str = None,
    priority: str = None,
    category: str = None,
    completed: bool = None,
) -> str:
    """
    Updates an existing todo item with the provided parameters.
    """
    return update_todo(
        todo_id=todo_id,
        title=title,
        description=description,
        priority=priority,
        category=category,
        completed=completed,
    )


@function_tool
def delete_todo_tool(todo_id: str = None, title: str = None) -> str:
    """
    Deletes a todo item by its ID or title.
    """
    return delete_todo(todo_id=todo_id, title=title)


@function_tool
def generate_productivity_tip_tool(category: str = "general") -> str:
    """
    Generates a productivity tip based on the specified category.
    """
    return generate_productivity_tip(category=category)


class TodoAgent:
    """
    AI Todo chatbot using OpenAI Agents Python SDK
    """

    def __init__(self):
        # Create the main agent with instructions for handling todo tasks
        self.agent = Agent(
            name="Todo Assistant",
            instructions="""You are a helpful AI assistant specialized in managing todo lists.
            You can help users create, view, update, and delete todo items using the available tools.
            You can also categorize tasks, set priorities, and provide recommendations
            for productivity and task management. Always respond in a friendly and helpful manner.

            Available tools:
            - create_todo: Creates a new todo item with title, description, priority, and category
            - get_todos: Retrieves a list of todo items with optional filters (filter_by, category, priority, search)
            - update_todo: Updates an existing todo item with various parameters (can use todo_id or title to identify the task)
            - delete_todo: Deletes a todo item by its ID or title
            - generate_productivity_tip: Generates a productivity tip based on category

            When a user wants to perform any todo operation:
            1. For update/delete operations, if the user doesn't provide a specific ID, you can use the title to identify the task
            2. For completion requests like "mark X as complete" or "update task to complete X",
               use the title parameter and set completed=true in the update_todo tool
            3. Always use the most appropriate tool for the user's request
            4. If a user says "update the task to complete [task name]", interpret this as marking that task as completed
            5. Be concise and helpful in your responses
            6. When users ask to update or delete tasks, you can use the title instead of requiring an ID
            """,
            model=model,
            tools=[
                create_todo_tool,
                get_todos_tool,
                update_todo_tool,
                delete_todo_tool,
                generate_productivity_tip_tool,
            ],
        )

    async def process_request(self, user_input: str, user_id: str = None) -> str:
        """
        Process user input and return the agent's response
        """
        try:
            # Set the authenticated user ID in the environment for the MCP tools
            if user_id:
                import os
                os.environ["AUTHENTICATED_USER_ID"] = user_id

            result = await Runner.run(self.agent, user_input)
            return result.final_output
        except Exception as e:
            return f"Sorry, I encountered an error processing your request: {str(e)}"

    def process_request_sync(self, user_input: str, user_id: str = None) -> str:
        """
        Process user input synchronously and return the agent's response
        """
        try:
            # Run the async function in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                coro = self.process_request(user_input, user_id)
                result = loop.run_until_complete(coro)
            finally:
                loop.close()
            return result
        except Exception as e:
            return f"Sorry, I encountered an error processing your request: {str(e)}"


# Example usage
if __name__ == "__main__":
    todo_agent = TodoAgent()

    # Example synchronous usage
    response = todo_agent.process_request_sync("What can you help me with?", "test_user")
    print(response)

    # Example asynchronous usage
    async def example():
        response = await todo_agent.process_request("Create a sample todo for me", "test_user")
        print(response)

    asyncio.run(example())
