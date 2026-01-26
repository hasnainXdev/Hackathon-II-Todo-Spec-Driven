import { NextRequest, NextResponse } from 'next/server';
import { headers } from 'next/headers';
import { auth } from './lib/auth';

export async function middleware(request: NextRequest) {
  // Define protected routes
  const protectedPaths = ['/dashboard', '/preferences'];
  const isProtectedPath = protectedPaths.some(path =>
    request.nextUrl.pathname.startsWith(path)
  );

  if (isProtectedPath) {
    // Validate the session using Better Auth's API with full database check
    const session = await auth.api.getSession({
      headers: await headers()
    });

    if (!session) {
      // Redirect to login if not authenticated
      return NextResponse.redirect(new URL('/login', request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  runtime: 'nodejs',
  matcher: ['/dashboard/:path*', '/preferences/:path*'],
};