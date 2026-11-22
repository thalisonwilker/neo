import { auth } from '@clerk/nextjs/server';
import type { Metadata } from 'next';

import { HomeView } from '@/features/home/components/home-view';

export const metadata: Metadata = {
  title: 'Início · Neo'
};

/** Página inicial do painel (spec 0038), destino pós-login. */
export default async function InicioPage() {
  await auth.protect();
  return <HomeView />;
}
