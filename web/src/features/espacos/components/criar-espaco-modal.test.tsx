import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { UsuarioDTO } from '@/lib/api';

const mocks = vi.hoisted(() => ({
  getToken: vi.fn(),
  push: vi.fn(),
  signOut: vi.fn(),
  recarregar: vi.fn(),
  criarEspaco: vi.fn()
}));

// Clerk, Next e API simulados: nenhuma chamada externa real.
vi.mock('@clerk/nextjs', () => ({
  useAuth: () => ({ getToken: mocks.getToken }),
  useClerk: () => ({ signOut: mocks.signOut })
}));
vi.mock('next/navigation', () => ({
  usePathname: () => '/dashboard/overview',
  useRouter: () => ({ push: mocks.push, replace: vi.fn() })
}));
vi.mock('@/lib/api', async (importOriginal) => ({
  ...(await importOriginal<typeof import('@/lib/api')>()),
  criarEspaco: mocks.criarEspaco
}));

const usuario: UsuarioDTO = {
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
};
vi.mock('@/features/onboarding/components/neo-access-guard', () => ({
  useUsuarioNeo: () => ({ usuario, recarregar: mocks.recarregar })
}));

import { HomeView } from '@/features/home/components/home-view';
import { CriarEspacoProvider } from './criar-espaco-provider';
import { MENSAGENS } from './criar-espaco-modal';

beforeEach(() => {
  mocks.getToken.mockResolvedValue('tok');
});

function abrirPelaHome() {
  render(
    <CriarEspacoProvider>
      <HomeView hoje={new Date(2026, 10, 22)} />
    </CriarEspacoProvider>
  );
  fireEvent.click(screen.getByRole('button', { name: 'Novo Espaço' }));
  return screen.getByRole('dialog');
}

const campoNome = () => screen.getByLabelText('Nome do Espaço');
const campoMeta = () => screen.getByLabelText('Meta semanal');
const botaoCriar = () => screen.getByRole('button', { name: /Criar Espaço|Criando…/ });
const tipo = (rotulo: string) => screen.getByRole('radio', { name: new RegExp(rotulo) });

describe('0040 AC-7: abrir o modal', () => {
  it('o "+" do cartão Espaços abre "Criar Espaço" no estado inicial', () => {
    const modal = abrirPelaHome();
    expect(within(modal).getByRole('heading', { name: 'Criar Espaço' })).toBeInTheDocument();
    expect(
      within(modal).getByText(
        'Escolha o tipo. Ele define o calendário, as tarefas, os agentes e as skills sugeridas.'
      )
    ).toBeInTheDocument();
    expect(campoNome()).toHaveValue('');
    expect(campoNome()).toHaveFocus();
    expect(tipo('Trabalho')).toBeChecked();
    expect(campoMeta()).toHaveValue('30');
    expect(
      within(modal).getByRole('switch', {
        name: 'Criar agentes e skills sugeridos para este tipo'
      })
    ).not.toBeChecked();
  });
});

describe('0040 AC-8: escolher o tipo', () => {
  it.each([
    ['Estudos', '10', 'Faculdade, cursos, leituras, provas e cronogramas'],
    ['Hobbies', '8', 'Atividades de lazer'],
    ['Pessoal', '8', 'Coisas da vida pessoal'],
    ['Trabalho', '30', 'Trabalho, carreira, clientes e outros projetos']
  ])('%s fica selecionado e a meta vira %s', (rotulo, meta, descricao) => {
    // Clicar no tipo já selecionado não troca nada (mantém a meta digitada).
    abrirPelaHome();
    // Parte de outro tipo, com a meta editada, para a troca ser real.
    fireEvent.click(tipo(rotulo === 'Pessoal' ? 'Hobbies' : 'Pessoal'));
    fireEvent.change(campoMeta(), { target: { value: '50' } });
    fireEvent.click(tipo(rotulo));
    expect(tipo(rotulo)).toBeChecked();
    expect(
      screen.getAllByRole('radio').filter((r) => (r as HTMLInputElement).checked)
    ).toHaveLength(1);
    expect(campoMeta()).toHaveValue(meta);
    expect(tipo(rotulo).closest('label')).toHaveTextContent(descricao);
    expect(tipo(rotulo).closest('label')).toHaveAttribute('data-selecionado', 'true');
  });
});

