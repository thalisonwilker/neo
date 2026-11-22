import { render, screen } from '@testing-library/react';
import { ptBR } from '@clerk/localizations';
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative, resolve } from 'node:path';
import type { ReactNode } from 'react';
import { describe, expect, it, vi } from 'vitest';

const captured = vi.hoisted(() => ({ props: undefined as Record<string, unknown> | undefined }));

// Clerk simulado: nenhuma chamada externa real.
vi.mock('@clerk/nextjs', () => ({
  ClerkProvider: ({ children, ...props }: { children: ReactNode }) => {
    captured.props = props;
    return <div data-testid='clerk-provider'>{children}</div>;
  }
}));

import Providers from '@/components/layout/providers';
import { localization } from './localization';

// Os testes rodam a partir de web/ (`npm run test`).
const srcRoot = resolve(process.cwd(), 'src');

function sourceFiles(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const full = join(dir, name);
    if (statSync(full).isDirectory()) return sourceFiles(full);
    return /\.(ts|tsx)$/.test(name) && !/\.test\.(ts|tsx)$/.test(name) ? [full] : [];
  });
}

describe('AC-8: provedor único e português do Brasil', () => {
  it('AC-8: existe um único ClerkProvider no código, em components/layout/providers.tsx', () => {
    const opening = new RegExp(['<Clerk', 'Provider\\b'].join(''));
    const withProvider = sourceFiles(srcRoot)
      .filter((file) => opening.test(readFileSync(file, 'utf8')))
      .map((file) => relative(srcRoot, file));
    expect(withProvider).toEqual(['components/layout/providers.tsx']);
  });

  it('AC-8: app/layout.tsx não importa o Clerk', () => {
    const layout = readFileSync(join(srcRoot, 'app/layout.tsx'), 'utf8');
    expect(layout).not.toMatch(/@clerk\//);
  });

  it('AC-8: o provedor aplica a localização ptBR', () => {
    render(
      <Providers>
        <p>conteúdo</p>
      </Providers>
    );
    expect(screen.getByText('conteúdo')).toBeInTheDocument();
    // pt-BR oficial + as traduções que o pacote não traz (features/auth/localization.ts).
    expect(captured.props?.localization).toBe(localization);
    expect(captured.props?.localization).toMatchObject({ locale: ptBR.locale });
  });

  it('AC-8: o documento declara o idioma pt-BR', () => {
    const layout = readFileSync(join(srcRoot, 'app/layout.tsx'), 'utf8');
    expect(layout).toMatch(/<html[^>]*lang='pt-BR'/);
  });
});
