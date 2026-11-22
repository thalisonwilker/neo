/**
 * Regras puras da página inicial (spec 0038). Sem React e sem Next:
 * os componentes da home consomem estas funções, e os testes as exercitam diretamente.
 */
import type { EspacoDTO, TipoEspaco } from '@/lib/api';

const DIAS_ABREVIADOS = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'] as const;
const MESES_ABREVIADOS = [
  'Jan',
  'Fev',
  'Mar',
  'Abr',
  'Mai',
  'Jun',
  'Jul',
  'Ago',
  'Set',
  'Out',
  'Nov',
  'Dez'
] as const;
const MESES = [
  'janeiro',
  'fevereiro',
  'março',
  'abril',
  'maio',
  'junho',
  'julho',
  'agosto',
  'setembro',
  'outubro',
  'novembro',
  'dezembro'
] as const;

/** AC-3: cabeçalho do calendário, semana começando no domingo. */
export const DIAS_DA_SEMANA = ['dom.', 'seg.', 'ter.', 'qua.', 'qui.', 'sex.', 'sáb.'] as const;

/** AC-1: data de hoje no formato `Dom, 22 Nov 2026`. */
export function formatarDataDeHoje(data: Date): string {
  return `${DIAS_ABREVIADOS[data.getDay()]}, ${data.getDate()} ${MESES_ABREVIADOS[data.getMonth()]} ${data.getFullYear()}`;
}

/** Mês do calendário; `mes` vai de 0 (janeiro) a 11 (dezembro). */
export interface MesDoCalendario {
  ano: number;
  mes: number;
}

export function mesDe(data: Date): MesDoCalendario {
  return { ano: data.getFullYear(), mes: data.getMonth() };
}

/** AC-3: título no formato `novembro de 2026`. */
export function tituloDoMes({ ano, mes }: MesDoCalendario): string {
  return `${MESES[mes]} de ${ano}`;
}

/** AC-4: mês anterior (-1) ou seguinte (+1), sempre a partir do 1º dia — nunca pula um mês. */
export function mesVizinho({ ano, mes }: MesDoCalendario, deslocamento: number): MesDoCalendario {
  const primeiroDia = new Date(ano, mes + deslocamento, 1);
  return mesDe(primeiroDia);
}

export interface DiaDoCalendario {
  chave: string;
  dia: number;
  doMes: boolean;
  hoje: boolean;
}

function chaveDoDia(data: Date): string {
  const mm = String(data.getMonth() + 1).padStart(2, '0');
  const dd = String(data.getDate()).padStart(2, '0');
  return `${data.getFullYear()}-${mm}-${dd}`;
}

/**
 * AC-3: grade do mês em semanas completas (domingo a sábado), com os dias dos meses
 * vizinhos marcados como fora do mês e o dia de hoje destacado.
 */
export function gradeDoMes(mesCalendario: MesDoCalendario, hoje: Date): DiaDoCalendario[][] {
  const { ano, mes } = mesCalendario;
  const primeiroDia = new Date(ano, mes, 1);
  const diasNoMes = new Date(ano, mes + 1, 0).getDate();
  const deslocamento = primeiroDia.getDay();
  const totalDeCelulas = Math.ceil((deslocamento + diasNoMes) / 7) * 7;
  const chaveDeHoje = chaveDoDia(hoje);

  const semanas: DiaDoCalendario[][] = [];
  for (let i = 0; i < totalDeCelulas; i++) {
    const data = new Date(ano, mes, 1 - deslocamento + i);
    const chave = chaveDoDia(data);
    if (i % 7 === 0) semanas.push([]);
    semanas[semanas.length - 1].push({
      chave,
      dia: data.getDate(),
      doMes: data.getMonth() === mes,
      hoje: chave === chaveDeHoje
    });
  }
  return semanas;
}

export type IconeDoTipo = 'pasta' | 'livro' | 'brilho' | 'coracao';

export interface PerfilDoTipo {
  rotulo: string;
  cor: string;
  icone: IconeDoTipo;
}

/** AC-5: rótulo, cor e ícone de cada Tipo de espaço (paleta do protótipo NEO). */
export const PERFIS_DE_TIPO: Record<TipoEspaco, PerfilDoTipo> = {
  trabalho: { rotulo: 'Trabalho', cor: '#00FFB2', icone: 'pasta' },
  estudos: { rotulo: 'Estudos', cor: '#38BDF8', icone: 'livro' },
  hobbies: { rotulo: 'Hobbies', cor: '#A78BFA', icone: 'brilho' },
  pessoal: { rotulo: 'Pessoal', cor: '#F472B6', icone: 'coracao' }
};

/** AC-5: Espaços na ordem de criação (mais antigo primeiro), sem alterar a lista original. */
export function ordenarEspacos(espacos: readonly EspacoDTO[]): EspacoDTO[] {
  return espacos.toSorted((a, b) => a.criado_em.localeCompare(b.criado_em));
}
