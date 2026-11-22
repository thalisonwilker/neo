import { render } from '@testing-library/react';
import type { ReactNode } from 'react';
import { describe, expect, it, vi } from 'vitest';

const captured = vi.hoisted(() => ({
  signIn: undefined as Record<string, unknown> | undefined,
  signUp: undefined as Record<string, unknown> | undefined
}));

// Clerk e cabeçalhos simulados: nenhuma chamada externa real.
vi.mock('@clerk/nextjs', () => ({
  SignIn: (props: Record<string, unknown>) => {
    captured.signIn = props;
    return <div data-testid='clerk-sign-in' />;
  },
  SignUp: (props: Record<string, unknown>) => {
    captured.signUp = props;
    return <div data-testid='clerk-sign-up' />;
  }
}));
vi.mock('next/headers', () => ({
  headers: async () => new Headers({ host: 'localhost:3100' })
}));

import SignInPage from './sign-in/[[...sign-in]]/page';
import SignUpPage from './sign-up/[[...sign-up]]/page';

type Params = Promise<{ redirect_url?: string | string[] }>;
const params = (redirect_url?: string | string[]): Params => Promise.resolve({ redirect_url });

async function destinationOf(page: 'sign-in' | 'sign-up', redirectUrl?: string | string[]) {
  const Page = page === 'sign-in' ? SignInPage : SignUpPage;
  const ui = (await Page({ searchParams: params(redirectUrl) })) as ReactNode;
  render(ui);
  const props = page === 'sign-in' ? captured.signIn : captured.signUp;
  return props?.forceRedirectUrl;
}

describe.each(['sign-in', 'sign-up'] as const)(
  'AC-3 e AC-4: destino pós-login na tela %s',
  (page) => {
    it('AC-3: leva ao caminho interno pedido', async () => {
      expect(await destinationOf(page, '/dashboard/kanban')).toBe('/dashboard/kanban');
    });

    it('AC-3: reduz a URL absoluta da mesma origem (formato do Clerk) a caminho e consulta', async () => {
      expect(await destinationOf(page, 'http://localhost:3100/dashboard/kanban?x=1')).toBe(
        '/dashboard/kanban?x=1'
      );
    });

    it('AC-3: sem redirect_url, leva a /dashboard/overview', async () => {
      expect(await destinationOf(page)).toBe('/dashboard/overview');
    });

    it('AC-3: com redirect_url repetido, usa o primeiro', async () => {
      expect(await destinationOf(page, ['/dashboard/chat', '/dashboard/kanban'])).toBe(
        '/dashboard/chat'
      );
    });

    it.each([
      'https://evil.example',
      '//evil.example',
      'javascript:alert(1)',
      'http://localhost:3100.evil.example/x',
      '/auth/sign-in'
    ])('AC-4: ignora %s e usa /dashboard/overview', async (raw) => {
      expect(await destinationOf(page, raw)).toBe('/dashboard/overview');
    });
  }
);
