// @vitest-environment node
import { describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
  protect: vi.fn(),
  cookies: vi.fn()
}));

// Clerk simulado: nenhuma chamada externa real.
vi.mock('@clerk/nextjs/server', () => ({ auth: { protect: mocks.protect } }));
vi.mock('next/headers', () => ({ cookies: mocks.cookies }));

// Componentes visuais simulados: o teste cobre só a regra de acesso do layout.
vi.mock('@/components/layout/app-sidebar', () => ({ default: () => null }));
vi.mock('@/components/layout/header', () => ({ default: () => null }));
vi.mock('@/features/espacos/components/criar-espaco-provider', () => ({
  CriarEspacoProvider: () => null
}));
vi.mock('@/components/ui/sidebar', () => ({
  SidebarInset: () => null,
  SidebarProvider: () => null
}));

import DashboardLayout from './layout';

describe('AC-6: defesa em profundidade no layout do /dashboard', () => {
  it('AC-6: sem sessão (auth.protect interrompe), o layout não renderiza o conteúdo', async () => {
    mocks.protect.mockRejectedValue(new Error('NEXT_REDIRECT:/auth/sign-in'));

    await expect(DashboardLayout({ children: 'conteúdo protegido' })).rejects.toThrow(
      'NEXT_REDIRECT:/auth/sign-in'
    );
    // Nada além da checagem de acesso foi executado.
    expect(mocks.cookies).not.toHaveBeenCalled();
  });

  it('AC-6: exige a sessão por conta própria, antes de qualquer outra coisa', async () => {
    mocks.protect.mockResolvedValue({ userId: 'user_123' });
    mocks.cookies.mockResolvedValue({ get: () => undefined });

    const element = await DashboardLayout({ children: 'conteúdo' });

    expect(mocks.protect).toHaveBeenCalledTimes(1);
    expect(element).toBeDefined();
  });
});
