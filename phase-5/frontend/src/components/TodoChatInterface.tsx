import { useState, useEffect, useRef } from 'react';
import authClient from '@/lib/auth-client';
import { FaPaperPlane, FaRobot, FaUser, FaVolumeUp, FaKeyboard } from 'react-icons/fa';
import {
  createConversationWithMessage,
  addMessageToConversation,
  getConversationMessages
} from '@/lib/api-client';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt: string;
}

export default function TodoChatInterface() {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [fontSize, setFontSize] = useState<'normal' | 'large' | 'largest'>('normal');
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const { data: session } = authClient.useSession();
  const eventSourceRef = useRef<EventSource | null>(null);

  // Scroll to bottom of messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Clean up EventSource on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    // Add user message to UI immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      createdAt: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Create a new conversation with the message
      const result = await createConversationWithMessage(inputValue);

      // The AI response is processed asynchronously in the backend
      // Our SSE connection will receive updates when the AI responds
      if (result.conversationId) {
        // Connect to SSE to receive updates
        connectToSSE(result.conversationId);
      }

    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message to UI
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `Sorry, I encountered an error processing your request: ${(error as Error).message}. Please try again.`,
        createdAt: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
      setIsLoading(false);
    } finally {
      setIsLoading(false);
    }
  };

  // Function to read message aloud using Web Speech API
  const readMessageAloud = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-US';
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      speechSynthesis.speak(utterance);
    } else {
      alert('Text-to-speech is not supported in your browser.');
    }
  };

  // Function to increase font size
  const increaseFontSize = () => {
    setFontSize(prev => {
      if (prev === 'normal') return 'large';
      if (prev === 'large') return 'largest';
      return 'largest'; // Stay at largest
    });
  };

  // Function to decrease font size
  const decreaseFontSize = () => {
    setFontSize(prev => {
      if (prev === 'largest') return 'large';
      if (prev === 'large') return 'normal';
      return 'normal'; // Stay at normal
    });
  };

  // Function to get font size class
  const getFontSizeClass = () => {
    switch (fontSize) {
      case 'large': return 'text-lg';
      case 'largest': return 'text-xl';
      default: return 'text-base';
    }
  };

  // Function to connect to Server-Sent Events for real-time updates
  const connectToSSE = (convId: string) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    // Create SSE connection to our API which proxies to the backend
    const eventSource = new EventSource(`/api/chat?conversation_id=${convId}&stream=true`);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'messages') {
          // Update messages with the latest from the backend
          // For simplicity, we'll just refetch all messages
          fetchMessages(convId);
        } else if (data.type === 'error') {
          console.error('SSE Error:', data.message);
        }
      } catch (error) {
        console.error('Error parsing SSE message:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE Error:', error);
      eventSource.close();
    };

    eventSourceRef.current = eventSource;
  };

  // Function to fetch messages from the backend
  const fetchMessages = async (convId: string) => {
    try {
      const backendMessages = await getConversationMessages(convId);

      // Convert backend messages to our UI format
      const uiMessages: Message[] = backendMessages.map((msg: any) => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        createdAt: msg.created_at || msg.timestamp || new Date().toISOString(),
      }));

      // Update only if there are new messages
      setMessages(prev => {
        const prevIds = new Set(prev.map(m => m.id));
        const newMessages = uiMessages.filter(msg => !prevIds.has(msg.id));

        if (newMessages.length > 0) {
          return [...prev, ...newMessages];
        }
        return prev;
      });
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  return (
    <div className="flex flex-col">
      <div className="bg-gray-800/80 backdrop-blur-sm rounded-xl p-6 shadow-xl border border-gray-700/50">
        <header className="mb-6">
          <h1 className="text-2xl font-bold text-white flex items-center">
            <svg className="mr-3 h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            AI Todo Assistant
          </h1>
          <p className="text-gray-400 mt-1">Ask me anything about your tasks and I'll help you manage them</p>
        </header>

        <div className="flex flex-col flex-1 min-h-[400px]">
          {/* Messages container */}
          <div
            className="flex-1 overflow-y-auto p-4 space-y-4"
            role="log"
            aria-live="polite"
            aria-label="Chat messages"
          >
            {messages.length === 0 ? (
              <div
                className="text-center py-8 text-gray-500"
                tabIndex={0}
                aria-label="Empty chat, start a conversation with the AI assistant"
              >
                <FaRobot className="mx-auto text-3xl mb-2 text-gray-500" aria-hidden="true" />
                <p className="text-gray-400">Start a conversation with the AI assistant...</p>
                <p className="text-sm mt-2 text-gray-500">Try: "Add a task to buy groceries"</p>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  role="listitem"
                >
                  <div
                    className={`max-w-[80%] rounded-lg px-4 py-2 ${getFontSizeClass()} ${message.role === 'user'
                        ? 'bg-blue-600 text-white rounded-br-none'
                        : 'bg-gray-700 text-gray-100 rounded-bl-none'
                      }`}
                    aria-label={`${message.role === 'user' ? 'User' : 'Assistant'} message: ${message.content}`}
                  >
                    <div className="flex items-start space-x-2">
                      {message.role === 'assistant' && (
                        <FaRobot className="mt-1 shrink-0 text-blue-400" aria-hidden="true" />
                      )}
                      <div>
                        <p>{message.content}</p>
                        <p
                          className={`text-xs mt-1 ${message.role === 'user' ? 'text-blue-200' : 'text-gray-400'
                            }`}
                        >
                          {new Date(message.createdAt).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </p>
                      </div>
                      {message.role === 'user' && (
                        <FaUser className="mt-1 shrink-0 text-blue-200" aria-hidden="true" />
                      )}
                    </div>

                    {/* Button to read message aloud */}
                    <button
                      onClick={() => readMessageAloud(message.content)}
                      className="mt-2 text-xs underline text-blue-300 hover:text-blue-200"
                      aria-label={`Read ${message.role} message aloud`}
                    >
                      Listen
                    </button>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} aria-hidden="true" />
          </div>

          {/* Input area */}
          <form
            onSubmit={handleSubmit}
            className="border-t p-3 bg-gray-800/80 rounded-b-xl mt-4 flex-shrink-0"
            role="form"
            aria-label="Chat input form"
          >
            <div className="flex">
              <label htmlFor="chat-input" className="sr-only">Type your message</label>
              <input
                id="chat-input"
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Type your message..."
                disabled={isLoading}
                className="flex-1 bg-gray-700 border border-gray-600 rounded-l-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 truncate"
                aria-label="Type your message to the AI assistant"
                aria-describedby="chat-help-text"
              />
              <button
                type="submit"
                disabled={isLoading || !inputValue.trim()}
                className={`bg-blue-600 text-white px-4 py-2 rounded-r-lg flex items-center ${isLoading || !inputValue.trim() ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-700'
                  }`}
                aria-label="Send message"
              >
                <FaPaperPlane aria-hidden="true" />
                <span className="ml-2">Send</span>
              </button>
            </div>
            <p
              id="chat-help-text"
              className="text-xs text-gray-500 mt-2 text-center sr-only"
            >
              Ask me to create, update, or manage your tasks using natural language
            </p>
          </form>
        </div>

        <footer className="mt-4 pt-4 border-t border-gray-700 text-center text-sm text-gray-500">
          AI-Powered Todo Management Assistant
        </footer>
      </div>
    </div>
  );
}