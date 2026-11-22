'use client';

import { usePathname } from 'next/navigation';
import { useMemo } from 'react';

import { useUsuarioNeo } from '@/features/onboarding/components/neo-access-guard';

export type BreadcrumbItem = {
  title: string;
  link: string;
};

/** 0039 AC-4: trilha de cada página do painel do Neo. */
const TRILHAS: Record<string, BreadcrumbItem[]> = {
  '/dashboard/overview': [{ title: 'Início', link: '/dashboard/overview' }],
  '/dashboard/profile': [{ title: 'Minha conta', link: '/dashboard/profile' }]
};

export function trilhaDe(pathname: string): BreadcrumbItem[] {
  const base = Object.keys(TRILHAS).find(
    (rota) => pathname === rota || pathname.startsWith(`${rota}/`)
  );
  return base ? TRILHAS[base] : [];
}

const PREFIXO_ESPACO = '/dashboard/espacos/';

/** 0040 AC-13: no dashboard de um Espaço, a trilha é o nome dele. */
export function trilhaDoEspaco(
  pathname: string,
  espacos: readonly { id: string; nome: string }[]
): BreadcrumbItem[] | null {
  if (!pathname.startsWith(PREFIXO_ESPACO)) return null;
  const id = pathname.slice(PREFIXO_ESPACO.length).split('/')[0];
  const espaco = espacos.find((e) => e.id === id);
  return [{ title: espaco?.nome ?? 'Espaço', link: pathname }];
}

export function useBreadcrumbs() {
  const pathname = usePathname() ?? '';
  const espacos = useUsuarioNeo()?.usuario.espacos;
  return useMemo(
    () => trilhaDoEspaco(pathname, espacos ?? []) ?? trilhaDe(pathname),
    [pathname, espacos]
  );
}
