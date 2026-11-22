'use client';

import { usePathname } from 'next/navigation';
import { useMemo } from 'react';

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

export function useBreadcrumbs() {
  const pathname = usePathname() ?? '';
  return useMemo(() => trilhaDe(pathname), [pathname]);
}
