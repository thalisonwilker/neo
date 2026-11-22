'use client';

import {
  IconChartLine,
  IconCheck,
  IconClock,
  IconFolder,
  IconListCheck,
  IconSparkles
} from '@tabler/icons-react';
import Link from 'next/link';
import type { ComponentType, CSSProperties, ReactNode } from 'react';

import { DIAS_DA_SEMANA } from '@/features/home/home-rules';
import { useUsuarioNeo } from '@/features/onboarding/components/neo-access-guard';
import type { EspacoDTO } from '@/lib/api';
import { cn } from '@/lib/utils';
import { PERFIS_DE_TIPO } from '../perfis';

const fonteDisplay = 'font-[family-name:var(--font-display)]';

export const SUGESTOES_DO_NEO = [
  'Crie o primeiro projeto deste Espaço',
  'Conecte uma integração',
  'Peça ao NEO um plano para a semana'
] as const;

function Cartao({
  titulo,
  icone: Icone,
  children,
  extra
}: {
  titulo: string;
  icone: ComponentType<{ size?: number; className?: string; 'aria-hidden'?: boolean }>;
  children: ReactNode;
  extra?: ReactNode;
}) {
  return (
    <section className='border-primary/15 relative flex min-h-56 min-w-0 flex-col rounded-2xl border bg-linear-to-br from-[rgba(14,24,43,.78)] to-[rgba(10,17,32,.62)] p-5 shadow-[0_14px_40px_rgba(0,0,0,.35)]'>
      <div className='mb-4 flex items-center gap-3'>
        <Icone size={20} className='text-(--cor-tipo)' aria-hidden />
        <h2 className={cn(fonteDisplay, 'text-base font-semibold')}>{titulo}</h2>
        {extra ? <div className='ml-auto'>{extra}</div> : null}
      </div>
      {children}
    </section>
  );
}

function Vazio({ children }: { children: ReactNode }) {
  return <p className='text-muted-foreground text-[13px]'>{children}</p>;
}

