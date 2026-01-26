'use client';

import TaskList from '@/components/TaskList';
import TaskForm from '@/components/TaskForm';
import Navbar from '@/components/Navbar';
import ChatInterface from '@/components/ChatInterface';
import authClient from '../../lib/auth-client';
import { useEffect, useState, useCallback } from 'react';
import { Task } from '@/types/task';

export default function DashboardPage() {
  const { data: session, isPending } = authClient.useSession();
  const [userId, setUserId] = useState<string | null>(null);
  const [tasks, setTasks] = useState<FormattedTask[]>([]);

  useEffect(() => {
    if (session?.user?.id) {
      setUserId(session.user.id);
    }
  }, [session]);

  interface FormattedTask {
    id: string;
    title: string;
    description?: string;
    completionStatus: boolean;
    userId: string;
    createdAt: Date;
    updatedAt: Date;
  }

  const handleTaskAdded = (newTask: Task) => {
    // Convert the new task to match our internal format
    const formattedTask: FormattedTask = {
      id: newTask.id,
      title: newTask.title,
      description: newTask.description,
      completionStatus: newTask.completion_status,
      userId: newTask.user_id,
      createdAt: new Date(newTask.created_at),
      updatedAt: new Date(newTask.updated_at)
    };
    setTasks(prev => [...prev, formattedTask]);
  };

  // Function to force refresh the task list
  const refreshTasks = useCallback(() => {
    // We'll trigger a refresh by updating the key of the TaskList component
    // This will cause it to remount and fetch fresh data
    setTasks([]); // Clear current tasks
    // The useEffect in TaskList will automatically fetch fresh data
  }, []);

  // If loading, show loading state
  if (isPending) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900 text-white">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  // If not authenticated, redirect to login (this would normally be handled by a router)
  if (!session?.user) {
    window.location.href = "/login";
    return null; // Prevent rendering while redirecting
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-900 to-gray-800 text-gray-100">
      <Navbar />
      <div className="pt-24 pb-12 px-4 sm:px-6 lg:px-8"> {/* pt-24 to account for fixed navbar */}
        <div className="max-w-7xl mx-auto">
          <div className="mb-10">
            <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
            <p className="text-gray-400">Manage your tasks efficiently</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-1">
              <div className="bg-gray-800/80 backdrop-blur-sm rounded-xl p-6 shadow-xl border border-gray-700/50">
                <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
                  <svg className="mr-2 h-5 w-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Add New Task
                </h2>
                <TaskForm onTaskAdded={handleTaskAdded} />
              </div>
            </div>

            <div className="lg:col-span-2 grid grid-rows-2 gap-8">
              <div className="bg-gray-800/80 backdrop-blur-sm rounded-xl p-6 shadow-xl border border-gray-700/50">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-white flex items-center">
                    <svg className="mr-2 h-5 w-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    Your Tasks
                  </h2>
                  <span className="bg-gradient-to-r from-blue-900 to-indigo-900 text-blue-300 text-xs font-medium px-3 py-1 rounded-full flex items-center">
                    <svg className="mr-1 h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'}
                  </span>
                </div>

                {userId ? (
                  <TaskList userId={userId} onTasksUpdate={setTasks} />
                ) : (
                  <div className="flex justify-center items-center h-32">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
                  </div>
                )}
              </div>

              <div className="bg-gray-800/80 backdrop-blur-sm rounded-xl p-6 shadow-xl border border-gray-700/50 flex flex-col h-full">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-white flex items-center">
                    <svg className="mr-2 h-5 w-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                    AI Task Assistant
                  </h2>
                </div>
                <div className="flex-1 min-h-[400px]">
                  <ChatInterface />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}