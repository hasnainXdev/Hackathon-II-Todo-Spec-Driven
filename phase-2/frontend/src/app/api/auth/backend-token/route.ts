import { NextRequest } from 'next/server';
import { auth } from '@/lib/auth';
import { NextResponse } from 'next/server';
import { SignJWT } from 'jose';

export async function GET(request: NextRequest) {
  try {
    console.log('Starting backend-token generation...');

    const session = await auth.api.getSession({
      headers: request.headers,
    });

    if (session) {
      console.log('Session found:', session.user.id);

      // Generate a JWT token compatible with the backend
      // Using the same algorithm and secret as the backend
      const backendSecret = process.env.BETTER_AUTH_SECRET!;
      console.log('Using secret (first 10 chars):', backendSecret?.substring(0, 10));

      const encoder = new TextEncoder();
      const secret = encoder.encode(backendSecret);

      const jwt = await new SignJWT({
        sub: session.user.id,
        email: session.user.email,
        name: session.user.name,
      })
        .setProtectedHeader({ alg: 'HS256' })
        .setIssuedAt()
        .setExpirationTime('1h')
        .sign(secret);  // Use the encoded secret

      console.log('Generated JWT (first 20 chars):', jwt.substring(0, 20));

      return NextResponse.json({
        authenticated: true,
        user: session.user,
        backend_token: jwt  // This is the token that can be used with the backend
      });
    } else {
      console.log('No session found');
      return NextResponse.json({ authenticated: false }, { status: 401 });
    }
  } catch (error) {
    console.error('Token generation error:', error);
    return NextResponse.json({ authenticated: false, error: 'Token generation failed' }, { status: 401 });
  }
}

export const dynamic = 'force-dynamic';