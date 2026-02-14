'use client';

import { useState, useEffect, useRef } from 'react';
import { authenticatedApi } from '@/lib/api';
import { Task } from '@/types/task';
import toast from 'react-hot-toast';

interface FormattedTask {
  id: string;
  title: string;
  description?: string;
  completionStatus: boolean;
  userId: string;
  createdAt: Date;
  updatedAt: Date;
  priority: 'low' | 'medium' | 'high';
  tags: string[];
}

interface TaskListProps {
  userId: string;
  onTasksUpdate?: (tasks: FormattedTask[]) => void;
}

// Define types for WebSocket events
interface TaskEvent {
  type: 'TASK_CREATED' | 'TASK_UPDATED' | 'TASK_DELETED' | 'AUTH_SUCCESS' | 'AUTH_ERROR';
  payload?: any;
  message?: string;
}

const TaskList = ({ userId, onTasksUpdate }: TaskListProps) => {
  const [taskList, setTaskList] = useState<FormattedTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingTaskId, setUpdatingTaskId] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [isWsConnected, setIsWsConnected] = useState(false);
  
  // New state for search, filter, and sort
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPriority, setFilterPriority] = useState<'all' | 'low' | 'medium' | 'high'>('all');
  const [filterTag, setFilterTag] = useState<string>('all');
  const [filterCompletion, setFilterCompletion] = useState<'all' | 'completed' | 'incomplete'>('all');
  const [sortBy, setSortBy] = useState<'createdAt' | 'updatedAt' | 'priority' | 'title'>('createdAt');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setLoading(true);

        // Build query parameters for search, filter, and sort
        const params = new URLSearchParams();
        if (searchTerm) params.append('search', searchTerm);
        if (filterPriority !== 'all') params.append('priority', filterPriority);
        if (filterTag !== 'all') params.append('tag', filterTag);
        if (filterCompletion !== 'all') {
          params.append('completed', filterCompletion === 'completed' ? 'true' : 'false');
        }
        params.append('sort', sortBy);
        params.append('order', sortOrder);

        // Fetch tasks from the backend API with query parameters
        const response = await authenticatedApi.get<Task[]>(`/tasks/?${params.toString()}`);
        const apiTasks = response.data;

        // Convert from API response to FormattedTask interface
        const tasksForDisplay = apiTasks.map((task: any) => ({
          id: task.id,
          title: task.title,
          description: task.description || undefined,
          completionStatus: task.completion_status,
          userId: task.user_id,
          createdAt: new Date(task.created_at),
          updatedAt: new Date(task.updated_at),
          priority: task.priority || 'medium',
          tags: task.tags || [],
        }));

        setTaskList(tasksForDisplay);

        // Notify parent component of the tasks
        if (onTasksUpdate) {
          onTasksUpdate(tasksForDisplay);
        }
      } catch (err: any) {
        setError('Failed to fetch tasks');
        console.error('Error fetching tasks:', err);
        toast.error('Failed to load tasks');
      } finally {
        setLoading(false);
      }
    };

    if (userId) {
      fetchTasks();
    }
  }, [userId, onTasksUpdate, searchTerm, filterPriority, filterTag, filterCompletion, sortBy, sortOrder]);

  // Set up WebSocket connection for real-time updates
  useEffect(() => {
    if (!userId) {
      // Don't establish WebSocket connection if userId is not available yet
      setIsWsConnected(false);
      return;
    }

    // Determine WebSocket URL based on environment
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const baseUrl = process.env.NEXT_PUBLIC_FASTAPI_API_URL?.replace(/^https?:\/\//, '');
    const wsUrl = `${protocol}//${baseUrl}/ws/${userId}`;

    console.log('Attempting to connect to WebSocket:', wsUrl);

    // Connect to WebSocket
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = async () => {
      console.log('WebSocket connected for real-time updates');
      setIsWsConnected(true);

      // Fetch the backend-compatible token from our exchange API route
      try {
        const response = await fetch('/api/auth/backend-token');
        const data = await response.json();

        if (data.backend_token) {
          console.log('Sending authentication to WebSocket');
          ws.send(JSON.stringify({ type: 'AUTH', token: data.backend_token }));
        } else {
          console.error('No backend token available for WebSocket authentication');
          setIsWsConnected(false); // Indicate connection failure
        }
      } catch (error) {
        console.error('Error getting backend token for WebSocket:', error);
        setIsWsConnected(false); // Indicate connection failure
      }
    };

    ws.onmessage = (event) => {
      try {
        const message: TaskEvent = JSON.parse(event.data);

        switch (message.type) {
          case 'TASK_CREATED':
            // Add the new task to the list
            const newTask: FormattedTask = {
              id: message.payload.id,
              title: message.payload.title,
              description: message.payload.description || undefined,
              completionStatus: message.payload.completion_status,
              userId: message.payload.user_id,
              createdAt: new Date(message.payload.created_at),
              updatedAt: new Date(message.payload.updated_at),
              priority: message.payload.priority || 'medium',
              tags: message.payload.tags || [],
            };
            setTaskList(prev => [...prev, newTask]);
            if (onTasksUpdate) onTasksUpdate([...taskList, newTask]);
            console.log('Task created via WebSocket:', newTask);
            break;

          case 'TASK_UPDATED':
            // Update the task in the list
            setTaskList(prev =>
              prev.map(task =>
                task.id === message.payload.id
                  ? {
                      ...task,
                      completionStatus: message.payload.completion_status ?? task.completionStatus,
                      title: message.payload.title ?? task.title,
                      description: message.payload.description ?? task.description,
                      priority: message.payload.priority ?? task.priority,
                      tags: message.payload.tags ?? task.tags,
                      updatedAt: new Date(message.payload.updated_at ?? task.updatedAt)
                    }
                  : task
              )
            );

            // Update the parent component
            const updatedTasks = taskList.map(task =>
              task.id === message.payload.id
                ? {
                    ...task,
                    completionStatus: message.payload.completion_status ?? task.completionStatus,
                    title: message.payload.title ?? task.title,
                    description: message.payload.description ?? task.description,
                    priority: message.payload.priority ?? task.priority,
                    tags: message.payload.tags ?? task.tags,
                    updatedAt: new Date(message.payload.updated_at ?? task.updatedAt)
                  }
                : task
            );
            if (onTasksUpdate) onTasksUpdate(updatedTasks);
            console.log('Task updated via WebSocket:', message.payload.id);
            break;

          case 'TASK_DELETED':
            // Remove the task from the list
            const filteredTasks = taskList.filter(task => task.id !== message.payload.id);
            setTaskList(filteredTasks);
            if (onTasksUpdate) onTasksUpdate(filteredTasks);
            console.log('Task deleted via WebSocket:', message.payload.id);
            break;

          case 'AUTH_SUCCESS':
            console.log('WebSocket authentication successful');
            setIsWsConnected(true); // Confirm successful authentication
            break;

          case 'AUTH_ERROR':
            console.error('WebSocket authentication error:', message.message);
            setIsWsConnected(false); // Indicate authentication failure
            break;

          default:
            console.warn('Unknown WebSocket message type:', message.type);
        }
      } catch (error) {
        console.error('Error processing WebSocket message:', error);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsWsConnected(false);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsWsConnected(false); // Indicate connection failure
    };

    // Clean up WebSocket connection when component unmounts
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [userId, taskList, onTasksUpdate]);

  // Set up periodic refresh as a fallback when WebSocket is not connected
  useEffect(() => {
    if (!userId) return;

    // When WebSocket is not connected, refresh periodically
    if (!isWsConnected) {
      const refreshInterval = setInterval(() => {
        const fetchTasks = async () => {
          try {
            // Only fetch if we're not already loading
            if (!loading) {
              // Build query parameters for search, filter, and sort
              const params = new URLSearchParams();
              if (searchTerm) params.append('search', searchTerm);
              if (filterPriority !== 'all') params.append('priority', filterPriority);
              if (filterTag !== 'all') params.append('tag', filterTag);
              if (filterCompletion !== 'all') {
                params.append('completed', filterCompletion === 'completed' ? 'true' : 'false');
              }
              params.append('sort', sortBy);
              params.append('order', sortOrder);

              // Fetch tasks from the backend API with query parameters
              const response = await authenticatedApi.get<Task[]>(`/tasks/?${params.toString()}`);
              const apiTasks = response.data;

              // Convert from API response to FormattedTask interface
              const tasksForDisplay = apiTasks.map((task: any) => ({
                id: task.id,
                title: task.title,
                description: task.description || undefined,
                completionStatus: task.completion_status,
                userId: task.user_id,
                createdAt: new Date(task.created_at),
                updatedAt: new Date(task.updated_at),
                priority: task.priority || 'medium',
                tags: task.tags || [],
              }));

              setTaskList(tasksForDisplay);

              // Notify parent component of the tasks
              if (onTasksUpdate) {
                onTasksUpdate(tasksForDisplay);
              }
            }
          } catch (err: any) {
            console.error('Error fetching tasks:', err);
            // Don't show error toast for background refresh to avoid annoying users
          }
        };

        fetchTasks();
      }, 10000); // Refresh every 10 seconds when WebSocket is not connected

      // Clean up the interval when the component unmounts
      return () => {
        clearInterval(refreshInterval);
      };
    }
  }, [userId, onTasksUpdate, loading, isWsConnected, searchTerm, filterPriority, filterTag, filterCompletion, sortBy, sortOrder]);

  const toggleTaskCompletion = async (taskId: string, currentStatus: boolean) => {
    setUpdatingTaskId(taskId);

    try {
      const response = await authenticatedApi.patch<Task>(`/tasks/${taskId}/complete`);
      const data = response.data as { completion_status: boolean; updated_at: string };

      // Update the UI with the response from the API
      setTaskList(prev => prev.map(task =>
        task.id === taskId
          ? {
            ...task,
            completionStatus: data.completion_status,
            updatedAt: new Date(data.updated_at)
          }
          : task
      ));

      toast.success(currentStatus ? 'Task marked as incomplete' : 'Task completed!');
    } catch (error) {
      console.error('Error toggling task completion:', error);
      toast.error('Failed to update task status');
    } finally {
      setUpdatingTaskId(null);
    }
  };

  const deleteTask = async (taskId: string) => {
    if (!confirm('Are you sure you want to delete this task? This action cannot be undone.')) {
      return;
    }

    try {
      await authenticatedApi.delete(`/tasks/${taskId}`);

      // Remove the task from the UI
      setTaskList(prev => prev.filter(task => task.id !== taskId));

      // Notify parent component of the update
      if (onTasksUpdate) {
        const tasksForParent = taskList.filter(task => task.id !== taskId);
        onTasksUpdate(tasksForParent);
      }

      toast.success('Task deleted successfully');
    } catch (error) {
      console.error('Error deleting task:', error);
      toast.error('Failed to delete task');
    }
  };

  // Get all unique tags from tasks for filtering
  const allTags = Array.from(new Set(taskList.flatMap(task => task.tags)));

  if (loading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/30 border border-red-700 rounded-lg p-4 text-red-300">
        Error: {error}
      </div>
    );
  }

  return (
    <div>
      {/* Controls for search, filter, and sort */}
      <div className="mb-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <label htmlFor="search" className="block text-sm font-medium text-gray-300 mb-1">
            Search
          </label>
          <input
            type="text"
            id="search"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition text-white placeholder-gray-500"
            placeholder="Search tasks..."
          />
        </div>

        <div>
          <label htmlFor="filterPriority" className="block text-sm font-medium text-gray-300 mb-1">
            Priority
          </label>
          <select
            id="filterPriority"
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value as 'all' | 'low' | 'medium' | 'high')}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition text-white"
          >
            <option value="all">All Priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div>
          <label htmlFor="filterTag" className="block text-sm font-medium text-gray-300 mb-1">
            Tag
          </label>
          <select
            id="filterTag"
            value={filterTag}
            onChange={(e) => setFilterTag(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition text-white"
          >
            <option value="all">All Tags</option>
            {allTags.map(tag => (
              <option key={tag} value={tag}>{tag}</option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="filterCompletion" className="block text-sm font-medium text-gray-300 mb-1">
            Status
          </label>
          <select
            id="filterCompletion"
            value={filterCompletion}
            onChange={(e) => setFilterCompletion(e.target.value as 'all' | 'completed' | 'incomplete')}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition text-white"
          >
            <option value="all">All Statuses</option>
            <option value="incomplete">Incomplete</option>
            <option value="completed">Completed</option>
          </select>
        </div>
      </div>

      <div className="mb-4 flex flex-wrap gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">Sort By</label>
          <div className="flex space-x-2">
            <button
              onClick={() => setSortBy('createdAt')}
              className={`px-3 py-1.5 text-sm rounded-lg ${
                sortBy === 'createdAt'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Created
            </button>
            <button
              onClick={() => setSortBy('updatedAt')}
              className={`px-3 py-1.5 text-sm rounded-lg ${
                sortBy === 'updatedAt'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Updated
            </button>
            <button
              onClick={() => setSortBy('priority')}
              className={`px-3 py-1.5 text-sm rounded-lg ${
                sortBy === 'priority'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Priority
            </button>
            <button
              onClick={() => setSortBy('title')}
              className={`px-3 py-1.5 text-sm rounded-lg ${
                sortBy === 'title'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Title
            </button>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">Order</label>
          <div className="flex space-x-2">
            <button
              onClick={() => setSortOrder('asc')}
              className={`px-3 py-1.5 text-sm rounded-lg ${
                sortOrder === 'asc'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Ascending
            </button>
            <button
              onClick={() => setSortOrder('desc')}
              className={`px-3 py-1.5 text-sm rounded-lg ${
                sortOrder === 'desc'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Descending
            </button>
          </div>
        </div>
      </div>

      {/* Show WebSocket connection status */}
      <div className="flex items-center justify-end mb-2">
        <span className={`text-xs flex items-center ${isWsConnected ? 'text-green-400' : 'text-yellow-400'}`}>
          <span className={`mr-1.5 h-2 w-2 rounded-full ${isWsConnected ? 'bg-green-400' : 'bg-yellow-400'} animate-pulse`}></span>
          {isWsConnected ? 'Real-time sync: Connected' : 'Real-time sync: Connecting...'}
        </span>
      </div>

      {taskList.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-500 mb-4">No tasks yet</div>
          <p className="text-gray-400">Add your first task using the form on the left</p>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="text-sm text-gray-400 mb-2">
            Showing <span className="font-medium text-white">{taskList.length}</span> {taskList.length === 1 ? 'task' : 'tasks'}
            {taskList.filter(t => t.completionStatus).length > 0 && (
              <span className="ml-2">
                (<span className="text-green-400">{taskList.filter(t => t.completionStatus).length}</span> completed)
              </span>
            )}
          </div>

          {taskList.map((task) => (
            <div
              key={task.id}
              className={`p-4 rounded-lg border transition-all duration-200 ${
                task.completionStatus
                  ? 'bg-green-900/10 border-green-800/50 hover:border-green-700/70'
                  : 'bg-gray-800/50 border-gray-700/50 hover:border-gray-600/70'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <button
                    onClick={() => toggleTaskCompletion(task.id, task.completionStatus)}
                    disabled={updatingTaskId === task.id}
                    className={`mt-1 shrink-0 h-5 w-5 rounded-full border flex items-center justify-center transition-all duration-200 ${
                      task.completionStatus
                        ? 'bg-green-600 border-green-600 transform scale-110'
                        : 'border-gray-400 hover:border-gray-300'
                    }`}
                    aria-label={task.completionStatus ? "Mark as incomplete" : "Mark as complete"}
                    title={task.completionStatus ? "Mark as incomplete" : "Mark as complete"}
                  >
                    {task.completionStatus && (
                      <svg className="h-3 w-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                  </button>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-baseline">
                      <h3 className={`font-medium ${task.completionStatus ? 'text-green-300 line-through' : 'text-white'
                        }`}>
                        {task.title}
                      </h3>
                      <div className="ml-2 flex items-center">
                        <span className="text-xs bg-gray-700 text-gray-300 px-2 py-0.5 rounded">
                          ID: {task.id.substring(0, 8)}...
                        </span>
                        <button
                          onClick={() => navigator.clipboard.writeText(task.id)}
                          className="ml-1 text-gray-400 hover:text-white transition-colors"
                          title="Copy full ID to clipboard"
                          aria-label={`Copy full ID for task ${task.title}`}
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                        </button>
                      </div>
                    </div>
                    
                    {task.description && (
                      <p className={`mt-1 text-sm ${task.completionStatus ? 'text-green-400/70' : 'text-gray-400'
                        }`}>
                        {task.description}
                      </p>
                    )}
                    
                    <div className="mt-2 flex flex-wrap gap-2">
                      {/* Priority badge */}
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        task.priority === 'low' 
                          ? 'bg-green-900/30 text-green-300 border border-green-800/50' 
                          : task.priority === 'medium' 
                            ? 'bg-yellow-900/30 text-yellow-300 border border-yellow-800/50' 
                            : 'bg-red-900/30 text-red-300 border border-red-800/50'
                      }`}>
                        {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
                      </span>
                      
                      {/* Tags */}
                      {task.tags && task.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {task.tags.map((tag, idx) => (
                            <span 
                              key={idx} 
                              className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-900/30 text-blue-300 border border-blue-800/50"
                            >
                              #{tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    <div className="mt-2 text-xs text-gray-500 flex items-center">
                      <svg className="mr-1 h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Updated: {task.updatedAt.toLocaleDateString()} • Created: {task.createdAt.toLocaleDateString()}
                    </div>
                  </div>
                </div>

                <div className="flex space-x-2 ml-4">
                  <button
                    onClick={() => deleteTask(task.id)}
                    disabled={updatingTaskId === task.id}
                    className="text-gray-500 hover:text-red-400 transition-colors disabled:opacity-50 cursor-pointer p-1 rounded-md hover:bg-red-900/30"
                    aria-label="Delete task"
                    title="Delete task"
                  >
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TaskList;