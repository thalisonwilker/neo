/**
 * Perfil de cada Tipo de espaço (spec 0040, tabela "Perfil do tipo").
 * Fonte única para o modal, o menu lateral, a página inicial e o dashboard do Espaço.
 */
import type { TipoEspaco } from '@/lib/api';

export type IconeDoTipo = 'pasta' | 'livro' | 'brilho' | 'coracao';

export interface QuartoIndicador {
  titulo: string;
  valorVazio: string;
  legenda: string;
}

export interface PerfilDoTipo {
  rotulo: string;
  cor: string;
  icone: IconeDoTipo;
  descricao: string;
  metaSugerida: number;
  quartoIndicador: QuartoIndicador;
}

/** Ordem dos cartões no modal. */
export const TIPOS_DE_ESPACO: readonly TipoEspaco[] = ['trabalho', 'estudos', 'hobbies', 'pessoal'];

export const PERFIS_DE_TIPO: Record<TipoEspaco, PerfilDoTipo> = {
  trabalho: {
    rotulo: 'Trabalho',
    cor: '#00FFB2',
    icone: 'pasta',
    descricao: 'Trabalho, carreira, clientes e outros projetos',
    metaSugerida: 30,
    quartoIndicador: { titulo: 'Deploys no mês', valorVazio: '0', legenda: 'neste mês' }
  },
  estudos: {
    rotulo: 'Estudos',
    cor: '#38BDF8',
    icone: 'livro',
    descricao: 'Faculdade, cursos, leituras, provas e cronogramas',
    metaSugerida: 10,
    quartoIndicador: { titulo: 'Sequência de estudo', valorVazio: '0 dias', legenda: 'neste mês' }
  },
  hobbies: {
    rotulo: 'Hobbies',
    cor: '#A78BFA',
    icone: 'brilho',
    descricao: 'Atividades de lazer',
    metaSugerida: 8,
    quartoIndicador: { titulo: 'Sessões na semana', valorVazio: '0', legenda: 'neste mês' }
  },
  pessoal: {
    rotulo: 'Pessoal',
    cor: '#F472B6',
    icone: 'coracao',
    descricao: 'Coisas da vida pessoal',
    metaSugerida: 8,
    quartoIndicador: { titulo: 'Contas a pagar', valorVazio: '0', legenda: 'neste mês' }
  }
};

/** Limites do formulário (iguais aos do domínio na API). */
export const MAX_NOME_ESPACO = 100;
export const MIN_META_SEMANAL = 1;
export const MAX_META_SEMANAL = 168;

/** Rota do dashboard de um Espaço. */
export const rotaDoEspaco = (id: string) => `/dashboard/espacos/${id}`;
