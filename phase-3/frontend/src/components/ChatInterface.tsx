'use client';

import { useState, useRef, useEffect } from 'react';
import authClient from '../lib/auth-client';
import { FaPaperPlane, FaRobot, FaUser, FaVolumeUp, FaKeyboard } from 'react-icons/fa';
import {
  createConversationWithMessage,
  addMessageToConversation,
  getConversationMessages
} from '../lib/api-client';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt: string;
}

interface ChatProps {
  conversationId?: string;
}

export default function ChatInterface({ conversationId }: ChatProps) {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(false); // Track background fetching
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

    // Create a temporary user message with a temporary ID
    const tempUserMessageId = `temp-${Date.now()}`;
    const userMessage: Message = {
      id: tempUserMessageId,
      role: 'user',
      content: inputValue,
      createdAt: new Date().toISOString(),
    };

    // Add user message to UI immediately
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      let result;

      if (conversationId) {
        // Add message to existing conversation
        result = await addMessageToConversation(conversationId, inputValue);
      } else {
        // Create new conversation with the message
        result = await createConversationWithMessage(inputValue);
      }

      // The AI response is processed asynchronously in the backend
      // Our SSE connection will receive updates when the AI responds
      // So we just need to update the conversation ID and let SSE handle updates
      if (result.conversationId && !conversationId) {
        // If we created a new conversation, we should reconnect SSE
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
        }
        connectToSSE(result.conversationId);
      }

      // Add a temporary "thinking" message from the assistant
      const thinkingMessage: Message = {
        id: `thinking-${Date.now()}`,
        role: 'assistant',
        content: '🤔 Thinking...',
        createdAt: new Date().toISOString(),
      };
      setMessages(prev => [...prev, thinkingMessage]);

    } catch (error) {
      console.error('Error sending message:', error);

      // Remove the temporary user message and add error message to UI
      setMessages(prev => prev.filter(msg => msg.id !== tempUserMessageId)); // Remove temp message

      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `❌ Sorry, I encountered an error processing your request: ${(error as Error).message}. Please try again.`,
        createdAt: new Date().toISOString(),
      };

      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
    } finally {
      // Don't reset isLoading here since the AI response is still coming
      // isLoading will be reset when the AI responds via SSE
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

          // Add error message to UI
          setMessages(prev => {
            // Filter out temporary thinking messages and temporary user messages
            const filteredPrev = prev.filter(msg =>
              !msg.content.includes('🤔 Thinking...') &&
              !msg.id.startsWith('temp-')
            );

            const errorMessage: Message = {
              id: `error-${Date.now()}`,
              role: 'assistant',
              content: `❌ ${data.message}`,
              createdAt: new Date().toISOString(),
            };

            // Reset loading state and add error message
            setIsLoading(false);
            return [...filteredPrev, errorMessage];
          });
        } else if (data.type === 'connection') {
          // Connection established message - just log it
          console.log('SSE Connection established:', data.message);
        }
      } catch (error) {
        console.error('Error parsing SSE message:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE Error:', error);
      eventSource.close();

      // Reset loading state on error
      setIsLoading(false);
    };

    eventSourceRef.current = eventSource;
  };

  // Function to fetch messages from the backend
  const fetchMessages = async (convId: string) => {
    setIsFetching(true); // Set fetching state when starting to fetch
    try {
      const backendMessages = await getConversationMessages(convId);

      // Convert backend messages to our UI format
      const uiMessages: Message[] = backendMessages.map((msg: any) => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        createdAt: msg.created_at || msg.timestamp || new Date().toISOString(),
      }));

      setMessages(prev => {
        // Filter out temporary thinking messages and temporary user messages
        const filteredPrev = prev.filter(msg =>
          !msg.content.includes('🤔 Thinking...') &&
          !msg.id.startsWith('temp-')
        );

        // Find new messages that aren't already in the UI
        const prevIds = new Set(filteredPrev.map(m => m.id));
        const newMessages = uiMessages.filter(msg => !prevIds.has(msg.id));

        // Return the filtered previous messages plus new messages
        return [...filteredPrev, ...newMessages];
      });

      // Reset loading state after receiving response
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching messages:', error);
    } finally {
      setIsFetching(false); // Always reset fetching state
    }
  };

  // Connect to SSE if conversationId is available
  useEffect(() => {
    if (conversationId) {
      connectToSSE(conversationId);
    }
  }, [conversationId]);

  return (
    <div
      className="flex flex-col h-full bg-gray-800/50 rounded-xl border border-gray-700 overflow-hidden"
      role="region"
      aria-label="AI Todo Assistant Chat Interface"
    >
      {/* Chat header with accessibility controls */}
      <div className="bg-gray-800/80 px-4 py-3 rounded-t-xl flex justify-between items-center border-b border-gray-700">
        <div>
          <h2 className="text-lg font-semibold text-white">AI Todo Assistant</h2>
          <p className="text-sm text-gray-400">Ask me anything about your tasks!</p>
        </div>

        {/* Accessibility controls */}
        <div className="flex space-x-2" role="toolbar" aria-label="Accessibility controls">
          <button
            onClick={increaseFontSize}
            className="p-2 rounded-full bg-gray-700 hover:bg-gray-600 text-gray-300"
            aria-label="Increase text size"
          >
            <FaKeyboard className="transform scale-125" />
          </button>
          <button
            onClick={() => readMessageAloud("Welcome to the AI Todo Assistant. You can ask me to create, update, or manage your tasks using natural language.")}
            className="p-2 rounded-full bg-gray-700 hover:bg-gray-600 text-gray-300"
            aria-label="Listen to welcome message"
          >
            <FaVolumeUp />
          </button>
        </div>
      </div>

      {/* Messages container */}
      <div
        className="flex-1 overflow-y-auto p-4 space-y-4 max-h-[400px]"
        style={{ maxHeight: 'calc(100vh - 200px)' }} // Adjust height based on screen size
        role="log"
        aria-live="polite"
        aria-label="Chat messages"
      >
        {isFetching && messages.length === 0 ? (
          <div className="flex justify-center items-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : messages.length === 0 ? (
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
          <>
            {isFetching && (
              <div className="flex justify-center items-center py-2">
                <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-blue-500"></div>
                <span className="ml-2 text-sm text-gray-400">Loading new messages...</span>
              </div>
            )}
            {messages.map((message) => (
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
                      <div className="whitespace-pre-wrap">
                        {message.content.split('\n').map((line, index) => {
                          // Check if the line contains an ID pattern like "ID: abcdef12..."
                          const idPattern = /(ID:\s*([a-zA-Z0-9-]+))/g;

                          const parts = [];
                          let lastIndex = 0;
                          let match;

                          while ((match = idPattern.exec(line)) !== null) {
                            // Add text before the match
                            if (match.index > lastIndex) {
                              parts.push(line.substring(lastIndex, match.index));
                            }

                            // Add the ID with copy button
                            const fullId = match[2]; // The full ID part
                            parts.push(
                              <span key={`id-${index}-${match.index}`} className="inline-flex items-center">
                                {match[0]}
                                <button
                                  onClick={() => navigator.clipboard.writeText(fullId)}
                                  className="ml-1 text-gray-400 hover:text-white transition-colors inline-flex items-center"
                                  title="Copy full ID to clipboard"
                                  aria-label={`Copy ID ${fullId}`}
                                >
                                  <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                  </svg>
                                </button>
                              </span>
                            );

                            lastIndex = match.index + match[0].length;
                          }

                          // Add remaining text after the last match
                          if (lastIndex < line.length) {
                            parts.push(line.substring(lastIndex));
                          }

                          return (
                            <div key={index}>
                              {parts}
                              {index < message.content.split('\n').length - 1 && <br />}
                            </div>
                          );
                        })}
                      </div>
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
            ))}
          </>
        )}
        <div ref={messagesEndRef} aria-hidden="true" />
      </div>

      {/* Input area */}
      <form
        onSubmit={handleSubmit}
        className="border-t p-3 bg-gray-800/80 rounded-b-xl flex-shrink-0"
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
            {isLoading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                <span>Sending...</span>
              </div>
            ) : (
              <>
                <FaPaperPlane aria-hidden="true" />
                <span className="ml-2">Send</span>
              </>
            )}
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
  );
}