'use client';

import {
  IconBook,
  IconBox,
  IconChevronLeft,
  IconChevronRight,
  IconClock,
  IconFolder,
  IconHeart,
  IconListCheck,
  IconSparkles
} from '@tabler/icons-react';
import { useState } from 'react';
import type { ComponentType, ReactNode } from 'react';

import { useUsuarioNeo } from '@/features/onboarding/components/neo-access-guard';
import type { EspacoDTO } from '@/lib/api';
import { cn } from '@/lib/utils';
import {
  DIAS_DA_SEMANA,
  PERFIS_DE_TIPO,
  formatarDataDeHoje,
  gradeDoMes,
  mesDe,
  mesVizinho,
  ordenarEspacos,
  tituloDoMes,
  type IconeDoTipo
} from '../home-rules';

const ICONES_DO_TIPO: Record<
  IconeDoTipo,
  ComponentType<{ size?: number; 'aria-hidden'?: boolean }>
> = {
  pasta: IconFolder,
  livro: IconBook,
  brilho: IconSparkles,
  coracao: IconHeart
};

const CONTADORES = ['Hoje', 'Esta semana', 'Este mês', 'Este ano'] as const;

const fonteDisplay = 'font-[family-name:var(--font-display)]';

function Cartao({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <section
      className={cn(
        'border-primary/15 hover:border-primary/30 relative min-w-0 rounded-2xl border bg-linear-to-br from-[rgba(14,24,43,.78)] to-[rgba(10,17,32,.62)] p-5 shadow-[0_14px_40px_rgba(0,0,0,.35)] backdrop-blur-xl transition-colors',
        className
      )}
    >
      {children}
    </section>
  );
}

/** AC-1: saudação com o nome de exibição e a data de hoje. */
function Saudacao({ nome, hoje }: { nome: string | null; hoje: Date }) {
  return (
    <header className='flex flex-wrap items-end justify-between gap-x-5 gap-y-2'>
      <div className='min-w-0'>
        <h1 className={cn(fonteDisplay, 'text-[28px] leading-tight font-semibold tracking-tight')}>
          {nome ? (
            <>
              Olá,{' '}
              <em className='text-primary not-italic [text-shadow:0_0_22px_rgba(0,255,178,.35)]'>
                {nome}
              </em>
            </>
          ) : (
            'Olá'
          )}
        </h1>
        <p className='text-muted-foreground mt-1 text-sm'>
          Sua agenda com todos os Espaços. Acesse um deles ou crie um novo.
        </p>
      </div>
      <p className='text-muted-foreground flex items-center gap-2 font-mono text-[12.5px]'>
        <IconClock size={15} aria-hidden />
        <time dateTime={hoje.toISOString().slice(0, 10)}>{formatarDataDeHoje(hoje)}</time>
      </p>
    </header>
  );
}

/** AC-2: quatro contadores de tarefas, vazios enquanto não há tarefas. */
function Contadores() {
  return (
    <ul aria-label='Tarefas por período' className='grid grid-cols-2 gap-4 xl:grid-cols-4'>
      {CONTADORES.map((periodo) => (
        <li key={periodo}>
          <Cartao className='px-5 py-4'>
            <p
              className={cn(
                fonteDisplay,
                'text-primary text-[44px] leading-none font-bold tabular-nums [text-shadow:0_0_24px_rgba(0,255,178,.4)]'
              )}
            >
              0
            </p>
            <p className={cn(fonteDisplay, 'mt-2.5 text-[15px] font-semibold')}>{periodo}</p>
            <p className='text-muted-foreground text-[12.5px]'>tarefas</p>
          </Cartao>
        </li>
      ))}
    </ul>
  );
}

const botaoCalendario =
  'border-primary/15 text-foreground hover:border-primary/40 hover:text-primary focus-visible:ring-ring inline-flex h-9 items-center justify-center rounded-[10px] border bg-[rgba(10,17,32,.8)] px-3 text-sm transition-colors focus-visible:ring-2 focus-visible:outline-none';

