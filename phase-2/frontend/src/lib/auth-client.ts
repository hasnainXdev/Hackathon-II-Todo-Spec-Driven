import { createAuthClient } from "better-auth/react";

const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL

export const authClient = createAuthClient({
  baseURL: BASE_URL,
});

// Export the client itself
export default authClient;