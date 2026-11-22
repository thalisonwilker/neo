'use client';

import { useAuth } from '@clerk/nextjs';
import { IconX } from '@tabler/icons-react';
import { useRouter } from 'next/navigation';
import { useId, useState } from 'react';
import type { CSSProperties, FormEvent } from 'react';

import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { useSignOut } from '@/features/auth/use-sign-out';
import { useUsuarioNeo } from '@/features/onboarding/components/neo-access-guard';
import { criarEspaco, type TipoEspaco } from '@/lib/api';
import { cn } from '@/lib/utils';
import {
  MAX_META_SEMANAL,
  MAX_NOME_ESPACO,
  MIN_META_SEMANAL,
  PERFIS_DE_TIPO,
  TIPOS_DE_ESPACO,
  rotaDoEspaco
} from '../perfis';
import { IconeDoTipoEspaco } from './icone-do-tipo';

type CampoDoFormulario = 'nome' | 'tipo' | 'meta_semanal';

export const MENSAGENS = {
  nomeVazio: 'Informe o nome do Espaço.',
  metaInvalida: `Use um número inteiro de horas entre ${MIN_META_SEMANAL} e ${MAX_META_SEMANAL}.`,
  indisponivel: 'Não foi possível criar o Espaço agora. Tente de novo.'
} as const;

/** AC-9: meta válida = inteiro (só dígitos) entre 1 e 168. */
export function validarMeta(texto: string): string | null {
  const limpo = texto.trim();
  if (!/^\d+$/.test(limpo)) return MENSAGENS.metaInvalida;
  const valor = Number(limpo);
  return valor >= MIN_META_SEMANAL && valor <= MAX_META_SEMANAL ? null : MENSAGENS.metaInvalida;
}

const fonteDisplay = 'font-[family-name:var(--font-display)]';

