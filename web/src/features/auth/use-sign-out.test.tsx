import { renderHook } from '@testing-library/react';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({ signOut: vi.fn() }));

// Clerk simulado: nenhuma chamada externa real.
vi.mock('@clerk/nextjs', () => ({ useClerk: () => ({ signOut: mocks.signOut }) }));

import { SIGN_OUT_LABEL, useSignOut } from './use-sign-out';

describe('AC-12: saída da sessão', () => {
  it('AC-12: sair encerra a sessão no Clerk e volta para /auth/sign-in', async () => {
    const { result } = renderHook(() => useSignOut());
    await result.current();
    expect(mocks.signOut).toHaveBeenCalledTimes(1);
    expect(mocks.signOut).toHaveBeenCalledWith({ redirectUrl: '/auth/sign-in' });
  });

  it('AC-12: o item do menu do usuário se chama "Sair"', () => {
    expect(SIGN_OUT_LABEL).toBe('Sair');
  });

  it('AC-12: o menu do usuário da sidebar usa a saída do painel, e não um texto ou caminho próprio', () => {
    const sidebar = readFileSync(
      resolve(process.cwd(), 'src/components/layout/app-sidebar.tsx'),
      'utf8'
    );
    expect(sidebar).toMatch(/useSignOut\(\)/);
    expect(sidebar).toMatch(/\{SIGN_OUT_LABEL\}/);
    expect(sidebar).not.toMatch(/Sign out/);
    expect(sidebar).not.toMatch(/signOut\(\{/);
  });
});
