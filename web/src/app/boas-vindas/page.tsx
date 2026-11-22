import { auth } from '@clerk/nextjs/server';
import type { Metadata } from 'next';

import { BoasVindasView } from '@/features/onboarding/components/boas-vindas-view';
import { NeoAccessGuard } from '@/features/onboarding/components/neo-access-guard';

export const metadata: Metadata = {
  title: 'Boas-vindas | NEO',
  description: 'Boas-vindas ao painel do Neo.'
};

export default async function BoasVindasPage() {
  await auth.protect();
  return (
    <NeoAccessGuard>
      <BoasVindasView />
    </NeoAccessGuard>
  );
}
