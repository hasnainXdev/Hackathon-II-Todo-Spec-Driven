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
 * Creates a new task
 */
export async function createTask(title: string, description?: string, priority?: string, tags?: string[], dueDate?: string, recurrenceRule?: string) {
  const backendToken = await getBackendToken();

  const response = await fetch(`${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/tasks`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${backendToken}`,
    },
    body: JSON.stringify({
      title,
      description,
      priority,
      tags,
      due_date: dueDate,
      recurrence_rule: recurrenceRule
    }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

/**
 * Gets all tasks for a user
 */
export async function getTasks(priority?: string, completed?: boolean, tag?: string, sortBy?: string, order?: string, search?: string) {
  const backendToken = await getBackendToken();
  
  // Build query parameters
  const params = new URLSearchParams();
  if (priority) params.append('priority', priority);
  if (completed !== undefined) params.append('completed', completed.toString());
  if (tag) params.append('tag', tag);
  if (sortBy) params.append('sort_by', sortBy);
  if (order) params.append('order', order);
  if (search) params.append('search', search);

  const queryString = params.toString();
  const url = `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/tasks${queryString ? '?' + queryString : ''}`;

  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${backendToken}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

/**
 * Gets a specific task by ID
 */
export async function getTaskById(taskId: string) {
  const backendToken = await getBackendToken();

  const response = await fetch(`${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/tasks/${taskId}`, {
    headers: {
      'Authorization': `Bearer ${backendToken}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

/**
 * Updates a task
 */
export async function updateTask(taskId: string, updates: Partial<{
  title: string;
  description: string;
  priority: string;
  tags: string[];
  due_date: string;
  completed: boolean;
}>) {
  const backendToken = await getBackendToken();

  const response = await fetch(`${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/tasks/${taskId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${backendToken}`,
    },
    body: JSON.stringify(updates),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

/**
 * Deletes a task
 */
export async function deleteTask(taskId: string) {
  const backendToken = await getBackendToken();

  const response = await fetch(`${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/tasks/${taskId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${backendToken}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return response.status === 204; // DELETE returns 204 No Content
}

/**
 * Completes a task
 */
export async function completeTask(taskId: string) {
  const backendToken = await getBackendToken();

  const response = await fetch(`${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/tasks/${taskId}/complete`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${backendToken}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

/**
 * Gets the history of events for a task
 */
export async function getTaskHistory(taskId: string) {
  const backendToken = await getBackendToken();

  const response = await fetch(`${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/tasks/${taskId}/history`, {
    headers: {
      'Authorization': `Bearer ${backendToken}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

/**
 * Processes a chat command for task management
 */
export async function processChatCommand(command: string) {
  const backendToken = await getBackendToken();

  const response = await fetch(`${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${backendToken}`,
    },
    body: JSON.stringify({
      command,
      userId: "" // Will be populated by the backend from the auth token
    }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return await response.json();
}