'use client';

import Navbar from '../components/Navbar';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-900 to-gray-800 text-gray-100">
      <Navbar />
      <div className="pt-24 pb-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-10 text-center">
            <h1 className="text-4xl font-bold text-white mb-4">AI-Powered Todo Assistant</h1>
            <p className="text-gray-400 text-lg">Manage your tasks with the power of AI</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
            <div className="bg-gray-800/80 backdrop-blur-sm rounded-xl p-6 shadow-xl border border-gray-700/50">
              <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
                <svg className="mr-2 h-5 w-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                Smart Task Management
              </h2>
              <p className="text-gray-300">
                Organize your tasks efficiently with our intelligent system that learns from your habits and priorities.
              </p>
            </div>

            <div className="bg-gray-800/80 backdrop-blur-sm rounded-xl p-6 shadow-xl border border-gray-700/50">
              <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
                <svg className="mr-2 h-5 w-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
                AI-Powered Assistance
              </h2>
              <p className="text-gray-300">
                Get intelligent suggestions and automate routine tasks with our AI assistant that understands natural language.
              </p>
            </div>
          </div>

          <div className="bg-gray-800/80 backdrop-blur-sm rounded-xl p-8 shadow-xl border border-gray-700/50 text-center">
            <h2 className="text-2xl font-bold text-white mb-4">Ready to boost your productivity?</h2>
            <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
              Join thousands of users who have transformed their task management with our AI-powered platform.
            </p>
            <a
              href="/dashboard"
              className="inline-block bg-gradient-to-r from-blue-600 to-indigo-700 hover:from-blue-700 hover:to-indigo-800 text-white font-semibold py-3 px-8 rounded-lg transition duration-300 transform hover:scale-105"
            >
              Go to Dashboard
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}