import Link from 'next/link';
import { FaCheckCircle, FaSyncAlt, FaLock, FaChartLine } from 'react-icons/fa';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      {/* Navigation */}
      <nav className="flex items-center justify-between p-6">
        <div className="text-2xl font-bold bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
          TaskFlow
        </div>
        <div className="flex space-x-6">
          <Link href="/login" className="hover:text-blue-400 transition-colors">
            Sign In
          </Link>
          <Link href="/signup" className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition-colors">
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 md:py-24 flex flex-col items-center text-center">
        <h1 className="text-4xl md:text-6xl font-bold max-w-3xl leading-tight">
          Streamline Your Life with <span className="bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">Smart Task Management</span>
        </h1>
        <p className="mt-6 text-xl text-gray-300 max-w-2xl">
          The ultimate todo app designed for productivity enthusiasts who demand both beauty and functionality.
        </p>
        <div className="mt-10 flex flex-col sm:flex-row gap-4">
          <Link
            href="/signup"
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 px-8 rounded-lg transition-all transform hover:scale-105 shadow-lg"
          >
            Start Free Trial
          </Link>
          <Link
            href="#features"
            className="bg-gray-800 hover:bg-gray-700 text-white font-semibold py-3 px-8 rounded-lg transition-all border border-gray-700"
          >
            Learn More
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-16 bg-gray-800/50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-16">Powerful Features for Maximum Productivity</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Feature 1 */}
            <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700 hover:border-blue-500 transition-all">
              <div className="text-blue-500 text-3xl mb-4">
                <FaCheckCircle />
              </div>
              <h3 className="text-xl font-semibold mb-2">Smart Task Organization</h3>
              <p className="text-gray-400">
                Intuitive categorization and tagging system to keep your tasks organized and accessible.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700 hover:border-blue-500 transition-all">
              <div className="text-blue-500 text-3xl mb-4">
                <FaSyncAlt />
              </div>
              <h3 className="text-xl font-semibold mb-2">Real-time Sync</h3>
              <p className="text-gray-400">
                Access your tasks from anywhere with seamless synchronization across all devices.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700 hover:border-blue-500 transition-all">
              <div className="text-blue-500 text-3xl mb-4">
                <FaLock />
              </div>
              <h3 className="text-xl font-semibold mb-2">Military-grade Security</h3>
              <p className="text-gray-400">
                End-to-end encryption keeps your personal and professional data completely secure.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700 hover:border-blue-500 transition-all">
              <div className="text-blue-500 text-3xl mb-4">
                <FaChartLine />
              </div>
              <h3 className="text-xl font-semibold mb-2">Productivity Analytics</h3>
              <p className="text-gray-400">
                Detailed insights into your habits to help you optimize your workflow.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4 text-center max-w-3xl">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Transform Your Productivity?
          </h2>
          <p className="text-xl text-gray-300 mb-10">
            Join thousands of users who have revolutionized their task management workflow.
          </p>
          <Link
            href="/signup"
            className="inline-block bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold py-4 px-10 rounded-lg transition-all transform hover:scale-105 shadow-lg text-lg"
          >
            Get Started Today - It's Free
          </Link>
          <p className="mt-4 text-gray-400">
            No credit card required. Free forever plan available.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-10">
        <div className="container mx-auto px-4 text-center text-gray-400">
          <p>© {new Date().getFullYear()} TaskFlow. All rights reserved.</p>
          <div className="mt-4 flex justify-center space-x-6">
            <Link href="#" className="hover:text-white transition-colors">Terms</Link>
            <Link href="#" className="hover:text-white transition-colors">Privacy</Link>
            <Link href="#" className="hover:text-white transition-colors">Contact</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}