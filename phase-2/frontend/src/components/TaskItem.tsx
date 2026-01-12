'use client';

import { useState } from 'react';
import { authenticatedApi } from '@/lib/api';
import { Task } from '@/types/task';

interface TaskItemProps {
  task: Task;
  onUpdate: (updatedTask: Task) => void;
  onDelete: (taskId: string) => void;
}

export default function TaskItem({ task, onUpdate, onDelete }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState(task.title);
  const [description, setDescription] = useState(task.description || '');
  const [isLoading, setIsLoading] = useState(false);

  const handleToggleComplete = async () => {
    setIsLoading(true);
    try {
      const response = await authenticatedApi.patch<Task>(`/tasks/${task.id}/complete`);
      onUpdate({ ...task, completion_status: (response.data as Task).completion_status });
    } catch (error) {
      console.error('Error toggling task completion:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveEdit = async () => {
    setIsLoading(true);
    try {
      const response = await authenticatedApi.put<Task>(`/tasks/${task.id}`, {
        title,
        description,
        completion_status: task.completion_status,
      });
      onUpdate(response.data as Task);
      setIsEditing(false);
    } catch (error) {
      console.error('Error updating task:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    setIsLoading(true);
    try {
      await authenticatedApi.delete(`/tasks/${task.id}`);
      onDelete(task.id);
    } catch (error) {
      console.error('Error deleting task:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`p-4 mb-3 rounded-lg border ${task.completion_status ? 'bg-green-50' : 'bg-white'} shadow-sm`}>
      {isEditing ? (
        <div>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full p-2 mb-2 border rounded"
            placeholder="Task title"
            disabled={isLoading}
          />
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full p-2 mb-2 border rounded"
            placeholder="Task description"
            disabled={isLoading}
          />
          <div className="flex justify-end space-x-2">
            <button
              onClick={() => setIsEditing(false)}
              className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              onClick={handleSaveEdit}
              className={`px-3 py-1 text-white rounded ${isLoading ? 'bg-blue-400' : 'bg-blue-500 hover:bg-blue-600'}`}
              disabled={isLoading}
            >
              {isLoading ? 'Saving...' : 'Save'}
            </button>
          </div>
        </div>
      ) : (
        <div>
          <div className="flex items-start">
            <input
              type="checkbox"
              checked={task.completion_status}
              onChange={handleToggleComplete}
              className="mt-1 mr-3"
              disabled={isLoading}
            />
            <div className="flex-1">
              <h3 className={`text-lg ${task.completion_status ? 'line-through text-gray-500' : ''}`}>
                {task.title}
              </h3>
              {task.description && (
                <p className={`mt-1 ${task.completion_status ? 'line-through text-gray-500' : 'text-gray-600'}`}>
                  {task.description}
                </p>
              )}
              <p className="text-xs text-gray-400 mt-2">
                Created: {new Date(task.created_at).toLocaleString()}
              </p>
            </div>
            <div className="flex space-x-2 ml-2">
              <button
                onClick={() => setIsEditing(!isLoading)}
                className={`text-blue-500 ${isLoading ? 'opacity-50 cursor-not-allowed' : 'hover:text-blue-700'}`}
                disabled={isLoading}
              >
                {isLoading ? 'Processing...' : 'Edit'}
              </button>
              <button
                onClick={handleDelete}
                className={`text-red-500 ${isLoading ? 'opacity-50 cursor-not-allowed' : 'hover:text-red-700'}`}
                disabled={isLoading}
              >
                {isLoading ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}