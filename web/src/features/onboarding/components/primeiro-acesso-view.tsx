'use client';

import { MAX_NOME_ESPACO } from '@/features/espacos/perfis';
import { useAuth } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { AuthShell } from '@/features/auth/components/auth-shell';
import { useSignOut } from '@/features/auth/use-sign-out';
import { DASHBOARD_ROOT_PATH } from '@/features/onboarding/routing';
import { marcarBoasVindasPendentes } from '@/features/onboarding/welcome-state';
import { submitPrimeiroAcesso, type TipoEspaco } from '@/lib/api';

const TIPOS_ESPACO: ReadonlyArray<{ valor: TipoEspaco; rotulo: string }> = [
  { valor: 'trabalho', rotulo: 'Trabalho' },
  { valor: 'estudos', rotulo: 'Estudos' },
  { valor: 'hobbies', rotulo: 'Hobbies' },
  { valor: 'pessoal', rotulo: 'Pessoal' }
];

/** AC-12: coleta Nome de exibição e primeiro Espaço no primeiro acesso. */
export function PrimeiroAcessoView() {
  const { getToken } = useAuth();
  const router = useRouter();
  const signOut = useSignOut();

  const [nomeExibicao, setNomeExibicao] = useState('');
  const [nomeEspaco, setNomeEspaco] = useState('');
  const [tipoEspaco, setTipoEspaco] = useState<TipoEspaco>('trabalho');
  const [enviando, setEnviando] = useState(false);
  const [errosCampo, setErrosCampo] = useState<Record<string, string>>({});
  const [erroGeral, setErroGeral] = useState<string | null>(null);

  async function aoEnviar(evento: React.FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (enviando) return;

    setEnviando(true);
    setErrosCampo({});
    setErroGeral(null);

    const token = await getToken();
    const resultado = await submitPrimeiroAcesso(token, {
      nome_exibicao: nomeExibicao,
      espaco: {
        nome: nomeEspaco,
        tipo: tipoEspaco
      }
    });

    if (resultado.ok) {
      const nomeFinal = resultado.usuario.nome_exibicao ?? nomeExibicao.trim();
      const espacoCriado = resultado.usuario.espacos[0]?.nome ?? nomeEspaco.trim();
      marcarBoasVindasPendentes({
        nomeExibicao: nomeFinal,
        nomeEspaco: espacoCriado
      });
      router.replace('/boas-vindas');
      return;
    }

    setEnviando(false);

    if (resultado.status === 409) {
      router.replace(DASHBOARD_ROOT_PATH);
      return;
    }

    if (resultado.status === 401) {
      void signOut();
      return;
    }

    if (resultado.status === 422 && resultado.erro.campo) {
      setErrosCampo({ [resultado.erro.campo]: resultado.erro.mensagem });
      return;
    }

    setErroGeral(resultado.erro.mensagem);
  }

  return (
    <AuthShell>
      <Card className='w-full'>
        <CardHeader>
          <CardTitle>Primeiro acesso</CardTitle>
          <CardDescription>
            Escolha como deseja ser chamado e crie o seu primeiro espaço no Neo.
          </CardDescription>
        </CardHeader>
        <form onSubmit={(e) => void aoEnviar(e)} noValidate>
          <CardContent className='space-y-4'>
            <div className='space-y-1.5'>
              <Label htmlFor='nome-exibicao'>Nome de exibição</Label>
              <Input
                id='nome-exibicao'
                name='nome_exibicao'
                placeholder='Ex.: Thalyson'
                value={nomeExibicao}
                onChange={(e) => setNomeExibicao(e.target.value)}
                aria-invalid={Boolean(errosCampo.nome_exibicao)}
                disabled={enviando}
              />
              {errosCampo.nome_exibicao ? (
                <p role='alert' className='text-destructive text-xs'>
                  {errosCampo.nome_exibicao}
                </p>
              ) : null}
            </div>

            <div className='space-y-1.5'>
              <Label htmlFor='nome-espaco'>Nome do espaço</Label>
              <Input
                id='nome-espaco'
                name='espaco_nome'
                maxLength={MAX_NOME_ESPACO}
                placeholder='Ex.: Neo'
                value={nomeEspaco}
                onChange={(e) => setNomeEspaco(e.target.value)}
                aria-invalid={Boolean(errosCampo['espaco.nome'])}
                disabled={enviando}
              />
              {errosCampo['espaco.nome'] ? (
                <p role='alert' className='text-destructive text-xs'>
                  {errosCampo['espaco.nome']}
                </p>
              ) : null}
            </div>

            <fieldset className='space-y-2' disabled={enviando}>
              <legend className='text-sm leading-none font-medium'>Tipo do espaço</legend>
              <div className='grid grid-cols-2 gap-2'>
                {TIPOS_ESPACO.map((opcao) => {
                  const selecionado = tipoEspaco === opcao.valor;
                  return (
                    <Button
                      key={opcao.valor}
                      type='button'
                      variant={selecionado ? 'default' : 'outline'}
                      aria-pressed={selecionado}
                      onClick={() => setTipoEspaco(opcao.valor)}
                      disabled={enviando}
                    >
                      {opcao.rotulo}
                    </Button>
                  );
                })}
              </div>
              {errosCampo['espaco.tipo'] ? (
                <p role='alert' className='text-destructive text-xs'>
                  {errosCampo['espaco.tipo']}
                </p>
              ) : null}
            </fieldset>

            {erroGeral ? (
              <p role='alert' className='text-destructive text-sm'>
                {erroGeral}
              </p>
            ) : null}
          </CardContent>
          <CardFooter className='pt-4'>
            <Button type='submit' className='w-full' disabled={enviando}>
              {enviando ? 'Salvando…' : 'Continuar'}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </AuthShell>
  );
}
