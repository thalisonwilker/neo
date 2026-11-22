import { fireEvent, render, screen, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { UsuarioDTO } from '@/lib/api';

const mocks = vi.hoisted(() => ({
  usuario: null as UsuarioDTO | null
}));

vi.mock('@/features/onboarding/components/neo-access-guard', () => ({
  useUsuarioNeo: () => (mocks.usuario ? { usuario: mocks.usuario, recarregar: vi.fn() } : null)
}));

import { HomeView } from './home-view';

const HOJE = new Date(2026, 10, 22, 10, 0, 0);

const usuarioBase: UsuarioDTO = {
  id: 'u1',
  email: 'dev@neo.app',
  nome_exibicao: 'Thalyson',
  primeiro_acesso_concluido: true,
  espacos: [
    {
      id: 'e2',
      nome: 'Faculdade',
      tipo: 'estudos',
      criado_em: '2026-11-22T13:00:00Z',
      meta_semanal: 10,
      agentes_sugeridos: false
    },
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

beforeEach(() => {
  mocks.usuario = usuarioBase;
});

describe('0038 AC-1: saudação e data de hoje', () => {
  it('mostra "Olá, Thalyson", o subtítulo e a data de hoje', () => {
    render(<HomeView hoje={HOJE} />);
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Olá, Thalyson');
    expect(
      screen.getByText('Sua agenda com todos os Espaços. Acesse um deles ou crie um novo.')
    ).toBeInTheDocument();
    expect(screen.getByText('Dom, 22 Nov 2026')).toBeInTheDocument();
  });

  it('sem nome de exibição, mostra só "Olá"', () => {
    mocks.usuario = { ...usuarioBase, nome_exibicao: null };
    render(<HomeView hoje={HOJE} />);
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(/^Olá$/);
  });
});

describe('0038 AC-2: contadores de tarefas vazios', () => {
  it('mostra Hoje, Esta semana, Este mês e Este ano, todos com 0 tarefas', () => {
    render(<HomeView hoje={HOJE} />);
    const itens = within(screen.getByRole('list', { name: 'Tarefas por período' })).getAllByRole(
      'listitem'
    );
    expect(itens.map((i) => i.textContent)).toEqual([
      '0Hojetarefas',
      '0Esta semanatarefas',
      '0Este mêstarefas',
      '0Este anotarefas'
    ]);
  });
});

describe('0038 AC-3: calendário do mês', () => {
  it('mostra novembro de 2026 a partir do domingo, com hoje destacado e sem itens', () => {
    render(<HomeView hoje={HOJE} />);
    expect(screen.getByRole('heading', { name: 'novembro de 2026' })).toBeInTheDocument();
    const tabela = screen.getByRole('table', { name: 'Calendário de novembro de 2026' });
    const cabecalhos = within(tabela)
      .getAllByRole('columnheader')
      .map((c) => c.textContent);
    expect(cabecalhos).toEqual(['dom.', 'seg.', 'ter.', 'qua.', 'qui.', 'sex.', 'sáb.']);

    const hoje = tabela.querySelector('[aria-current="date"]');
    expect(hoje).toHaveTextContent('22');

    const celulas = within(tabela).getAllByRole('cell');
    expect(celulas).toHaveLength(35);
    expect(celulas.every((c) => c.children.length === 1)).toBe(true);
    expect(tabela.querySelectorAll('[data-fora-do-mes]')).toHaveLength(5);
  });
});

describe('0038 AC-4: navegar no calendário', () => {
  it('avança, volta e retorna ao mês atual', () => {
    render(<HomeView hoje={HOJE} />);
    fireEvent.click(screen.getByRole('button', { name: 'Próximo mês' }));
    expect(screen.getByRole('heading', { name: 'dezembro de 2026' })).toBeInTheDocument();
    expect(document.querySelector('[aria-current="date"]')).toBeNull();

    fireEvent.click(screen.getByRole('button', { name: 'Mês anterior' }));
    fireEvent.click(screen.getByRole('button', { name: 'Mês anterior' }));
    expect(screen.getByRole('heading', { name: 'outubro de 2026' })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Hoje' }));
    expect(screen.getByRole('heading', { name: 'novembro de 2026' })).toBeInTheDocument();
  });
});

describe('0038 AC-5: lista de Espaços reais', () => {
  it('lista os Espaços na ordem de criação com rótulo, cor e tipo', () => {
    render(<HomeView hoje={HOJE} />);
    const cartao = screen.getByRole('heading', { name: 'Espaços' }).closest('section')!;
    const itens = within(cartao).getAllByRole('listitem');
    expect(itens.map((i) => i.getAttribute('data-tipo'))).toEqual(['trabalho', 'estudos']);
    expect(itens[0]).toHaveTextContent('NeoTrabalho · sem tarefas ainda');
    expect(itens[1]).toHaveTextContent('FaculdadeEstudos · sem tarefas ainda');
    expect(itens[0].querySelector('span')).toHaveStyle({ color: '#00FFB2' });
    expect(itens[1].querySelector('span')).toHaveStyle({ color: '#38BDF8' });
  });

  it('sem Espaços, mostra "Nenhum Espaço ainda."', () => {
    mocks.usuario = { ...usuarioBase, espacos: [] };
    render(<HomeView hoje={HOJE} />);
    expect(screen.getByText('Nenhum Espaço ainda.')).toBeInTheDocument();
  });

  it('nome longo fica inteiro no title', () => {
    const nome = 'Faculdade · Ciência da Computação e Engenharia';
    mocks.usuario = {
      ...usuarioBase,
      espacos: [
        {
          id: 'e1',
          nome,
          tipo: 'estudos',
          criado_em: '2026-11-22T12:00:00Z',
          meta_semanal: 10,
          agentes_sugeridos: false
        }
      ]
    };
    render(<HomeView hoje={HOJE} />);
    expect(screen.getByTitle(nome)).toHaveClass('truncate');
  });
});

describe('0038 AC-6: próximas tarefas vazias', () => {
  it('mostra o estado vazio', () => {
    render(<HomeView hoje={HOJE} />);
    expect(screen.getByRole('heading', { name: 'Próximas tarefas' })).toBeInTheDocument();
    expect(
      screen.getByText('Nenhuma tarefa ainda. Crie a primeira para vê-la no calendário.')
    ).toBeInTheDocument();
  });
});
