import { auth } from '@clerk/nextjs/server';
import type { Metadata } from 'next';

import ProfileViewPage from '@/features/profile/components/profile-view-page';

export const metadata: Metadata = {
  title: 'Minha conta | NEO'
};

/** 0039 AC-3: tela de conta do Usuário (Clerk), aberta por "Minha conta". */
export default async function MinhaContaPage() {
  await auth.protect();

  return <ProfileViewPage />;
}
