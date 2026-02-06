import { auth } from './auth';

interface TokenResponse {
  authenticated: boolean;
  user?: any;
  backend_token?: string;
  error?: string;
}

/**
 * Retrieves a backend-compatible token from the auth API
 */
async function getBackendToken(): Promise<string> {
  try {
    const tokenResponse = await fetch('/api/auth/backend-token');
    const tokenData: TokenResponse = await tokenResponse.json();

    if (!tokenData.backend_token) {
      throw new Error(tokenData.error || 'No backend token available');
    }

    return tokenData.backend_token;
  } catch (error) {
    console.error('Error getting backend token:', error);
    throw new Error('Failed to authenticate with backend');
  }
}

/**
 * Creates a new conversation
 */
export async function createConversation(title: string) {
  const backendToken = await getBackendToken();

  const response = await fetch(`${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/chats/chats/conversations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${backendToken}`,
    },
    body: JSON.stringify({ title }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

/**
 * Adds a message to an existing conversation
 */
export async function addMessageToConversation(conversationId: string, content: string, role: 'user' | 'assistant' = 'user') {
  const backendToken = await getBackendToken();

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/chats/chats/conversations/${conversationId}/messages`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${backendToken}`,
      },
      body: JSON.stringify({
        role,
        content
      }),
    }
  );

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  const responseData = await response.json();

  // Format the response to ensure clarity
  return formatApiResponse(responseData);
}

/**
 * Formats API responses for better clarity in the UI
 */
function formatApiResponse(data: any): any {
  // If the response contains a JSON string in the content, parse and format it nicely
  if (data && typeof data.content === 'string') {
    try {
      // Try to parse if it looks like a JSON string
      const parsed = JSON.parse(data.content);

      // If it's a structured response from our AI service, format it appropriately
      if (parsed.response) {
        return {
          ...data,
          content: formatAiResponse(parsed.response)
        };
      }
      return data;
    } catch (e) {
      // If it's not JSON, return as-is
      return data;
    }
  }
  return data;
}

/**
 * Formats AI responses for better readability
 */
function formatAiResponse(response: string): string {
  // If the response is a JSON string representing a task operation, format it nicely
  try {
    const parsed = JSON.parse(response);

    if (typeof parsed === 'object') {
      // Format task creation response
      if (parsed.title && parsed.id) {
        return `✅ Successfully created task: "${parsed.title}" (ID: ${parsed.id})`;
      }

      // Format task update response
      if (parsed.id && (parsed.title || parsed.completed !== undefined)) {
        const updates = [];
        if (parsed.title) updates.push(`title: "${parsed.title}"`);
        if (parsed.completed !== undefined) {
          updates.push(parsed.completed ? 'marked as completed' : 'marked as incomplete');
        }
        return `✅ Successfully updated task (ID: ${parsed.id}). ${updates.join(', ')}.`;
      }

      // Format task deletion response
      if (parsed.success === true && parsed.deleted_id) {
        return `✅ Successfully deleted task (ID: ${parsed.deleted_id})`;
      }

      // Format list of tasks response
      if (Array.isArray(parsed)) {
        if (parsed.length === 0) {
          return '📋 You have no tasks at the moment.';
        }

        const taskList = parsed.map((task: any) => {
          const status = task.completed ? '✅' : '⏳';
          const taskId = task.id ? `(ID: ${task.id.substring(0, 8)}...)` : '';
          return `- ${status} "${task.title}" ${taskId}`.trim();
        }).join('\n');

        return `📋 Here are your tasks:\n${taskList}`;
      }

      // Format generic success response
      if (parsed.success === true && parsed.message) {
        return `✅ ${parsed.message}`;
      }
    }

    return JSON.stringify(parsed, null, 2);
  } catch (e) {
    // If it's not JSON, return as-is but clean up any excessive technical jargon
    // Remove technical prefixes that might appear in AI responses
    let cleanedResponse = response.replace(/```json[\s\S]*?\n```/g, '');
    cleanedResponse = cleanedResponse.replace(/```[\s\S]*?\n```/g, '');

    // If the response contains JSON-like strings, try to parse and format them
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      try {
        const extractedJson = JSON.parse(jsonMatch[0]);
        if (Array.isArray(extractedJson)) {
          if (extractedJson.length === 0) {
            return '📋 You have no tasks at the moment.';
          }

          const taskList = extractedJson.map((task: any) => {
            const status = task.completed ? '✅' : '⏳';
            const taskId = task.id ? `(ID: ${task.id.substring(0, 8)}...)` : '';
            return `- ${status} "${task.title}" ${taskId}`.trim();
          }).join('\n');

          return `📋 Here are your tasks:\n${taskList}`;
        }
      } catch (parseError) {
        // If parsing fails, return the cleaned response
      }
    }

    return cleanedResponse;
  }
}

/**
 * Fetches messages for a conversation
 */
export async function getConversationMessages(conversationId: string) {
  const backendToken = await getBackendToken();

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/chats/chats/conversations/${conversationId}/messages`,
    {
      headers: {
        'Authorization': `Bearer ${backendToken}`,
      },
    }
  );

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  const responseData = await response.json();

  // Format all messages in the response for better clarity
  return responseData.map((message: any) => formatApiResponse(message));
}

/**
 * Fetches all conversations for the user
 */
export async function getUserConversations() {
  const backendToken = await getBackendToken();

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/chats/chats/conversations`,
    {
      headers: {
        'Authorization': `Bearer ${backendToken}`,
      },
    }
  );

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

/**
 * Creates a new conversation and adds the first message
 */
export async function createConversationWithMessage(content: string) {
  // First create a conversation
  const conversationTitle = `New conversation ${new Date().toISOString()}`;
  const conversation = await createConversation(conversationTitle);

  // Then add the message to the conversation
  const messageResponse = await addMessageToConversation(conversation.id, content);

  return {
    conversationId: conversation.id,
    message: messageResponse
  };
}