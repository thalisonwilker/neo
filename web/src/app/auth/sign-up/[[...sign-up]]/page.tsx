import SignUpViewPage from '@/features/auth/components/sign-up-view';
import { getPostLoginRedirect } from '@/features/auth/post-login';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Cadastrar | NEO',
  description: 'Crie sua conta para acessar o painel do NEO.'
};

export default async function Page({
  searchParams
}: {
  searchParams: Promise<{ redirect_url?: string | string[] }>;
}) {
  return <SignUpViewPage redirectUrl={await getPostLoginRedirect(searchParams)} />;
}
