import { NextRequest } from 'next/server';
import { auth } from "../../../../../lib/auth";
import { NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    if (session) {
      return NextResponse.json({ authenticated: true, user: session.user });
    } else {
      return NextResponse.json({ authenticated: false }, { status: 401 });
    }
  } catch (error) {
    console.error('Session validation error:', error);
    return NextResponse.json({ authenticated: false, error: 'Session validation failed' }, { status: 401 });
  }
}

export const dynamic = 'force-dynamic';