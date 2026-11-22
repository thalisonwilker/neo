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

/** AC-15: tela exibida quando a API está fora do ar ou responde 5xx. */
export function ApiIndisponivelView({ onRetry }: { onRetry: () => void }) {
  return (
    <AuthShell>
      <Card className='w-full'>
        <CardHeader>
          <CardTitle>Não foi possível falar com o Neo agora</CardTitle>
          <CardDescription>
            A API do Neo está temporariamente indisponível ou não respondeu a tempo.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className='text-muted-foreground text-sm'>
            Verifique se o serviço da API está no ar e tente novamente.
          </p>
        </CardContent>
        <CardFooter>
          <Button type='button' className='w-full' onClick={onRetry}>
            Tentar de novo
          </Button>
        </CardFooter>
      </Card>
    </AuthShell>
  );
}
