'use client';

import { useClerk } from '@clerk/nextjs';

import { SIGN_IN_PATH } from './access';

/** Texto do item de saída no menu do usuário. */
export const SIGN_OUT_LABEL = 'Sair';

/** AC-12: encerra a sessão no Clerk e leva o usuário à tela de entrada. */
export function useSignOut() {
  const { signOut } = useClerk();
  return () => signOut({ redirectUrl: SIGN_IN_PATH });
}