describe('0040 AC-9: validar antes de enviar', () => {
  it('nome vazio deixa o botão desabilitado e mostra a mensagem ao sair do campo', () => {
    abrirPelaHome();
    expect(botaoCriar()).toBeDisabled();
    fireEvent.change(campoNome(), { target: { value: '   ' } });
    fireEvent.blur(campoNome());
    expect(screen.getByText(MENSAGENS.nomeVazio)).toBeInTheDocument();
    expect(botaoCriar()).toBeDisabled();
  });

  it.each(['0', '169', '12,5', 'doze', ''])('meta "%s" é inválida', (valor) => {
    abrirPelaHome();
    fireEvent.change(campoNome(), { target: { value: 'Faculdade' } });
    fireEvent.change(campoMeta(), { target: { value: valor } });
    expect(screen.getByText(MENSAGENS.metaInvalida)).toBeInTheDocument();
    expect(botaoCriar()).toBeDisabled();
  });

  it('o nome não aceita mais de 100 caracteres', () => {
    abrirPelaHome();
    expect(campoNome()).toHaveAttribute('maxLength', '100');
  });
});

describe('0040 AC-10: criar e abrir o dashboard', () => {
  it('envia os dados, mostra "Criando…" e vai para o dashboard do novo Espaço', async () => {
    let concluir: (v: unknown) => void = () => {};
    mocks.criarEspaco.mockReturnValue(new Promise((r) => (concluir = r)));
    abrirPelaHome();

    fireEvent.change(campoNome(), { target: { value: '  Faculdade  ' } });
    fireEvent.click(tipo('Estudos'));
    fireEvent.change(campoMeta(), { target: { value: '12' } });
    fireEvent.click(screen.getByRole('switch'));
    fireEvent.click(botaoCriar());

    await waitFor(() => expect(botaoCriar()).toHaveTextContent('Criando…'));
    expect(botaoCriar()).toBeDisabled();
    fireEvent.click(botaoCriar());
    expect(mocks.criarEspaco).toHaveBeenCalledTimes(1);
    expect(mocks.criarEspaco).toHaveBeenCalledWith('tok', {
      nome: 'Faculdade',
      tipo: 'estudos',
      meta_semanal: 12,
      agentes_sugeridos: true
    });

    await act(async () => {
      concluir({ ok: true, status: 201, espaco: { id: 'e2' } });
    });
    expect(mocks.push).toHaveBeenCalledWith('/dashboard/espacos/e2');
    expect(mocks.recarregar).toHaveBeenCalledTimes(1);
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
  });
});

describe('0040 AC-11: erro ao criar', () => {
  async function preencherEEnviar() {
    abrirPelaHome();
    fireEvent.change(campoNome(), { target: { value: 'Faculdade' } });
    fireEvent.click(botaoCriar());
  }

  it('422 mostra a mensagem junto ao campo e mantém os dados', async () => {
    mocks.criarEspaco.mockResolvedValue({
      ok: false,
      status: 422,
      erro: { erro: 'dados_invalidos', mensagem: 'Nome do espaço inválido.', campo: 'nome' }
    });
    await preencherEEnviar();
    expect(await screen.findByText('Nome do espaço inválido.')).toBeInTheDocument();
    expect(campoNome()).toHaveValue('Faculdade');
    expect(campoNome()).toHaveAttribute('aria-invalid', 'true');
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });

  it('API fora do ar mostra a mensagem geral e mantém os dados', async () => {
    mocks.criarEspaco.mockResolvedValue({
      ok: false,
      status: 503,
      erro: { erro: 'api_indisponivel', mensagem: 'x' }
    });
    await preencherEEnviar();
    expect(await screen.findByText(MENSAGENS.indisponivel)).toBeInTheDocument();
    expect(campoNome()).toHaveValue('Faculdade');
    expect(botaoCriar()).toBeEnabled();
  });

  it('sessão expirada (401) encerra a sessão', async () => {
    mocks.criarEspaco.mockResolvedValue({
      ok: false,
      status: 401,
      erro: { erro: 'token_invalido', mensagem: 'x' }
    });
    await preencherEEnviar();
    await waitFor(() => expect(mocks.signOut).toHaveBeenCalled());
  });
});

describe('0040 AC-12: cancelar', () => {
  it.each([
    ['Cancelar', () => fireEvent.click(screen.getByRole('button', { name: 'Cancelar' }))],
    ['×', () => fireEvent.click(screen.getByRole('button', { name: 'Fechar' }))],
    ['Esc', () => fireEvent.keyDown(screen.getByRole('dialog'), { key: 'Escape' })]
  ])('%s fecha sem chamar a API e reabrir volta ao início', async (_, fechar) => {
    abrirPelaHome();
    fireEvent.change(campoNome(), { target: { value: 'Rascunho' } });
    fireEvent.click(tipo('Pessoal'));
    fechar();
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
    expect(mocks.criarEspaco).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole('button', { name: 'Novo Espaço' }));
    expect(campoNome()).toHaveValue('');
    expect(tipo('Trabalho')).toBeChecked();
    expect(campoMeta()).toHaveValue('30');
  });
});
