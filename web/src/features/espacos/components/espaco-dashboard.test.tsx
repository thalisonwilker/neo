import { fireEvent, render, screen, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { EspacoDTO, UsuarioDTO } from '@/lib/api';

const mocks = vi.hoisted(() => ({
  pathname: '/dashboard/espacos/e2',
  usuario: null as UsuarioDTO | null
}));

// Clerk e Next simulados: nenhuma chamada externa real.
vi.mock('@clerk/nextjs', () => ({
  useAuth: () => ({ getToken: vi.fn() }),
  useClerk: () => ({ signOut: vi.fn() }),
  useUser: () => ({
    user: { fullName: 'Thalyson', imageUrl: '', emailAddresses: [{ emailAddress: 'd@neo.app' }] }
  })
}));
vi.mock('next/navigation', () => ({
  usePathname: () => mocks.pathname,
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() })
}));
vi.mock('@/features/onboarding/components/neo-access-guard', () => ({
  useUsuarioNeo: () => (mocks.usuario ? { usuario: mocks.usuario, recarregar: vi.fn() } : null)
}));

import AppSidebar from '@/components/layout/app-sidebar';
import Header from '@/components/layout/header';
import { SidebarProvider } from '@/components/ui/sidebar';
import { CriarEspacoProvider } from './criar-espaco-provider';
import { EspacoView, SUGESTOES_DO_NEO } from './espaco-dashboard';

const espaco = (parcial: Partial<EspacoDTO> & Pick<EspacoDTO, 'id' | 'tipo'>): EspacoDTO => ({
  nome: `Espaço ${parcial.id}`,
  criado_em: '2026-11-22T12:00:00Z',
  meta_semanal: 30,
  agentes_sugeridos: false,
  ...parcial
});

const usuarioBase = (espacos: EspacoDTO[]): UsuarioDTO => ({
  id: 'u1',
  email: 'dev@neo.app',
  nome_exibicao: 'Thalyson',
  primeiro_acesso_concluido: true,
  espacos
});

beforeEach(() => {
  mocks.pathname = '/dashboard/espacos/e2';
  window.matchMedia = vi.fn().mockReturnValue({
    matches: false,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn()
  });
  mocks.usuario = usuarioBase([
    espaco({ id: 'e1', nome: 'Neo', tipo: 'trabalho', criado_em: '2026-11-22T10:00:00Z' }),
    espaco({
      id: 'e2',
      nome: 'Novo Espaço de trabalho',
      tipo: 'trabalho',
      criado_em: '2026-11-22T11:00:00Z'
    })
  ]);
});

