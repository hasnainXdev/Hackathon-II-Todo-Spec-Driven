import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import { SessionProvider } from 'next-auth/react';
import ChatInterface from '../src/components/ChatInterface';

// Mock the next-auth session
vi.mock('next-auth/react', () => ({
  useSession: () => ({ data: { accessToken: 'mock-token' }, status: 'authenticated' }),
}));

// Mock fetch API
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('ChatInterface Component', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  it('renders the chat interface correctly', () => {
    render(
      <MockedProvider>
        <SessionProvider session={{}}>
          <ChatInterface />
        </SessionProvider>
      </MockedProvider>
    );

    expect(screen.getByText('AI Todo Assistant')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
  });

  it('allows user to type and submit a message', async () => {
    const userMessage = 'Test message';
    
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        conversation_id: 'test-conversation-id',
        response: 'AI response to test message',
        success: true
      })
    });

    render(
      <MockedProvider>
        <SessionProvider session={{}}>
          <ChatInterface />
        </SessionProvider>
      </MockedProvider>
    );

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: userMessage } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        '/api/chat',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock-token',
          }),
          body: JSON.stringify({
            message: userMessage,
            conversation_id: undefined,
          }),
        })
      );
    });
  });

  it('displays user and AI messages correctly', async () => {
    const userMessage = 'What are my tasks?';
    const aiResponse = 'You have 3 tasks: Buy groceries, Walk the dog, Finish report';
    
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        conversation_id: 'test-conversation-id',
        response: aiResponse,
        success: true
      })
    });

    render(
      <MockedProvider>
        <SessionProvider session={{}}>
          <ChatInterface />
        </SessionProvider>
      </MockedProvider>
    );

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: userMessage } });
    fireEvent.click(sendButton);

    // Wait for the AI response to appear
    await waitFor(() => {
      expect(screen.getByText(aiResponse)).toBeInTheDocument();
    });

    // Check that both user and AI messages are displayed
    expect(screen.getByText(userMessage)).toBeInTheDocument();
    expect(screen.getByText(aiResponse)).toBeInTheDocument();
  });

  it('shows error message when API call fails', async () => {
    const userMessage = 'Test message';
    
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    render(
      <MockedProvider>
        <SessionProvider session={{}}>
          <ChatInterface />
        </SessionProvider>
      </MockedProvider>
    );

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: userMessage } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/encountered an error processing your request/i)).toBeInTheDocument();
    });
  });

  it('disables input while loading', async () => {
    const userMessage = 'Test message';
    
    // Mock a slow API response
    mockFetch.mockImplementationOnce(() =>
      new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            ok: true,
            json: async () => ({
              conversation_id: 'test-conversation-id',
              response: 'AI response',
              success: true
            })
          });
        }, 100);
      })
    );

    render(
      <MockedProvider>
        <SessionProvider session={{}}>
          <ChatInterface />
        </SessionProvider>
      </MockedProvider>
    );

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: userMessage } });
    fireEvent.click(sendButton);

    // Input should be disabled during loading
    expect(input).toBeDisabled();
    expect(sendButton).toBeDisabled();

    // Wait for the request to complete
    await waitFor(() => {
      expect(input).not.toBeDisabled();
      expect(sendButton).not.toBeDisabled();
    });
  });
});