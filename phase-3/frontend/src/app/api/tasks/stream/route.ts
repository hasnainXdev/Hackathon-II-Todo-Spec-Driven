import { NextRequest, NextResponse } from 'next/server';
import { auth } from "../../../../../lib/auth";

// This is a simplified implementation that simulates real-time updates
// In a production environment, you would use a proper pub/sub system like Redis, RabbitMQ, etc.
// or WebSocket connections to broadcast updates in real-time

export async function GET(request: NextRequest) {
  try {
    // Authenticate the user
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    if (!session) {
      return NextResponse.json(
        { error: 'Unauthorized: No access token available' },
        { status: 401 }
      );
    }

    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId');

    // Verify that the requesting user matches the userId in the query
    if (userId !== session.user?.id) {
      return NextResponse.json(
        { error: 'Forbidden: Cannot access tasks for another user' },
        { status: 403 }
      );
    }

    // Create a server-sent events stream
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        // Send initial connection message
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'connected', userId })}\n\n`));

        // In a real implementation, you would set up a listener to your backend
        // that notifies when tasks change for this user. For now, we'll simulate
        // this with a periodic check or by listening to a pub/sub system.

        // For demonstration purposes, we'll create a mock event emitter
        // In a real implementation, this would connect to your actual task update system
        const interval = setInterval(() => {
          // This is where you would listen for actual task updates
          // For now, we'll just send a heartbeat to keep the connection alive
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'heartbeat' })}\n\n`));
        }, 30000); // Send heartbeat every 30 seconds

        // Store interval reference to clear it later
        (controller as any).__interval = interval;
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
        'Access-Control-Allow-Origin': '*',
      },
    });
  } catch (error) {
    console.error('Error in task stream API:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}