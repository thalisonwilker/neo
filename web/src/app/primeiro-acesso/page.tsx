import { auth } from '@clerk/nextjs/server';
import type { Metadata } from 'next';

import { NeoAccessGuard } from '@/features/onboarding/components/neo-access-guard';
import { PrimeiroAcessoView } from '@/features/onboarding/components/primeiro-acesso-view';

export const metadata: Metadata = {
  title: 'Primeiro acesso | NEO',
  description: 'Defina seu nome de exibição e crie o primeiro espaço no Neo.'
};

export default async function PrimeiroAcessoPage() {
  await auth.protect();
  return (
    <NeoAccessGuard>
      <PrimeiroAcessoView />
    </NeoAccessGuard>
  );
}