describe('0040 AC-13: dashboard vazio do Espaço', () => {
  it('mostra nome, subtítulo, os 4 indicadores e os 6 cartões vazios', () => {
    render(<EspacoView id='e2' />);
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Novo Espaço de trabalho');
    expect(screen.getByText('Trabalho · visão geral do Espaço')).toBeInTheDocument();

    const indicadores = within(screen.getByRole('list', { name: 'Indicadores do Espaço' }))
      .getAllByRole('listitem')
      .map((i) => i.textContent);
    expect(indicadores).toEqual([
      '0Tarefas abertas0 concluídas',
      '0hHoras na semanameta de 30h',
      '0Projetos ativosnenhum ainda',
      '0Deploys no mêsneste mês'
    ]);

    const cartoes = screen.getAllByRole('heading', { level: 2 }).map((h) => h.textContent);
    expect(cartoes).toEqual([
      'Em andamento e para hoje',
      'Horas por dia',
      'Projetos',
      'Agenda',
      'Sugestões do NEO',
      'Hábitos'
    ]);
    expect(screen.getByText('Nenhuma tarefa em andamento.')).toBeInTheDocument();
    expect(screen.getByText('0h na semana')).toBeInTheDocument();
    expect(document.querySelectorAll('[data-horas="0"]')).toHaveLength(7);
    expect(screen.getByText('Nenhum projeto ainda.')).toBeInTheDocument();
    expect(screen.getByText('Nenhum compromisso agendado.')).toBeInTheDocument();
    for (const sugestao of SUGESTOES_DO_NEO) {
      expect(screen.getByText(sugestao)).toBeInTheDocument();
    }
    expect(screen.queryByRole('button', { name: 'Fazer' })).not.toBeInTheDocument();
    expect(screen.getByText('Os hábitos deste Espaço aparecem aqui.')).toBeInTheDocument();
    expect(document.title).toBe('Novo Espaço de trabalho | NEO');
  });

  it.each([
    ['estudos', 'Estudos', '#38BDF8', '0 diasSequência de estudoneste mês', 10],
    ['hobbies', 'Hobbies', '#A78BFA', '0Sessões na semananeste mês', 8],
    ['pessoal', 'Pessoal', '#F472B6', '0Contas a pagarneste mês', 8]
  ] as const)('tipo %s usa a cor e o 4º indicador do tipo', (tipo, rotulo, cor, quarto, meta) => {
    mocks.usuario = usuarioBase([espaco({ id: 'e9', tipo, meta_semanal: meta })]);
    const { container } = render(<EspacoView id='e9' />);
    expect(screen.getByText(`${rotulo} · visão geral do Espaço`)).toBeInTheDocument();
    expect((container.firstChild as HTMLElement).style.getPropertyValue('--cor-tipo')).toBe(cor);
    const itens = within(screen.getByRole('list', { name: 'Indicadores do Espaço' })).getAllByRole(
      'listitem'
    );
    expect(itens[1]).toHaveTextContent(`meta de ${meta}h`);
    expect(itens[3].textContent).toBe(quarto);
  });

  it('a trilha do cabeçalho mostra o nome do Espaço', () => {
    render(
      <SidebarProvider defaultOpen>
        <Header />
      </SidebarProvider>
    );
    expect(within(screen.getByRole('banner')).getByText('Novo Espaço de trabalho')).toBeVisible();
  });
});

describe('0040 AC-14: Espaço inexistente', () => {
  it('mostra "Espaço não encontrado" com link para o Início', () => {
    render(<EspacoView id='de-outro-usuario' />);
    expect(screen.getByRole('heading', { name: 'Espaço não encontrado' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Ir para o Início' })).toHaveAttribute(
      'href',
      '/dashboard/overview'
    );
    expect(screen.queryByText('Neo')).not.toBeInTheDocument();
  });
});

function renderSidebar() {
  return render(
    <SidebarProvider defaultOpen>
      <CriarEspacoProvider>
        <AppSidebar />
      </CriarEspacoProvider>
    </SidebarProvider>
  );
}

describe('0040 AC-15: Espaços no menu lateral', () => {
  it('lista os Espaços na ordem de criação, destaca o aberto e termina com "Novo Espaço"', () => {
    renderSidebar();
    const grupo = screen.getByRole('list', { name: 'Espaços' });
    const itens = within(grupo).getAllByRole('listitem');
    expect(itens.map((i) => i.textContent)).toEqual([
      'Neo',
      'Novo Espaço de trabalho',
      'Novo Espaço'
    ]);
    expect(within(itens[0]).getByRole('link')).toHaveAttribute('href', '/dashboard/espacos/e1');
    expect(within(itens[1]).getByRole('link')).toHaveAttribute('aria-current', 'page');
    expect(within(itens[0]).getByRole('link')).not.toHaveAttribute('aria-current');
    expect(itens[0]).toHaveAttribute('data-tipo', 'trabalho');
    expect(itens[0].querySelector('svg')).toHaveStyle({ color: '#00FFB2' });
  });

  it('nome longo é cortado com reticências e fica inteiro no title', () => {
    const longo = 'Faculdade · Ciência da Computação e Engenharia de Software';
    mocks.usuario = usuarioBase([espaco({ id: 'e3', nome: longo, tipo: 'estudos' })]);
    renderSidebar();
    const link = screen.getByRole('link', { name: longo });
    expect(link).toHaveAttribute('title', longo);
    expect(within(link).getByText(longo)).toHaveClass('truncate');
  });

  it('"Novo Espaço" abre o modal "Criar Espaço" (AC-7)', () => {
    renderSidebar();
    fireEvent.click(within(screen.getByRole('list', { name: 'Espaços' })).getByText('Novo Espaço'));
    expect(screen.getByRole('dialog')).toHaveTextContent('Criar Espaço');
  });
});
