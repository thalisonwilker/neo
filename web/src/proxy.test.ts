// @vitest-environment node
import { NextRequest } from 'next/server';
import { describe, expect, it, vi } from 'vitest';

// Clerk simulado: nenhuma chamada externa real. `clerkMiddleware(handler)` devolve o próprio handler.
vi.mock('@clerk/nextjs/server', () => ({
  clerkMiddleware: (handler: unknown) => handler
}));

import proxy from './proxy';

type AuthResult = { userId: string | null };
type Handler = (auth: () => Promise<AuthResult>, req: NextRequest) => Promise<Response | void>;

const run = proxy as unknown as Handler;
const origin = 'http://localhost:3100';
const withSession = async (): Promise<AuthResult> => ({ userId: 'user_123' });
const withoutSession = async (): Promise<AuthResult> => ({ userId: null });
const get = (path: string) => new NextRequest(`${origin}${path}`);

describe('AC-2: acesso sem sessão leva à entrada com o destino', () => {
  it('AC-2: redireciona uma página protegida para /auth/sign-in com redirect_url', async () => {
    const res = (await run(withoutSession, get('/dashboard/kanban'))) as Response;
    expect(res.status).toBe(307);
    expect(res.headers.get('location')).toBe(
      `${origin}/auth/sign-in?redirect_url=%2Fdashboard%2Fkanban`
    );
  });

  it('AC-2: preserva a consulta do pedido no redirect_url', async () => {
    const res = (await run(withoutSession, get('/dashboard/chat?tab=1'))) as Response;
    expect(res.headers.get('location')).toBe(
      `${origin}/auth/sign-in?redirect_url=%2Fdashboard%2Fchat%3Ftab%3D1`
    );
  });

  it('AC-2: a API sem sessão não redireciona e responde 401 sem dados', async () => {
    const res = (await run(withoutSession, get('/api/products'))) as Response;
    expect(res.status).toBe(401);
    expect(res.headers.get('location')).toBeNull();
    expect(await res.json()).toEqual({ error: 'Não autenticado' });
  });
});

describe('AC-1: o proxy aplica a política de acesso', () => {
  it.each(['/dashboard/overview', '/dashboard', '/api/products', '/api/users/1'])(
    'AC-1: com sessão, %s segue adiante',
    async (path) => {
      expect(await run(withSession, get(path))).toBeUndefined();
    }
  );

  it.each(['/auth/sign-in', '/auth/sign-up', '/auth/sign-in/factor-one', '/'])(
    'AC-1: sem sessão, a rota pública %s segue adiante',
    async (path) => {
      expect(await run(withoutSession, get(path))).toBeUndefined();
    }
  );

  it('AC-1: rota pública não consulta a sessão', async () => {
    const auth = vi.fn(withoutSession);
    await run(auth, get('/auth/sign-in'));
    expect(auth).not.toHaveBeenCalled();
  });
});
