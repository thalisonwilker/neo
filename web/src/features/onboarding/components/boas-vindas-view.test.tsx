import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
  getToken: vi.fn(),
  pathname: '/boas-vindas',
  replace: vi.fn(),
  signOut: vi.fn(),
  fetchMe: vi.fn()
}));

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

import {
  lerBoasVindasPendentes,
  limparBoasVindasPendentes,
  marcarBoasVindasPendentes
} from '@/features/onboarding/welcome-state';
import { BoasVindasView } from './boas-vindas-view';
import { NeoAccessGuard } from './neo-access-guard';

const usuarioConcluido = {
  id: 'u1',
  email: 'dev@neo.app',
  nome_exibicao: 'Thalyson',
  primeiro_acesso_concluido: true,
  espacos: [{ id: 'e1', nome: 'Neo', tipo: 'trabalho' as const, criado_em: '2026-11-22T12:00:00Z' }]
};

describe('AC-13: tela de Boas-vindas', () => {
  beforeEach(() => {
    mocks.pathname = '/boas-vindas';
    mocks.getToken.mockResolvedValue('tok_teste');
    mocks.replace.mockReset();
    mocks.signOut.mockReset();
    mocks.fetchMe.mockResolvedValue({ ok: true, status: 200, usuario: usuarioConcluido });
    limparBoasVindasPendentes();
  });

  it('AC-13: exibe Boas-vindas com o nome de exibição, o Espaço criado e botão para /dashboard', async () => {
    marcarBoasVindasPendentes({ nomeExibicao: 'Thalyson', nomeEspaco: 'Neo' });

    render(
      <NeoAccessGuard>
        <BoasVindasView />
      </NeoAccessGuard>
    );

    expect(await screen.findByText('Boas-vindas, Thalyson')).toBeInTheDocument();
    expect(screen.getByText('Neo')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Ir para o painel' }));
    expect(lerBoasVindasPendentes()).toBeNull();
    expect(mocks.replace).toHaveBeenCalledWith('/dashboard');
  });

  it('AC-13: nova visita a /boas-vindas sem boas-vindas pendentes vai direto para /dashboard', async () => {
    render(
      <NeoAccessGuard>
        <BoasVindasView />
      </NeoAccessGuard>
    );

    await waitFor(() => {
      expect(mocks.replace).toHaveBeenCalledWith('/dashboard');
    });
    expect(screen.queryByText('Boas-vindas, Thalyson')).not.toBeInTheDocument();
  });
});
