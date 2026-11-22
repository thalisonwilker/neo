import { fireEvent, render, screen, within } from '@testing-library/react';
import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
  pathname: '/dashboard/overview',
  push: vi.fn(),
  signOut: vi.fn()
}));

// Clerk e Next simulados: nenhuma chamada externa real.
vi.mock('@clerk/nextjs', () => ({
  useUser: () => ({
    user: {
      fullName: 'Thalyson Wilker',
      imageUrl: '',
      emailAddresses: [{ emailAddress: 'dev@neo.app' }]
    }
  }),
  useClerk: () => ({ signOut: mocks.signOut })
}));
vi.mock('@clerk/nextjs/server', () => ({ auth: { protect: vi.fn() } }));
vi.mock('@/components/themes/font.config', () => ({ fontVariables: '' }));
vi.mock('next/navigation', () => ({
  usePathname: () => mocks.pathname,
  useRouter: () => ({ push: mocks.push, replace: vi.fn() })
}));

import { SidebarProvider } from '@/components/ui/sidebar';
import { metadata as rootMetadata } from '@/app/layout';
import { metadata as homeMetadata } from '@/app/dashboard/overview/page';
import { metadata as contaMetadata } from '@/app/dashboard/profile/[[...profile]]/page';
import AppSidebar from './app-sidebar';
import Header from './header';

const src = (p: string) => resolve(process.cwd(), 'src', p);

beforeEach(() => {
  mocks.pathname = '/dashboard/overview';
  // jsdom não implementa matchMedia (usado pelo menu lateral para detectar celular).
  window.matchMedia = vi.fn().mockReturnValue({
    matches: false,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn()
  });
});

describe('0039 AC-1: páginas e APIs de exemplo deixam de existir', () => {
  it.each([
    'app/dashboard/product',
    'app/dashboard/users',
    'app/dashboard/kanban',
    'app/dashboard/chat',
    'app/dashboard/ai-chat',
    'app/dashboard/forms',
    'app/dashboard/react-query',
    'app/dashboard/elements',
    'app/dashboard/exclusive',
    'app/dashboard/billing',
    'app/dashboard/notifications',
    'app/dashboard/workspaces',
    'app/api'
  ])('a rota %s não existe', (rota) => {
    expect(existsSync(src(rota))).toBe(false);
  });

  it('só restam as páginas do Neo', () => {
    expect(existsSync(src('app/dashboard/overview/page.tsx'))).toBe(true);
    expect(existsSync(src('app/dashboard/profile/[[...profile]]/page.tsx'))).toBe(true);
    expect(existsSync(src('app/primeiro-acesso/page.tsx'))).toBe(true);
    expect(existsSync(src('app/boas-vindas/page.tsx'))).toBe(true);
  });
});

function renderSidebar() {
  return render(
    <SidebarProvider defaultOpen>
      <AppSidebar />
    </SidebarProvider>
  );
}

describe('0039 AC-2: menu lateral do Neo', () => {
  it('mostra a marca NEO e um único item "Início", sem seletor de organização', () => {
    renderSidebar();
    expect(screen.getByRole('link', { name: 'NEO — Início' })).toHaveAttribute(
      'href',
      '/dashboard/overview'
    );
    const menu = screen.getByRole('list', { name: 'Menu principal' });
    const links = within(menu).getAllByRole('link');
    expect(links.map((l) => l.textContent)).toEqual(['Início']);
    expect(links[0]).toHaveAttribute('aria-current', 'page');
    expect(screen.queryByText(/organiza/i)).not.toBeInTheDocument();
  });

  it('o menu do usuário tem só "Minha conta" e "Sair"', async () => {
    renderSidebar();
    fireEvent.click(screen.getAllByText('Thalyson Wilker')[0]);
    const itens = await screen.findAllByRole('menuitem');
    expect(itens.map((i) => i.textContent)).toEqual(['Minha conta', 'Sair']);
  });

  it('"Minha conta" leva a /dashboard/profile (AC-3)', async () => {
    renderSidebar();
    fireEvent.click(screen.getAllByText('Thalyson Wilker')[0]);
    fireEvent.click(await screen.findByRole('menuitem', { name: 'Minha conta' }));
    expect(mocks.push).toHaveBeenCalledWith('/dashboard/profile');
  });
});

describe('0039 AC-3: Minha conta', () => {
  it('a página se chama "Minha conta | NEO"', () => {
    expect(contaMetadata.title).toBe('Minha conta | NEO');
  });
});

describe('0039 AC-4: cabeçalho enxuto', () => {
  function renderHeader() {
    return render(
      <SidebarProvider defaultOpen>
        <Header />
      </SidebarProvider>
    );
  }

  it('na página inicial, mostra só o botão do menu e a trilha "Início"', () => {
    renderHeader();
    const header = screen.getByRole('banner');
    expect(within(header).getAllByRole('button')).toHaveLength(1);
    expect(within(header).getByText('Início')).toBeInTheDocument();
    // Sem busca, GitHub, tema ou notificações: nenhum link de verdade no cabeçalho.
    expect(header.querySelectorAll('a')).toHaveLength(0);
  });

  it('em Minha conta, a trilha é "Minha conta"', () => {
    mocks.pathname = '/dashboard/profile/security';
    renderHeader();
    expect(within(screen.getByRole('banner')).getByText('Minha conta')).toBeInTheDocument();
  });
});

describe('0039 AC-5: tema único NEO escuro e identidade Neo', () => {
  it('o layout raiz fixa o tema NEO escuro, sem seletor nem cookie de tema', () => {
    const layout = readFileSync(src('app/layout.tsx'), 'utf8');
    expect(layout).toMatch(/data-theme='neo'/);
    expect(layout).toMatch(/className='dark'/);
    expect(layout).toMatch(/forcedTheme='dark'/);
    expect(layout).not.toMatch(/active_theme/);
    expect(existsSync(src('components/themes/theme-selector.tsx'))).toBe(false);
    expect(existsSync(src('components/themes/theme-mode-toggle.tsx'))).toBe(false);
  });

  it('só o tema NEO é carregado', () => {
    const css = readFileSync(src('styles/theme.css'), 'utf8');
    expect(css.match(/@import/g)).toHaveLength(1);
    expect(css).toMatch(/themes\/neo\.css/);
  });

  it('os metadados seguem o padrão "<página> | NEO" e não citam o template', () => {
    expect(rootMetadata.title).toEqual({ default: 'NEO', template: '%s' });
    expect(homeMetadata.title).toBe('Início | NEO');
    const textos = [rootMetadata.description, rootMetadata.applicationName].join(' ');
    expect(textos).not.toMatch(/shadcn|dashboard|kiranism/i);
    expect(rootMetadata.openGraph).toBeUndefined();
    expect(rootMetadata.twitter).toBeUndefined();
  });
});
