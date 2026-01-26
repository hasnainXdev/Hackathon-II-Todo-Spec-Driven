import { NextRequest, NextResponse } from 'next/server';
import { auth } from "../../../lib/auth";
import { getConversationMessages } from "../../../lib/api-client";

// Helper function to get backend token from session
async function getBackendTokenFromSession(headers: Headers) {
  try {
    const session = await auth.api.getSession({ headers });

    if (!session) {
      throw new Error('Unauthorized: No access token available');
    }

    // Get the backend token from the session
    const tokenResponse = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/api/auth/backend-token`, {
      headers: {
        cookie: headers.get('cookie') || '',
      }
    });

    if (!tokenResponse.ok) {
      throw new Error('Failed to get backend token');
    }

    const tokenData = await tokenResponse.json();
    if (!tokenData.backend_token) {
      throw new Error(tokenData.error || 'No backend token available');
    }

    return tokenData.backend_token;
  } catch (error) {
    console.error('Error getting backend token:', error);
    throw new Error('Authentication failed');
  }
}

// Function to fetch messages directly without using the client library
async function fetchConversationMessages(conversationId: string, backendToken: string) {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/chats/chats/conversations/${conversationId}/messages`,
    {
      headers: {
        'Authorization': `Bearer ${backendToken}`,
      },
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

export async function POST(request: NextRequest) {
  try {
    // Get the session to authenticate the user
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    if (!session) {
      return NextResponse.json(
        { error: 'Unauthorized: No access token available' },
        { status: 401 }
      );
    }

    // Parse the request body
    const { message, conversation_id } = await request.json();

    if (!message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }

    // Import the functions here to avoid circular dependencies
    const { createConversationWithMessage, addMessageToConversation } = await import("../../../lib/api-client");

    let result;

    if (conversation_id) {
      // Add message to existing conversation
      result = await addMessageToConversation(conversation_id, message);
    } else {
      // Create new conversation with the message
      result = await createConversationWithMessage(message);
    }

    // Return the response from the backend
    return NextResponse.json({
      response: result.message?.response || result.message?.content || "Your message has been received. The AI assistant will respond shortly.",
      conversation_id: conversation_id || result.conversationId,
      success: true,
      action_performed: result.action_performed,
      task_details: result.task_details
    });
  } catch (error) {
    console.error('Error in chat API route:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    if (!session) {
      return NextResponse.json(
        { error: 'Unauthorized: No access token available' },
        { status: 401 }
      );
    }

    // Extract conversation_id from query params
    const { searchParams } = new URL(request.url);
    const conversationId = searchParams.get('conversation_id');
    const stream = searchParams.get('stream'); // Check if streaming is requested

    if (!conversationId) {
      return NextResponse.json(
        { error: 'Conversation ID is required' },
        { status: 400 }
      );
    }

    if (stream) {
      // Handle Server-Sent Events for real-time updates
      const encoder = new TextEncoder();
      const stream = new ReadableStream({
        async start(controller) {
          try {
            // Get backend token once at the start of the stream
            let backendToken: string;
            try {
              backendToken = await getBackendTokenFromSession(request.headers);
            } catch (authErr) {
              console.error('Authentication error in SSE:', authErr);
              controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'error', message: 'Authentication failed' })}\n\n`));
              controller.close();
              return;
            }

            // Send initial event
            controller.enqueue(encoder.encode(`data: {"type": "connection", "message": "Connected to chat stream"}\n\n`));

            // Poll for new messages periodically
            const interval = setInterval(async () => {
              try {
                // Check if controller is still active before enqueuing
                if (controller.desiredSize === null) {
                  // Controller is closed, clear the interval
                  clearInterval(interval);
                  return;
                }

                // Fetch messages from the backend using the token
                const messages = await fetchConversationMessages(conversationId, backendToken);

                // Send new messages as Server-Sent Events
                controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'messages', data: messages })}\n\n`));
              } catch (err) {
                console.error('Error polling messages:', err);

                try {
                  // Check if controller is still active before enqueuing
                  if (controller.desiredSize !== null) {
                    controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'error', message: 'Error polling messages: ' + (err as Error).message })}\n\n`));
                  }
                } catch (enqueueErr) {
                  console.error('Error enqueuing error message:', enqueueErr);
                }

                // Stop the interval if there's an authentication error
                if ((err as Error).message.includes('Authentication')) {
                  clearInterval(interval);
                  try {
                    controller.close();
                  } catch (closeErr) {
                    console.error('Error closing controller:', closeErr);
                  }
                }
              }
            }, 30000); // Poll every 30 seconds to reduce spam

            // Store interval ID to clear it later
            (controller as any).__interval = interval;
          } catch (error) {
            console.error('Error in SSE stream:', error);
            controller.error(error);
          }
        },

        cancel() {
          // Cleanup when connection closes
          if ((this as any).__interval) {
            clearInterval((this as any).__interval);
          }
        }
      });

      return new Response(stream, {
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
      });
    } else {
      // Fetch messages normally using the imported function
      const messages = await getConversationMessages(conversationId);

      return NextResponse.json({ messages });
    }
  } catch (error) {
    console.error('Error fetching chat messages:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    );
  }
}