/** 0040 AC-7 a AC-12: modal "Criar Espaço". */
export function CriarEspacoModal({ aberto, aoFechar }: { aberto: boolean; aoFechar: () => void }) {
  const { getToken } = useAuth();
  const router = useRouter();
  const signOut = useSignOut();
  const contextoUsuario = useUsuarioNeo();
  const idBase = useId();

  const [nome, setNome] = useState('');
  const [nomeTocado, setNomeTocado] = useState(false);
  const [tipo, setTipo] = useState<TipoEspaco>('trabalho');
  const [meta, setMeta] = useState(String(PERFIS_DE_TIPO.trabalho.metaSugerida));
  const [agentes, setAgentes] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [errosApi, setErrosApi] = useState<Partial<Record<CampoDoFormulario, string>>>({});
  const [erroGeral, setErroGeral] = useState<string | null>(null);

  const erroNome = nomeTocado && !nome.trim() ? MENSAGENS.nomeVazio : null;
  const erroMeta = validarMeta(meta);
  const valido = nome.trim().length > 0 && erroMeta === null;

  function escolherTipo(novo: TipoEspaco) {
    setTipo(novo);
    // AC-8: a meta passa a ser a Meta sugerida do tipo escolhido.
    setMeta(String(PERFIS_DE_TIPO[novo].metaSugerida));
    setErrosApi((e) => ({ ...e, tipo: undefined, meta_semanal: undefined }));
  }

  async function aoEnviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setNomeTocado(true);
    if (!valido || enviando) return;

    setEnviando(true);
    setErrosApi({});
    setErroGeral(null);
    const resultado = await criarEspaco(await getToken(), {
      nome: nome.trim(),
      tipo,
      meta_semanal: Number(meta.trim()),
      agentes_sugeridos: agentes
    });

    if (resultado.ok) {
      aoFechar();
      router.push(rotaDoEspaco(resultado.espaco.id));
      contextoUsuario?.recarregar();
      return;
    }

    setEnviando(false);
    if (resultado.status === 401) {
      void signOut();
      return;
    }
    if (resultado.status === 422 && resultado.erro.campo) {
      const campo = resultado.erro.campo as CampoDoFormulario;
      setErrosApi({ [campo]: resultado.erro.mensagem });
      return;
    }
    setErroGeral(
      resultado.status === 409 || resultado.status === 403
        ? resultado.erro.mensagem
        : MENSAGENS.indisponivel
    );
  }

  const mensagemNome = erroNome ?? errosApi.nome ?? null;
  const mensagemMeta = erroMeta ?? errosApi.meta_semanal ?? null;

  return (
    <Dialog open={aberto} onOpenChange={(abrir) => !abrir && aoFechar()}>
      <DialogContent
        showCloseButton={false}
        className='border-primary/15 max-h-[calc(100dvh-2rem)] gap-0 overflow-y-auto rounded-3xl border bg-linear-to-br from-[rgba(14,24,43,.97)] to-[rgba(10,17,32,.97)] p-6 shadow-[0_24px_80px_rgba(0,0,0,.6)] sm:max-w-3xl md:p-8'
      >
        <div className='flex items-start justify-between gap-4'>
          <div>
            <DialogTitle className={cn(fonteDisplay, 'text-2xl font-semibold md:text-[28px]')}>
              Criar Espaço
            </DialogTitle>
            <DialogDescription className='mt-2 text-sm md:text-base'>
              Escolha o tipo. Ele define o calendário, as tarefas, os agentes e as skills sugeridas.
            </DialogDescription>
          </div>
          <Button
            type='button'
            variant='outline'
            size='icon'
            aria-label='Fechar'
            className='border-primary/20 flex-none'
            onClick={aoFechar}
          >
            <IconX aria-hidden />
          </Button>
        </div>

        <form onSubmit={(e) => void aoEnviar(e)} noValidate className='mt-6 space-y-6'>
          <div className='space-y-2'>
            <Label htmlFor={`${idBase}-nome`} className='text-muted-foreground font-normal'>
              Nome do Espaço
            </Label>
            <Input
              id={`${idBase}-nome`}
              autoFocus
              value={nome}
              maxLength={MAX_NOME_ESPACO}
              placeholder='Ex.: Faculdade'
              onChange={(e) => {
                setNome(e.target.value);
                setErrosApi((er) => ({ ...er, nome: undefined }));
              }}
              onBlur={() => setNomeTocado(true)}
              aria-invalid={Boolean(mensagemNome)}
              aria-describedby={mensagemNome ? `${idBase}-nome-erro` : undefined}
              className='h-12 text-base'
            />
            {mensagemNome ? (
              <p id={`${idBase}-nome-erro`} role='alert' className='text-destructive text-xs'>
                {mensagemNome}
              </p>
            ) : null}
          </div>

          <fieldset className='space-y-3'>
            <legend className='text-muted-foreground mb-3 text-xs tracking-[0.12em] uppercase'>
              Tipo
            </legend>
            <div className='grid grid-cols-2 gap-3 md:grid-cols-4'>
              {TIPOS_DE_ESPACO.map((opcao) => {
                const perfil = PERFIS_DE_TIPO[opcao];
                const selecionado = tipo === opcao;
                return (
                  <label
                    key={opcao}
                    data-tipo={opcao}
                    data-selecionado={selecionado || undefined}
                    style={{ '--cor-tipo': perfil.cor } as CSSProperties}
                    className={cn(
                      'relative flex cursor-pointer flex-col gap-2 rounded-2xl border p-4 transition-colors md:p-5',
                      'has-focus-visible:ring-ring has-focus-visible:ring-2',
                      selecionado
                        ? 'border-(--cor-tipo) bg-[color-mix(in_srgb,var(--cor-tipo)_6%,transparent)] shadow-[0_0_24px_color-mix(in_srgb,var(--cor-tipo)_35%,transparent)]'
                        : 'border-border/70 hover:border-(--cor-tipo)/50'
                    )}
                  >
                    <input
                      type='radio'
                      name={`${idBase}-tipo`}
                      value={opcao}
                      checked={selecionado}
                      onChange={() => escolherTipo(opcao)}
                      className='sr-only'
                    />
                    <span
                      className='grid size-11 place-items-center rounded-xl border'
                      style={{ borderColor: `${perfil.cor}55` }}
                    >
                      <IconeDoTipoEspaco tipo={opcao} size={20} />
                    </span>
                    <span className={cn(fonteDisplay, 'mt-2 text-lg font-semibold')}>
                      {perfil.rotulo}
                    </span>
                    <span className='text-muted-foreground text-sm'>{perfil.descricao}</span>
                  </label>
                );
              })}
            </div>
            {errosApi.tipo ? (
              <p role='alert' className='text-destructive text-xs'>
                {errosApi.tipo}
              </p>
            ) : null}
          </fieldset>

          <div className='space-y-2'>
            <div className='flex items-center gap-4'>
              <Label htmlFor={`${idBase}-meta`} className='text-muted-foreground font-normal'>
                Meta semanal
              </Label>
              <Input
                id={`${idBase}-meta`}
                inputMode='numeric'
                value={meta}
                onChange={(e) => {
                  setMeta(e.target.value);
                  setErrosApi((er) => ({ ...er, meta_semanal: undefined }));
                }}
                aria-invalid={Boolean(mensagemMeta)}
                aria-describedby={mensagemMeta ? `${idBase}-meta-erro` : `${idBase}-meta-un`}
                className='h-12 w-24 font-mono text-base'
              />
              <span id={`${idBase}-meta-un`} className='text-muted-foreground'>
                horas
              </span>
            </div>
            {mensagemMeta ? (
              <p id={`${idBase}-meta-erro`} role='alert' className='text-destructive text-xs'>
                {mensagemMeta}
              </p>
            ) : null}
          </div>

          <div className='flex items-center gap-3'>
            <Switch
              id={`${idBase}-agentes`}
              checked={agentes}
              onCheckedChange={(v) => setAgentes(Boolean(v))}
            />
            <Label htmlFor={`${idBase}-agentes`} className='font-normal'>
              Criar agentes e skills sugeridos para este tipo
            </Label>
          </div>

          {erroGeral ? (
            <p role='alert' className='text-destructive text-sm'>
              {erroGeral}
            </p>
          ) : null}

          <div className='flex flex-col-reverse gap-3 sm:flex-row sm:justify-end'>
            <Button type='button' variant='outline' size='lg' onClick={aoFechar}>
              Cancelar
            </Button>
            <Button type='submit' size='lg' disabled={!valido || enviando}>
              {enviando ? 'Criando…' : 'Criar Espaço'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
