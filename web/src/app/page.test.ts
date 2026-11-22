// @vitest-environment node
import { describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
  auth: vi.fn(),
  // Como o Next, `redirect` interrompe a execução lançando uma exceção.
  redirect: vi.fn((url: string) => {
    throw new Error(`NEXT_REDIRECT:${url}`);
  })
}));

vi.mock('@clerk/nextjs/server', () => ({ auth: mocks.auth }));
vi.mock('next/navigation', () => ({ redirect: mocks.redirect }));

import Dashboard from './dashboard/page';
import Page from './page';

describe('AC-5: a raiz e o índice do painel decidem pela sessão', () => {
  it('AC-5: com sessão ativa, / vai a /dashboard/overview', async () => {
    mocks.auth.mockResolvedValue({ userId: 'user_123' });
    await expect(Page()).rejects.toThrow('NEXT_REDIRECT:/dashboard/overview');
  });

  it('AC-5: sem sessão, / vai a /auth/sign-in', async () => {
    mocks.auth.mockResolvedValue({ userId: null });
    await expect(Page()).rejects.toThrow('NEXT_REDIRECT:/auth/sign-in');
  });

  it('AC-5: o índice /dashboard segue a mesma regra', async () => {
    mocks.auth.mockResolvedValue({ userId: 'user_123' });
    await expect(Dashboard()).rejects.toThrow('NEXT_REDIRECT:/dashboard/overview');
    mocks.auth.mockResolvedValue({ userId: null });
    await expect(Dashboard()).rejects.toThrow('NEXT_REDIRECT:/auth/sign-in');
  });
});
