import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_FASTAPI_API_URL;

// Create the base axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Custom wrapper function for authenticated requests
async function authenticatedRequest<T>(config: any): Promise<any> {
  try {
    console.log('Starting authenticated request...');
    // Fetch the backend-compatible token from our exchange API route
    const response = await fetch('/api/auth/backend-token');
    const data = await response.json();
    console.log('Received backend token response:', { authenticated: data.authenticated, hasToken: !!data.backend_token });

    if (data.backend_token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${data.backend_token}`;
      console.log('Set Authorization header with token (first 20 chars):', data.backend_token.substring(0, 20));
    } else {
      // If no token is available, redirect to login
      console.log('No backend token available, redirecting to login');
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
      throw new Error('Authentication required');
    }
  } catch (error) {
    console.error('Error getting backend token:', error);
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
    throw error;
  }

  return apiClient(config);
}

// Export the authenticated API client with methods
export const authenticatedApi = {
  get: <T>(url: string, config?: any) => authenticatedRequest<T>({ ...config, url, method: 'GET' }),
  post: <T>(url: string, data?: any, config?: any) => authenticatedRequest<T>({ ...config, url, method: 'POST', data }),
  put: <T>(url: string, data?: any, config?: any) => authenticatedRequest<T>({ ...config, url, method: 'PUT', data }),
  patch: <T>(url: string, data?: any, config?: any) => authenticatedRequest<T>({ ...config, url, method: 'PATCH', data }),
  delete: <T>(url: string, config?: any) => authenticatedRequest<T>({ ...config, url, method: 'DELETE' }),
};

// Add a response interceptor to handle token expiration and refresh
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      // For Better Auth, a 401 usually means the session has expired
      // We should redirect to login to trigger re-authentication
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }

    // Handle other error responses
    if (error.response?.status >= 500) {
      console.error('Server error:', error.response.data);
      // You might want to show a user-friendly error message
    } else if (error.response?.status === 409) {
      // Handle conflict errors (e.g., optimistic locking)
      console.warn('Conflict error:', error.response.data);
      // You might want to show a specific message to the user
    }

    return Promise.reject(error);
  }
);

// Export the base client for other uses if needed
export default apiClient;