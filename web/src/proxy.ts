import { clerkMiddleware } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

import { buildSignInUrl, isProtectedPath } from '@/features/auth/access';

const isApiPath = (pathname: string) => pathname === '/api' || pathname.startsWith('/api/');

/**
 * Primeira camada de proteção do painel (spec 0036, AC-1 e AC-2). O layout do /dashboard
 * continua exigindo sessão por conta própria (segunda camada).
 *
 * O proxy decide por conta própria, em vez de delegar ao `auth.protect()`: para uma
 * requisição que não é página, o `auth.protect()` do Clerk responde 404, e o redirecionamento
 * dele usa um formato de `redirect_url` diferente do que a spec define.
 */
export default clerkMiddleware(async (auth, req) => {
  const { pathname, search } = req.nextUrl;
  if (!isProtectedPath(pathname)) return;

  const { userId } = await auth();
  if (userId) return;

  // A API não redireciona: responde 401 sem dados.
  if (isApiPath(pathname)) {
    return NextResponse.json({ error: 'Não autenticado' }, { status: 401 });
  }

  return NextResponse.redirect(new URL(buildSignInUrl(pathname, search), req.url));
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)'
  ]
};
