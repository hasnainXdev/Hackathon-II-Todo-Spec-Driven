'use client';

import Navbar from '../components/Navbar';
import { FaCheckCircle, FaLightbulb, FaSyncAlt, FaChartBar, FaLock, FaHeadset } from 'react-icons/fa';

export default function Home() {
  const features = [
    {
      icon: <FaLightbulb className="h-8 w-8 text-blue-400" />,
      title: "AI-Powered Suggestions",
      description: "Get intelligent task suggestions based on your habits and priorities."
    },
    {
      icon: <FaSyncAlt className="h-8 w-8 text-green-400" />,
      title: "Real-Time Sync",
      description: "Access your tasks from anywhere with seamless synchronization across devices."
    },
    {
      icon: <FaChartBar className="h-8 w-8 text-purple-400" />,
      title: "Productivity Analytics",
      description: "Track your progress with insightful analytics and productivity reports."
    },
    {
      icon: <FaLock className="h-8 w-8 text-yellow-400" />,
      title: "Secure & Private",
      description: "Military-grade encryption keeps your data secure and private at all times."
    },
    {
      icon: <FaHeadset className="h-8 w-8 text-red-400" />,
      title: "24/7 Support",
      description: "Our dedicated support team is always ready to assist you."
    },
    {
      icon: <FaCheckCircle className="h-8 w-8 text-teal-400" />,
      title: "Smart Organization",
      description: "Automatically categorize and prioritize tasks with smart algorithms."
    }
  ];

  const testimonials = [
    {
      name: "Alex Johnson",
      role: "Product Manager",
      quote: "This app transformed how our team manages projects. The AI suggestions are incredibly accurate!"
    },
    {
      name: "Sarah Williams",
      role: "Freelance Designer",
      quote: "I've tried many task managers, but none come close to this level of intelligence and ease of use."
    },
    {
      name: "Michael Chen",
      role: "Software Engineer",
      quote: "The real-time sync and collaboration features have made remote work so much easier."
    }
  ];

  const faqs = [
    {
      question: "How secure is my data?",
      answer: "We use end-to-end encryption and comply with industry security standards to protect your data."
    },
    {
      question: "Can I use this offline?",
      answer: "Yes, our app supports offline mode and will sync when you reconnect to the internet."
    },
    {
      question: "Is there a free trial?",
      answer: "Absolutely! You can try all premium features for 14 days with no commitment."
    },
    {
      question: "How does the AI assistance work?",
      answer: "Our AI analyzes your task patterns and suggests optimizations, deadlines, and priorities."
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-900 to-gray-800 text-gray-100">
      <Navbar />

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6 leading-tight">
              Transform Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-500">Productivity</span> with AI
            </h1>
            <p className="text-gray-300 text-lg md:text-xl max-w-3xl mx-auto mb-10">
              The ultimate AI-powered task manager that learns your habits, predicts your needs, and helps you achieve more with less effort.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <a
                href="/signup"
                className="bg-gradient-to-r from-blue-600 to-indigo-700 hover:from-blue-700 hover:to-indigo-800 text-white font-semibold py-4 px-8 rounded-lg transition duration-300 transform hover:scale-105 shadow-lg shadow-blue-500/20"
              >
                Get Started Free
              </a>
              <a
                href="/demo"
                className="bg-gray-800 hover:bg-gray-700 text-white font-semibold py-4 px-8 rounded-lg transition duration-300 border border-gray-700"
              >
                Watch Demo
              </a>
            </div>
          </div>

          <div className="mt-16 rounded-2xl overflow-hidden shadow-2xl border border-gray-700/50 max-w-5xl mx-auto">
            <div className="bg-gradient-to-br from-gray-800 to-gray-900 p-1">
              <div className="bg-gray-900 p-4">
                <div className="flex space-x-2">
                  <div className="w-3 h-3 rounded-full bg-red-500"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                </div>
              </div>
              <div className="p-6 md:p-10 bg-gray-800/50 backdrop-blur-sm">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-4">
                    <div className="h-4 bg-gray-700 rounded w-3/4"></div>
                    <div className="h-4 bg-gray-700 rounded"></div>
                    <div className="h-4 bg-gray-700 rounded w-5/6"></div>
                    <div className="h-12 bg-gradient-to-r from-blue-600/20 to-indigo-700/20 rounded-lg mt-6 border border-gray-700 flex items-center px-4">
                      <div className="h-3 w-3 rounded-full bg-green-400 mr-2"></div>
                      <div className="h-4 bg-gray-600 rounded w-1/2"></div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div className="h-32 bg-gray-700/30 rounded-lg border border-gray-700 flex items-center justify-center">
                      <div className="text-center">
                        <div className="h-8 w-8 bg-blue-500/20 rounded-full mx-auto mb-2 flex items-center justify-center">
                          <FaLightbulb className="text-blue-400" />
                        </div>
                        <div className="h-4 bg-gray-600 rounded w-3/4 mx-auto"></div>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-2">
                      <div className="h-16 bg-gray-700/30 rounded-lg border border-gray-700"></div>
                      <div className="h-16 bg-gray-700/30 rounded-lg border border-gray-700"></div>
                      <div className="h-16 bg-gray-700/30 rounded-lg border border-gray-700"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-900/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Powerful Features</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Everything you need to stay organized, productive, and ahead of your goals
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="bg-gray-800/80 backdrop-blur-sm rounded-xl p-6 shadow-xl border border-gray-700/50 hover:border-blue-500/30 transition-all duration-300 hover:-translate-y-1"
              >
                <div className="mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-gray-300">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Trusted by Thousands</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Join our community of satisfied users who have transformed their productivity
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div
                key={index}
                className="bg-gray-800/80 backdrop-blur-sm rounded-xl p-6 shadow-xl border border-gray-700/50"
              >
                <div className="flex items-center mb-4">
                  <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold mr-3">
                    {testimonial.name.charAt(0)}
                  </div>
                  <div>
                    <h4 className="font-semibold text-white">{testimonial.name}</h4>
                    <p className="text-gray-400 text-sm">{testimonial.role}</p>
                  </div>
                </div>
                <p className="text-gray-300 italic">"{testimonial.quote}"</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-blue-900/30 to-indigo-900/30">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">Ready to Transform Your Productivity?</h2>
          <p className="text-gray-300 text-lg mb-8 max-w-2xl mx-auto">
            Join thousands of users who have revolutionized their task management with our AI-powered platform.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <a
              href="/signup"
              className="bg-gradient-to-r from-blue-600 to-indigo-700 hover:from-blue-700 hover:to-indigo-800 text-white font-semibold py-4 px-8 rounded-lg transition duration-300 transform hover:scale-105"
            >
              Start Free Trial
            </a>
            <a
              href="/pricing"
              className="bg-gray-800 hover:bg-gray-700 text-white font-semibold py-4 px-8 rounded-lg transition duration-300 border border-gray-700"
            >
              View Pricing
            </a>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Frequently Asked Questions</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Everything you need to know about the product
            </p>
          </div>

          <div className="space-y-6">
            {faqs.map((faq, index) => (
              <div
                key={index}
                className="bg-gray-800/80 backdrop-blur-sm rounded-xl p-6 shadow-xl border border-gray-700/50"
              >
                <h3 className="text-lg font-semibold text-white mb-2">{faq.question}</h3>
                <p className="text-gray-300">{faq.answer}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 border-t border-gray-800 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-xl font-bold text-blue-400 mb-4">TodoApp</h3>
              <p className="text-gray-400">
                The smartest way to manage your tasks with AI assistance.
              </p>
            </div>

            <div>
              <h4 className="text-lg font-semibold text-white mb-4">Product</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Features</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Integrations</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Roadmap</a></li>
              </ul>
            </div>

            <div>
              <h4 className="text-lg font-semibold text-white mb-4">Resources</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Documentation</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Guides</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Support</a></li>
              </ul>
            </div>

            <div>
              <h4 className="text-lg font-semibold text-white mb-4">Company</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Careers</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Contact</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Partners</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-500 text-sm">© 2026 TodoApp. All rights reserved.</p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <span className="sr-only">Twitter</span>
                <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                </svg>
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <span className="sr-only">GitHub</span>
                <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                </svg>
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <span className="sr-only">LinkedIn</span>
                <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}