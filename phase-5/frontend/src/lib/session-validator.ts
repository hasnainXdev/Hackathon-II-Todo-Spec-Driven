import { cookies } from 'next/headers';
import { auth } from '@/lib/auth';

export async function isAuthenticated(): Promise<boolean> {
  try {
    const allCookies = await cookies();
    const token = allCookies.get('better-auth.session-token');

    if (!token) {
      return false;
    }

    const session = await auth.api.getSession({
      headers: new Headers({
        cookie: `better-auth.session-token=${token.value}`,
      }),
    });

    return !!session;
  } catch (error) {
    console.error('Session validation error:', error);
    return false;
  }
}