/** 0040 AC-13: dashboard vazio do Espaço, na cor e com os indicadores do tipo. */
function DashboardDoEspaco({ espaco }: { espaco: EspacoDTO }) {
  const perfil = PERFIS_DE_TIPO[espaco.tipo];
  const indicadores = [
    { valor: '0', titulo: 'Tarefas abertas', legenda: '0 concluídas' },
    { valor: '0h', titulo: 'Horas na semana', legenda: `meta de ${espaco.meta_semanal}h` },
    { valor: '0', titulo: 'Projetos ativos', legenda: 'nenhum ainda' },
    {
      valor: perfil.quartoIndicador.valorVazio,
      titulo: perfil.quartoIndicador.titulo,
      legenda: perfil.quartoIndicador.legenda
    }
  ];

  return (
    <div
      className='flex min-w-0 flex-1 flex-col gap-5 p-4 md:gap-6 md:p-6'
      style={{ '--cor-tipo': perfil.cor } as CSSProperties}
      data-tipo={espaco.tipo}
    >
      <header className='min-w-0'>
        <h1
          className={cn(
            fonteDisplay,
            'truncate text-[28px] leading-tight font-semibold text-(--cor-tipo) [text-shadow:0_0_22px_color-mix(in_srgb,var(--cor-tipo)_40%,transparent)]'
          )}
          title={espaco.nome}
        >
          {espaco.nome}
        </h1>
        <p className='text-muted-foreground mt-1 text-sm'>
          {perfil.rotulo} · visão geral do Espaço
        </p>
      </header>

      <ul aria-label='Indicadores do Espaço' className='grid grid-cols-2 gap-4 xl:grid-cols-4'>
        {indicadores.map((indicador) => (
          <li
            key={indicador.titulo}
            className='border-primary/15 rounded-2xl border bg-linear-to-br from-[rgba(14,24,43,.78)] to-[rgba(10,17,32,.62)] px-5 py-4'
          >
            <p
              className={cn(
                fonteDisplay,
                'text-[40px] leading-none font-bold text-(--cor-tipo) tabular-nums [text-shadow:0_0_24px_color-mix(in_srgb,var(--cor-tipo)_40%,transparent)]'
              )}
            >
              {indicador.valor}
            </p>
            <p className={cn(fonteDisplay, 'mt-2.5 text-[15px] font-semibold')}>
              {indicador.titulo}
            </p>
            <p className='text-muted-foreground truncate text-[12.5px]'>{indicador.legenda}</p>
          </li>
        ))}
      </ul>

      <div className='grid min-w-0 grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3'>
        <Cartao titulo='Em andamento e para hoje' icone={IconListCheck}>
          <Vazio>Nenhuma tarefa em andamento.</Vazio>
        </Cartao>

        <Cartao
          titulo='Horas por dia'
          icone={IconChartLine}
          extra={<span className='text-muted-foreground font-mono text-xs'>0h na semana</span>}
        >
          <div
            role='img'
            aria-label='Horas por dia: nenhuma hora nesta semana'
            className='mt-auto flex h-32 items-end gap-2 border-b border-white/10 pb-1'
          >
            {DIAS_DA_SEMANA.map((dia) => (
              <div key={dia} className='flex flex-1 flex-col items-center gap-1'>
                <span data-horas='0' className='h-0.5 w-full rounded-full bg-(--cor-tipo)/30' />
              </div>
            ))}
          </div>
          <div className='text-muted-foreground mt-1 flex gap-2 font-mono text-[11px]'>
            {DIAS_DA_SEMANA.map((dia) => (
              <span key={dia} className='flex-1 text-center'>
                {dia}
              </span>
            ))}
          </div>
        </Cartao>

        <Cartao titulo='Projetos' icone={IconFolder}>
          <Vazio>Nenhum projeto ainda.</Vazio>
        </Cartao>

        <Cartao titulo='Agenda' icone={IconClock}>
          <Vazio>Nenhum compromisso agendado.</Vazio>
        </Cartao>

        <Cartao titulo='Sugestões do NEO' icone={IconSparkles}>
          <ul className='flex flex-col'>
            {SUGESTOES_DO_NEO.map((sugestao) => (
              <li
                key={sugestao}
                className='flex items-start gap-3 border-b border-white/5 py-3 text-sm last:border-0'
              >
                <IconSparkles
                  size={16}
                  className='mt-0.5 flex-none text-(--cor-tipo)'
                  aria-hidden
                />
                {sugestao}
              </li>
            ))}
          </ul>
        </Cartao>

        <Cartao titulo='Hábitos' icone={IconCheck}>
          <Vazio>Os hábitos deste Espaço aparecem aqui.</Vazio>
        </Cartao>
      </div>
    </div>
  );
}

/** 0040 AC-14: id que não é de um Espaço do Usuário. */
function EspacoNaoEncontrado() {
  return (
    <div className='flex flex-1 flex-col items-center justify-center gap-3 p-6 text-center'>
      <h1 className={cn(fonteDisplay, 'text-2xl font-semibold')}>Espaço não encontrado</h1>
      <p className='text-muted-foreground text-sm'>
        Este Espaço não existe ou não pertence à sua conta.
      </p>
      <Link
        href='/dashboard/overview'
        className='text-primary text-sm underline underline-offset-4'
      >
        Ir para o Início
      </Link>
    </div>
  );
}

/** Página do Espaço: lê o Espaço do Usuário já carregado por `GET /v1/me` (design 0040). */
export function EspacoView({ id }: { id: string }) {
  const contexto = useUsuarioNeo();
  const espaco = contexto?.usuario.espacos.find((e) => e.id === id) ?? null;

  // AC-13: título "<nome do Espaço> | NEO". O nome só existe no cliente (vem de /v1/me), então a
  // página usa a tag <title> do React 19, que o Next aplica no <head>.
  return (
    <>
      <title>{espaco ? `${espaco.nome} | NEO` : 'Espaço não encontrado | NEO'}</title>
      {espaco ? <DashboardDoEspaco espaco={espaco} /> : <EspacoNaoEncontrado />}
    </>
  );
}
