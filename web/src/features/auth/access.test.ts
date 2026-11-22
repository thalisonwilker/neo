import { describe, expect, it } from 'vitest';

import {
  DEFAULT_POST_LOGIN_PATH,
  SIGN_IN_PATH,
  SIGN_UP_PATH,
  buildSignInUrl,
  isProtectedPath,
  resolvePostLoginRedirect
} from './access';

describe('AC-1: política de acesso por rota', () => {
  it.each(['/dashboard', '/dashboard/overview', '/dashboard/kanban/qualquer-coisa'])(
    'AC-1: %s é protegida',
    (path) => {
      expect(isProtectedPath(path)).toBe(true);
    }
  );

  it.each(['/api', '/api/products', '/api/chat/stream'])('AC-1: %s (API) é protegida', (path) => {
    expect(isProtectedPath(path)).toBe(true);
  });

  it.each(['/auth/sign-in', '/auth/sign-up', '/auth/sign-in/factor-one', '/auth/sign-up/continue'])(
    'AC-1: %s é pública',
    (path) => {
      expect(isProtectedPath(path)).toBe(false);
    }
  );

  it.each(['/', '/auth', '/dashboardx', '/api-docs', '/favicon.ico'])(
    'AC-1: %s não é tratada como protegida (não está sob /dashboard nem /api)',
    (path) => {
      expect(isProtectedPath(path)).toBe(false);
    }
  );
});

describe('AC-2: URL de entrada com o destino', () => {
  it('AC-2: leva o caminho pedido em redirect_url, codificado', () => {
    expect(buildSignInUrl('/dashboard/kanban')).toBe(
      '/auth/sign-in?redirect_url=%2Fdashboard%2Fkanban'
    );
  });

  it('AC-2: preserva a consulta do caminho pedido', () => {
    expect(buildSignInUrl('/dashboard/chat', '?tab=1')).toBe(
      '/auth/sign-in?redirect_url=%2Fdashboard%2Fchat%3Ftab%3D1'
    );
  });

  it('AC-2: usa a rota de entrada oficial', () => {
    expect(SIGN_IN_PATH).toBe('/auth/sign-in');
    expect(SIGN_UP_PATH).toBe('/auth/sign-up');
  });
});

describe('AC-3: destino pós-login válido e padrão', () => {
  it.each(['/dashboard/kanban', '/dashboard/chat?tab=1', '/dashboard/overview'])(
    'AC-3: aceita o caminho interno %s',
    (path) => {
      expect(resolvePostLoginRedirect(path)).toBe(path);
    }
  );

  it.each([undefined, null, ''])('AC-3: usa /dashboard/overview quando o destino é %j', (raw) => {
    expect(resolvePostLoginRedirect(raw)).toBe('/dashboard/overview');
    expect(DEFAULT_POST_LOGIN_PATH).toBe('/dashboard/overview');
  });

  it('AC-3: descarta o fragmento (#...)', () => {
    expect(resolvePostLoginRedirect('/dashboard/kanban#coluna')).toBe('/dashboard/kanban');
  });

  it('AC-3: reduz uma URL absoluta da mesma origem (como o Clerk gera) a caminho e consulta', () => {
    expect(
      resolvePostLoginRedirect(
        'http://localhost:3100/dashboard/kanban?x=1',
        'http://localhost:3100'
      )
    ).toBe('/dashboard/kanban?x=1');
  });
});

describe('AC-4: destino pós-login inválido é ignorado', () => {
  it.each([
    ['URL externa', 'https://evil.example'],
    ['URL externa com caminho', 'https://evil.example/dashboard'],
    ['protocolo relativo', '//evil.example'],
    ['esquema javascript', 'javascript:alert(1)'],
    ['esquema data', 'data:text/html,<script>alert(1)</script>'],
    ['barra invertida', '/\\evil.example'],
    ['tabulação escondida', '/\t/evil.example'],
    ['quebra de linha inicial', '\n//evil.example'],
    ['espaço inicial', ' //evil.example'],
    ['sem barra inicial', 'dashboard/kanban'],
    ['rota de entrada', '/auth/sign-in'],
    ['rota de entrada com consulta', '/auth/sign-in?redirect_url=%2Fdashboard'],
    ['subrota de entrada', '/auth/sign-in/factor-one'],
    ['rota de cadastro', '/auth/sign-up']
  ])('AC-4: ignora %s', (_nome, raw) => {
    expect(resolvePostLoginRedirect(raw)).toBe('/dashboard/overview');
  });

  it('AC-4: ignora URL absoluta de outra origem mesmo com origem conhecida', () => {
    expect(
      resolvePostLoginRedirect('https://evil.example/dashboard', 'http://localhost:3100')
    ).toBe('/dashboard/overview');
    expect(
      resolvePostLoginRedirect('http://localhost:3100.evil.example/x', 'http://localhost:3100')
    ).toBe('/dashboard/overview');
  });

  it('AC-4: URL absoluta sem origem conhecida é ignorada', () => {
    expect(resolvePostLoginRedirect('http://localhost:3100/dashboard/kanban')).toBe(
      '/dashboard/overview'
    );
  });

  it('AC-4: ignora destinos absurdamente longos', () => {
    expect(resolvePostLoginRedirect('/' + 'a'.repeat(5000))).toBe('/dashboard/overview');
  });
});