/** AC-3 e AC-4: calendário do mês com navegação. */
function CalendarioDoMes({ hoje }: { hoje: Date }) {
  const [mesExibido, setMesExibido] = useState(() => mesDe(hoje));
  const semanas = gradeDoMes(mesExibido, hoje);
  const titulo = tituloDoMes(mesExibido);

  return (
    <Cartao className='flex flex-col'>
      <div className='mb-4 flex flex-wrap items-center justify-between gap-3'>
        <h2 className={cn(fonteDisplay, 'text-2xl font-semibold')} aria-live='polite'>
          {titulo}
        </h2>
        <div className='flex items-center gap-2'>
          <button
            type='button'
            className={cn(botaoCalendario, 'w-9 px-0')}
            aria-label='Mês anterior'
            onClick={() => setMesExibido((m) => mesVizinho(m, -1))}
          >
            <IconChevronLeft size={16} aria-hidden />
          </button>
          <button
            type='button'
            className={botaoCalendario}
            onClick={() => setMesExibido(mesDe(hoje))}
          >
            Hoje
          </button>
          <button
            type='button'
            className={cn(botaoCalendario, 'w-9 px-0')}
            aria-label='Próximo mês'
            onClick={() => setMesExibido((m) => mesVizinho(m, 1))}
          >
            <IconChevronRight size={16} aria-hidden />
          </button>
        </div>
      </div>

      <table className='w-full table-fixed border-collapse' aria-label={`Calendário de ${titulo}`}>
        <thead>
          <tr>
            {DIAS_DA_SEMANA.map((dia) => (
              <th
                key={dia}
                scope='col'
                className='text-muted-foreground border-border/60 border-b pb-2 text-right text-xs font-normal sm:text-sm'
              >
                {dia}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {semanas.map((semana) => (
            <tr key={semana[0].chave}>
              {semana.map((dia) => (
                <td
                  key={dia.chave}
                  data-hoje={dia.hoje || undefined}
                  data-fora-do-mes={!dia.doMes || undefined}
                  className='border-border/60 h-14 border-b border-l p-1.5 align-top first:border-l-0 sm:h-24'
                >
                  <span
                    aria-current={dia.hoje ? 'date' : undefined}
                    className={cn(
                      'ml-auto grid h-6 min-w-6 w-fit place-items-center rounded-full px-1.5 text-xs sm:text-sm',
                      dia.doMes ? 'text-slate-300' : 'text-muted-foreground/50',
                      dia.hoje &&
                        'bg-primary text-primary-foreground font-semibold shadow-[0_0_14px_rgba(0,255,178,.55)]'
                    )}
                  >
                    {dia.dia}
                  </span>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </Cartao>
  );
}

/** AC-5: Espaços reais do Usuário, com cor e ícone do Tipo de espaço. */
function CartaoDeEspacos({ espacos }: { espacos: readonly EspacoDTO[] }) {
  const ordenados = ordenarEspacos(espacos);
  return (
    <Cartao>
      <div className='mb-3 flex items-center gap-3'>
        <IconBox size={20} className='text-primary' aria-hidden />
        <h2 className={cn(fonteDisplay, 'text-base font-semibold')}>Espaços</h2>
      </div>
      {ordenados.length === 0 ? (
        <p className='text-muted-foreground text-[13px]'>Nenhum Espaço ainda.</p>
      ) : (
        <ul className='flex max-h-64 flex-col overflow-y-auto'>
          {ordenados.map((espaco) => {
            const perfil = PERFIS_DE_TIPO[espaco.tipo];
            const Icone = ICONES_DO_TIPO[perfil.icone];
            return (
              <li
                key={espaco.id}
                data-tipo={espaco.tipo}
                className='flex items-center gap-3 rounded-xl px-1 py-2.5'
              >
                <span
                  className='grid size-10 flex-none place-items-center rounded-xl border'
                  style={{ color: perfil.cor, borderColor: `${perfil.cor}55` }}
                >
                  <Icone size={18} aria-hidden />
                </span>
                <div className='min-w-0'>
                  <p className='truncate font-medium' title={espaco.nome}>
                    {espaco.nome}
                  </p>
                  <p className='text-muted-foreground truncate text-[13px]'>
                    {perfil.rotulo} · sem tarefas ainda
                  </p>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </Cartao>
  );
}

/** AC-6: próximas tarefas, vazias enquanto não há tarefas. */
function ProximasTarefas() {
  return (
    <Cartao className='flex-1'>
      <div className='mb-3 flex items-center gap-3'>
        <IconListCheck size={20} className='text-primary' aria-hidden />
        <h2 className={cn(fonteDisplay, 'text-base font-semibold')}>Próximas tarefas</h2>
      </div>
      <p className='text-muted-foreground text-[13px]'>
        Nenhuma tarefa ainda. Crie a primeira para vê-la no calendário.
      </p>
    </Cartao>
  );
}

/** Página inicial do painel (spec 0038). `hoje` é injetável para os testes. */
export function HomeView({ hoje: hojeInjetado }: { hoje?: Date }) {
  const [hoje] = useState(() => hojeInjetado ?? new Date());
  const contexto = useUsuarioNeo();
  const usuario = contexto?.usuario;

  return (
    <div className='flex min-w-0 flex-1 flex-col gap-5 p-4 md:gap-6 md:p-6'>
      <Saudacao nome={usuario?.nome_exibicao ?? null} hoje={hoje} />
      <Contadores />
      <div className='grid min-w-0 grid-cols-1 gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(320px,400px)]'>
        <CalendarioDoMes hoje={hoje} />
        <div className='flex min-w-0 flex-col gap-5'>
          <CartaoDeEspacos espacos={usuario?.espacos ?? []} />
          <ProximasTarefas />
        </div>
      </div>
    </div>
  );
}
