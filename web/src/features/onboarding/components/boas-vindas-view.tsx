'use client';

import { useRouter } from 'next/navigation';

import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle
} from '@/components/ui/card';
import { AuthShell } from '@/features/auth/components/auth-shell';
import { DASHBOARD_ROOT_PATH } from '@/features/onboarding/routing';
import {
  lerBoasVindasPendentes,
  limparBoasVindasPendentes
} from '@/features/onboarding/welcome-state';
import { useUsuarioNeo } from './neo-access-guard';

/** AC-13: tela exibida uma vez após concluir o Primeiro acesso. */
export function BoasVindasView() {
  const router = useRouter();
  const contextoUsuario = useUsuarioNeo();
  const pendente = lerBoasVindasPendentes();

  const nomeExibicao =
    contextoUsuario?.usuario.nome_exibicao ?? pendente?.nomeExibicao ?? 'por aqui';
  const nomeEspaco = contextoUsuario?.usuario.espacos[0]?.nome ?? pendente?.nomeEspaco ?? '';

  function irParaPainel() {
    limparBoasVindasPendentes();
    router.replace(DASHBOARD_ROOT_PATH);
  }

  return (
    <AuthShell>
      <Card className='w-full'>
        <CardHeader>
          <CardTitle>Boas-vindas, {nomeExibicao}</CardTitle>
          <CardDescription>
            Seu primeiro acesso está pronto para começar a organizar seus projetos no Neo.
          </CardDescription>
        </CardHeader>
        <CardContent className='space-y-2'>
          {nomeEspaco ? (
            <p className='text-sm'>
              Espaço inicial criado: <strong className='font-semibold'>{nomeEspaco}</strong>
            </p>
          ) : null}
        </CardContent>
        <CardFooter>
          <Button type='button' className='w-full' onClick={irParaPainel}>
            Ir para o painel
          </Button>
        </CardFooter>
      </Card>
    </AuthShell>
  );
}
