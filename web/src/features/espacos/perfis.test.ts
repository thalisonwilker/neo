import { describe, expect, it } from 'vitest';

import {
  MAX_META_SEMANAL,
  MAX_NOME_ESPACO,
  MIN_META_SEMANAL,
  PERFIS_DE_TIPO,
  TIPOS_DE_ESPACO,
  rotaDoEspaco
} from './perfis';

describe('0040 AC-8 e AC-13: perfil do tipo (tabela da spec)', () => {
  it.each([
    [
      'trabalho',
      'Trabalho',
      '#00FFB2',
      'pasta',
      'Trabalho, carreira, clientes e outros projetos',
      30,
      ['Deploys no mês', '0', 'neste mês']
    ],
    [
      'estudos',
      'Estudos',
      '#38BDF8',
      'livro',
      'Faculdade, cursos, leituras, provas e cronogramas',
      10,
      ['Sequência de estudo', '0 dias', 'neste mês']
    ],
    [
      'hobbies',
      'Hobbies',
      '#A78BFA',
      'brilho',
      'Atividades de lazer',
      8,
      ['Sessões na semana', '0', 'neste mês']
    ],
    [
      'pessoal',
      'Pessoal',
      '#F472B6',
      'coracao',
      'Coisas da vida pessoal',
      8,
      ['Contas a pagar', '0', 'neste mês']
    ]
  ] as const)('%s', (tipo, rotulo, cor, icone, descricao, meta, [titulo, valorVazio, legenda]) => {
    expect(PERFIS_DE_TIPO[tipo]).toEqual({
      rotulo,
      cor,
      icone,
      descricao,
      metaSugerida: meta,
      quartoIndicador: { titulo, valorVazio, legenda }
    });
  });

  it('os cartões do modal seguem a ordem Trabalho, Estudos, Hobbies, Pessoal', () => {
    expect(TIPOS_DE_ESPACO).toEqual(['trabalho', 'estudos', 'hobbies', 'pessoal']);
  });

  it('os limites do formulário batem com os da API', () => {
    expect([MAX_NOME_ESPACO, MIN_META_SEMANAL, MAX_META_SEMANAL]).toEqual([100, 1, 168]);
    expect(rotaDoEspaco('abc')).toBe('/dashboard/espacos/abc');
  });
});
