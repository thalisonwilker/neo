import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
  getToken: vi.fn(),
  pathname: '/dashboard/overview',
  replace: vi.fn(),
  signOut: vi.fn(),
  fetchMe: vi.fn()
}));

// Clerk, Next Router e cliente da API simulados: zero chamadas externas reais.
vi.mock('@clerk/nextjs', () => ({
  useAuth: () => ({ isLoaded: true, getToken: mocks.getToken }),
  useClerk: () => ({ signOut: mocks.signOut })
}));
vi.mock('next/navigation', () => ({
  usePathname: () => mocks.pathname,
  useRouter: () => ({ replace: mocks.replace })
}));
vi.mock('@/lib/api', () => ({
  fetchMe: mocks.fetchMe
}));

import { limparBoasVindasPendentes } from '@/features/onboarding/welcome-state';
import { NeoAccessGuard } from './neo-access-guard';

const usuarioConcluido = {
  id: 'u1',
  email: 'dev@neo.app',
  nome_exibicao: 'Thalyson',
  primeiro_acesso_concluido: true,
  espacos: [
    {
      id: 'e1',
      nome: 'Neo',
      tipo: 'trabalho' as const,
      criado_em: '2026-11-22T12:00:00Z',
      meta_semanal: 30,
      agentes_sugeridos: false
    }
  ]
};

const usuarioPendente = {
  id: 'u1',
  email: 'dev@neo.app',
  nome_exibicao: null,
  primeiro_acesso_concluido: false,
  espacos: []
};

describe('AC-11, AC-14, AC-15: guarda de rotas protegidas NeoAccessGuard', () => {
  beforeEach(() => {
    mocks.pathname = '/dashboard/overview';
    mocks.getToken.mockResolvedValue('tok_teste');
    mocks.replace.mockReset();
    mocks.signOut.mockReset();
    mocks.fetchMe.mockReset();
    limparBoasVindasPendentes();
  });

  it('AC-11: usuário com primeiro acesso concluído acessa o conteúdo do painel', async () => {
    mocks.fetchMe.mockResolvedValue({ ok: true, status: 200, usuario: usuarioConcluido });

    render(
      <NeoAccessGuard>
        <div>Conteúdo secreto do painel</div>
      </NeoAccessGuard>
    );

    expect(await screen.findByText('Conteúdo secreto do painel')).toBeInTheDocument();
  });

  it('AC-11: usuário com primeiro acesso pendente em /dashboard é redirecionado para /primeiro-acesso sem renderizar o painel', async () => {
    mocks.fetchMe.mockResolvedValue({ ok: true, status: 200, usuario: usuarioPendente });

    render(
      <NeoAccessGuard>
        <div>Conteúdo secreto do painel</div>
      </NeoAccessGuard>
    );

    await waitFor(() => {
      expect(mocks.replace).toHaveBeenCalledWith('/primeiro-acesso');
    });
    expect(screen.queryByText('Conteúdo secreto do painel')).not.toBeInTheDocument();
  });

  it('AC-11: API responde 401 -> encerra a sessão (volta para /auth/sign-in) sem renderizar o painel', async () => {
    mocks.fetchMe.mockResolvedValue({
      ok: false,
      status: 401,
      erro: { erro: 'token_invalido', mensagem: 'Inválido' }
    });

    render(
      <NeoAccessGuard>
        <div>Conteúdo secreto do painel</div>
      </NeoAccessGuard>
    );

    await waitFor(() => {
      expect(mocks.signOut).toHaveBeenCalledWith({ redirectUrl: '/auth/sign-in' });
    });
    expect(screen.queryByText('Conteúdo secreto do painel')).not.toBeInTheDocument();
  });

  it('AC-14: API responde 403 -> exibe Acesso não liberado com botão Sair e não vaza conteúdo do painel', async () => {
    mocks.fetchMe.mockResolvedValue({
      ok: false,
      status: 403,
      erro: { erro: 'acesso_nao_liberado', mensagem: 'Sem permissão' }
    });

    render(
      <NeoAccessGuard>
        <div>Conteúdo secreto do painel</div>
      </NeoAccessGuard>
    );

    expect(await screen.findByText('Acesso não liberado')).toBeInTheDocument();
    expect(screen.queryByText('Conteúdo secreto do painel')).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Sair' }));
    expect(mocks.signOut).toHaveBeenCalledWith({ redirectUrl: '/auth/sign-in' });
  });

  it('AC-15: API indisponível (5xx) -> exibe mensagem amigável e Tentar de novo refaz a chamada', async () => {
    mocks.fetchMe
      .mockResolvedValueOnce({
        ok: false,
        status: 503,
        erro: { erro: 'api_indisponivel', mensagem: 'Offline' }
      })
      .mockResolvedValueOnce({ ok: true, status: 200, usuario: usuarioConcluido });

    render(
      <NeoAccessGuard>
        <div>Conteúdo secreto do painel</div>
      </NeoAccessGuard>
    );

    expect(await screen.findByText('Não foi possível falar com o Neo agora')).toBeInTheDocument();
    expect(screen.queryByText('Conteúdo secreto do painel')).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Tentar de novo' }));

    expect(await screen.findByText('Conteúdo secreto do painel')).toBeInTheDocument();
    expect(mocks.fetchMe).toHaveBeenCalledTimes(2);
  });
});
