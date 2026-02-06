'use client';

import { useState } from 'react';
import { createTask } from '@/lib/event-driven-api-client';
import { Task } from '@/types/task';
import toast from 'react-hot-toast';

interface TaskFormProps {
  onTaskAdded: (task: Task) => void;
}

export default function TaskForm({ onTaskAdded }: TaskFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      toast.error('Title is required');
      return;
    }

    if (title.trim().length > 200) {
      toast.error('Title is too long (max 200 characters)');
      return;
    }

    if (description.length > 1000) {
      toast.error('Description is too long (max 1000 characters)');
      return;
    }

    setIsLoading(true);
    try {
      const response = await createTask(title.trim(), description.trim());

      // The API response should already match the Task interface
      onTaskAdded(response as Task);
      setTitle('');
      setDescription('');
      toast.success('Task created successfully!');
    } catch (error: any) {
      console.error('Error creating task:', error);
      toast.error(error.response?.data?.detail || 'Failed to create task');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-300 mb-2">
          Task Title *
        </label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className={`w-full px-4 py-3 bg-gray-700 border ${
            title.trim().length > 180 ? 'border-yellow-500' :
            title.trim().length > 200 ? 'border-red-500' : 'border-gray-600'
          } rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition text-white placeholder-gray-500`}
          placeholder="What needs to be done?"
          maxLength={200}
          disabled={isLoading}
          aria-required="true"
          aria-describedby="title-count"
        />
        <div id="title-count" className="text-right text-xs text-gray-400 mt-1">
          {title.length}/200
          {title.trim().length > 180 && title.trim().length <= 200 && (
            <span className="text-yellow-400 ml-1">Getting close...</span>
          )}
          {title.trim().length > 200 && (
            <span className="text-red-400 ml-1">Too long!</span>
          )}
        </div>
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-300 mb-2">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition text-white placeholder-gray-500 resize-none"
          placeholder="Add details (optional)"
          rows={4}
          maxLength={1000}
          disabled={isLoading}
          aria-describedby="description-count"
        />
        <div id="description-count" className="text-right text-xs text-gray-400 mt-1">
          {description.length}/1000
          {description.length > 900 && description.length <= 1000 && (
            <span className="text-yellow-400 ml-1">Getting close...</span>
          )}
          {description.length > 1000 && (
            <span className="text-red-400 ml-1">Too long!</span>
          )}
        </div>
      </div>

      <button
        type="submit"
        className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-medium py-3 px-4 rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center cursor-pointer transform hover:scale-[1.02] active:scale-[0.98]"
        disabled={isLoading}
        aria-busy={isLoading}
      >
        {isLoading ? (
          <>
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Adding Task...
          </>
        ) : (
          <>
            <svg className="-ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Add New Task
          </>
        )}
      </button>
    </form>
  );
}