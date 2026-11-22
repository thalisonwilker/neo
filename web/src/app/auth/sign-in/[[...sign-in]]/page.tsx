import SignInViewPage from '@/features/auth/components/sign-in-view';
import { getPostLoginRedirect } from '@/features/auth/post-login';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Entrar | NEO',
  description: 'Entre no painel do NEO.'
};

export default async function Page({
  searchParams
}: {
  searchParams: Promise<{ redirect_url?: string | string[] }>;
}) {
  return <SignInViewPage redirectUrl={await getPostLoginRedirect(searchParams)} />;
}
