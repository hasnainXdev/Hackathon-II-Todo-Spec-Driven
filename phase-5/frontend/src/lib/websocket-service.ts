import { useEffect, useRef } from 'react';

interface TaskEvent {
  type: 'TASK_CREATED' | 'TASK_UPDATED' | 'TASK_DELETED' | 'TASK_COMPLETED' | 'REMINDER_DUE';
  payload: any;
  timestamp: string;
}

interface WebSocketHookOptions {
  userId: string;
  onMessage: (event: TaskEvent) => void;
  onError?: (error: Event) => void;
  onClose?: (event: CloseEvent) => void;
}

export const useTaskWebSocket = ({ userId, onMessage, onError, onClose }: WebSocketHookOptions) => {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!userId) return;

    const connect = () => {
      // Using the sync service WebSocket endpoint
      // If NEXT_PUBLIC_WEBSOCKET_URL is defined, use it; otherwise derive from API URL
      let wsBaseUrl;
      if (process.env.NEXT_PUBLIC_WEBSOCKET_URL) {
        wsBaseUrl = process.env.NEXT_PUBLIC_WEBSOCKET_URL.replace(/^https?:\/\//, '');
      } else {
        // Derive WebSocket URL from API URL by removing /api/v1
        wsBaseUrl = process.env.NEXT_PUBLIC_FASTAPI_API_URL?.replace(/^https?:\/\//, '').replace('/api/v1', '');
      }
      
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${wsBaseUrl}/ws/${userId}`;

      console.log('Connecting to WebSocket:', wsUrl);

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected for real-time task updates');
      };

      ws.onmessage = (event) => {
        try {
          const message: TaskEvent = JSON.parse(event.data);
          onMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        if (onClose) onClose(event);

        // Attempt to reconnect after a delay
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        reconnectTimeoutRef.current = setTimeout(connect, 5000); // Reconnect after 5 seconds
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        if (onError) onError(error);
      };
    };

    connect();

    // Cleanup function
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [userId, onMessage, onError, onClose]);

  const sendMessage = (message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  };

  return {
    sendMessage,
    isConnected: wsRef.current?.readyState === WebSocket.OPEN,
  };
};