'use client';

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
import { useSignOut } from '@/features/auth/use-sign-out';

/** AC-14: tela exibida quando a API responde 403 `acesso_nao_liberado`. */
export function AcessoNaoLiberadoView() {
  const sair = useSignOut();

  return (
    <AuthShell>
      <Card className='w-full'>
        <CardHeader>
          <CardTitle>Acesso não liberado</CardTitle>
          <CardDescription>
            O seu e-mail ainda não está autorizado para acessar este painel do Neo.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className='text-muted-foreground text-sm'>
            Peça ao mantenedor para liberar o seu e-mail na lista de permissão e tente entrar
            novamente.
          </p>
        </CardContent>
        <CardFooter>
          <Button type='button' variant='outline' className='w-full' onClick={() => void sair()}>
            Sair
          </Button>
        </CardFooter>
      </Card>
    </AuthShell>
  );
}
