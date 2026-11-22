export interface DadosBoasVindas {
  nomeExibicao: string;
  nomeEspaco: string;
}

let pendenteNestaVisita: DadosBoasVindas | null = null;

/** Marca em memória da visita atual que o Primeiro acesso acabou de ser concluído (AC-13). */
export function marcarBoasVindasPendentes(dados: DadosBoasVindas): void {
  pendenteNestaVisita = dados;
}

export function lerBoasVindasPendentes(): DadosBoasVindas | null {
  return pendenteNestaVisita;
}

export function limparBoasVindasPendentes(): void {
  pendenteNestaVisita = null;
}
