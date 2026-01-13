import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { getAuthDb } from "./better-auth-db-connection";

export const auth = betterAuth({
  database: drizzleAdapter(getAuthDb(), {
    provider: "pg", // specify PostgreSQL
  }),
  secret: process.env.BETTER_AUTH_SECRET,
  baseURL: process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000",
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
  },
  plugins: [
    jwt(),
  ],
});