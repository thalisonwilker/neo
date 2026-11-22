import { describe, expect, it } from 'vitest';

import {
  PERFIS_DE_TIPO,
  formatarDataDeHoje,
  gradeDoMes,
  mesVizinho,
  ordenarEspacos,
  tituloDoMes
} from './home-rules';

describe('0038 AC-1: data de hoje', () => {
  it('formata como "Dom, 22 Nov 2026"', () => {
    expect(formatarDataDeHoje(new Date(2026, 10, 22))).toBe('Dom, 22 Nov 2026');
  });

  it('usa o acento de sábado e o mês de março', () => {
    expect(formatarDataDeHoje(new Date(2026, 2, 7))).toBe('Sáb, 7 Mar 2026');
  });
});

describe('0038 AC-3: grade do mês', () => {
  it('novembro de 2026 começa no domingo e tem 5 semanas', () => {
    const semanas = gradeDoMes({ ano: 2026, mes: 10 }, new Date(2026, 10, 22));
    expect(tituloDoMes({ ano: 2026, mes: 10 })).toBe('novembro de 2026');
    expect(semanas).toHaveLength(5);
    expect(semanas[0][0]).toMatchObject({ dia: 1, doMes: true });
    const ultima = semanas[4];
    expect(ultima.map((d) => d.dia)).toEqual([29, 30, 1, 2, 3, 4, 5]);
    expect(ultima.slice(2).every((d) => !d.doMes)).toBe(true);
  });

  it('destaca só o dia de hoje', () => {
    const dias = gradeDoMes({ ano: 2026, mes: 10 }, new Date(2026, 10, 22)).flat();
    expect(dias.filter((d) => d.hoje).map((d) => d.chave)).toEqual(['2026-11-22']);
  });

  it('fevereiro de 2026 (28 dias, começa no domingo) ocupa 4 semanas exatas', () => {
    const semanas = gradeDoMes({ ano: 2026, mes: 1 }, new Date(2026, 10, 22));
    expect(semanas).toHaveLength(4);
    expect(semanas.flat().every((d) => d.doMes)).toBe(true);
  });

  it('agosto de 2026 começa no sábado e completa a semana com julho', () => {
    const semanas = gradeDoMes({ ano: 2026, mes: 7 }, new Date(2026, 10, 22));
    expect(semanas[0].slice(0, 6).every((d) => !d.doMes)).toBe(true);
    expect(semanas[0][6]).toMatchObject({ dia: 1, doMes: true });
    expect(semanas).toHaveLength(6);
  });

  it('não destaca hoje quando o mês exibido é outro', () => {
    const dias = gradeDoMes({ ano: 2026, mes: 11 }, new Date(2026, 10, 22)).flat();
    expect(dias.some((d) => d.hoje)).toBe(false);
  });
});

describe('0038 AC-4: navegação de mês', () => {
  it('avança e volta um mês, atravessando o ano', () => {
    expect(mesVizinho({ ano: 2026, mes: 11 }, 1)).toEqual({ ano: 2027, mes: 0 });
    expect(mesVizinho({ ano: 2026, mes: 0 }, -1)).toEqual({ ano: 2025, mes: 11 });
  });

  it('de janeiro vai para fevereiro, sem pular para março', () => {
    expect(mesVizinho({ ano: 2026, mes: 0 }, 1)).toEqual({ ano: 2026, mes: 1 });
  });
});

describe('0038 AC-5: perfil e ordem dos Espaços', () => {
  it('cada Tipo de espaço tem rótulo, cor e ícone da tabela da spec', () => {
    expect(PERFIS_DE_TIPO).toEqual({
      trabalho: { rotulo: 'Trabalho', cor: '#00FFB2', icone: 'pasta' },
      estudos: { rotulo: 'Estudos', cor: '#38BDF8', icone: 'livro' },
      hobbies: { rotulo: 'Hobbies', cor: '#A78BFA', icone: 'brilho' },
      pessoal: { rotulo: 'Pessoal', cor: '#F472B6', icone: 'coracao' }
    });
  });

  it('ordena por data de criação sem mudar a lista original', () => {
    const original = [
      { id: 'b', nome: 'Faculdade', tipo: 'estudos' as const, criado_em: '2026-11-22T13:00:00Z' },
      { id: 'a', nome: 'Neo', tipo: 'trabalho' as const, criado_em: '2026-11-22T12:00:00Z' }
    ];
    expect(ordenarEspacos(original).map((e) => e.id)).toEqual(['a', 'b']);
    expect(original[0].id).toBe('b');
  });
});
