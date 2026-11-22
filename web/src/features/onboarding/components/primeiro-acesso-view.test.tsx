import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
  getToken: vi.fn(),
  replace: vi.fn(),
  signOut: vi.fn(),
  submitPrimeiroAcesso: vi.fn()
}));

vi.mock('@clerk/nextjs', () => ({
  useAuth: () => ({ getToken: mocks.getToken }),
  useClerk: () => ({ signOut: mocks.signOut })
}));
vi.mock('next/navigation', () => ({
  useRouter: () => ({ replace: mocks.replace })
}));
vi.mock('@/lib/api', () => ({
  submitPrimeiroAcesso: mocks.submitPrimeiroAcesso
}));

import {
  lerBoasVindasPendentes,
  limparBoasVindasPendentes
} from '@/features/onboarding/welcome-state';
import { PrimeiroAcessoView } from './primeiro-acesso-view';

describe('AC-12: tela de Primeiro acesso', () => {
  beforeEach(() => {
    mocks.getToken.mockResolvedValue('tok_teste');
    mocks.replace.mockReset();
    mocks.signOut.mockReset();
    mocks.submitPrimeiroAcesso.mockReset();
    limparBoasVindasPendentes();
  });

  it('AC-12: preenche campos, envia POST /v1/primeiro-acesso, marca boas-vindas e navega para /boas-vindas', async () => {
    mocks.submitPrimeiroAcesso.mockResolvedValue({
      ok: true,
      status: 201,
      usuario: {
        id: 'u1',
        email: 'dev@neo.app',
        nome_exibicao: 'Thalyson',
        primeiro_acesso_concluido: true,
        espacos: [
          {
            id: 'e1',
            nome: 'Neo',
            tipo: 'trabalho',
            criado_em: '2026-11-22T12:00:00Z',
            meta_semanal: 30,
            agentes_sugeridos: false
          }
        ]
      }
    });

    render(<PrimeiroAcessoView />);

    fireEvent.change(screen.getByLabelText('Nome de exibição'), {
      target: { value: 'Thalyson' }
    });
    fireEvent.change(screen.getByLabelText('Nome do espaço'), {
      target: { value: 'Neo' }
    });
    fireEvent.click(screen.getByRole('button', { name: 'Estudos' }));
    fireEvent.click(screen.getByRole('button', { name: 'Continuar' }));

    await waitFor(() => {
      expect(mocks.submitPrimeiroAcesso).toHaveBeenCalledWith('tok_teste', {
        nome_exibicao: 'Thalyson',
        espaco: { nome: 'Neo', tipo: 'estudos' }
      });
    });

    expect(lerBoasVindasPendentes()).toEqual({ nomeExibicao: 'Thalyson', nomeEspaco: 'Neo' });
    expect(mocks.replace).toHaveBeenCalledWith('/boas-vindas');
  });

  it('AC-12: desabilita o botão de envio enquanto o pedido está em andamento', async () => {
    let resolverPedido!: (valor: unknown) => void;
    mocks.submitPrimeiroAcesso.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolverPedido = resolve;
        })
    );

    render(<PrimeiroAcessoView />);
    fireEvent.change(screen.getByLabelText('Nome de exibição'), { target: { value: 'Thalyson' } });
    fireEvent.change(screen.getByLabelText('Nome do espaço'), { target: { value: 'Neo' } });

    const botao = screen.getByRole('button', { name: 'Continuar' });
    fireEvent.click(botao);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Salvando…' })).toBeDisabled();
    });

    resolverPedido({
      ok: true,
      status: 201,
      usuario: {
        id: 'u1',
        email: 'dev@neo.app',
        nome_exibicao: 'Thalyson',
        primeiro_acesso_concluido: true,
        espacos: [
          {
            id: 'e1',
            nome: 'Neo',
            tipo: 'trabalho',
            criado_em: '2026-11-22T12:00:00Z',
            meta_semanal: 30,
            agentes_sugeridos: false
          }
        ]
      }
    });

    await waitFor(() => {
      expect(mocks.replace).toHaveBeenCalledWith('/boas-vindas');
    });
  });

  it('AC-12: erro 422 exibe a mensagem junto ao campo correspondente sem sair da tela', async () => {
    mocks.submitPrimeiroAcesso.mockResolvedValue({
      ok: false,
      status: 422,
      erro: {
        erro: 'dados_invalidos',
        mensagem: 'Nome de exibição deve ter entre 1 e 60 caracteres.',
        campo: 'nome_exibicao'
      }
    });

    render(<PrimeiroAcessoView />);
    fireEvent.click(screen.getByRole('button', { name: 'Continuar' }));

    expect(
      await screen.findByText('Nome de exibição deve ter entre 1 e 60 caracteres.')
    ).toBeInTheDocument();
    expect(screen.getByLabelText('Nome de exibição')).toHaveAttribute('aria-invalid', 'true');
    expect(mocks.replace).not.toHaveBeenCalled();
  });

  it('AC-12 (0040 AC-6): o nome do espaço aceita até 100 caracteres', () => {
    render(<PrimeiroAcessoView />);
    expect(screen.getByLabelText('Nome do espaço')).toHaveAttribute('maxLength', '100');
  });
});
