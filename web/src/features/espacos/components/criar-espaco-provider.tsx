'use client';

import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import type { ReactNode } from 'react';

import { CriarEspacoModal } from './criar-espaco-modal';

interface CriarEspacoContextValue {
  abrir: () => void;
}

const CriarEspacoContext = createContext<CriarEspacoContextValue | null>(null);

/** 0040 AC-7: quem estiver dentro do provedor pode abrir o modal "Criar Espaço". */
export function useCriarEspaco(): CriarEspacoContextValue | null {
  return useContext(CriarEspacoContext);
}

export function CriarEspacoProvider({ children }: { children: ReactNode }) {
  const [aberto, setAberto] = useState(false);
  // Cada abertura monta um formulário novo (AC-12: reabrir volta ao estado inicial).
  const [abertura, setAbertura] = useState(0);

  const abrir = useCallback(() => {
    setAbertura((n) => n + 1);
    setAberto(true);
  }, []);
  const fechar = useCallback(() => setAberto(false), []);
  const valor = useMemo(() => ({ abrir }), [abrir]);

  return (
    <CriarEspacoContext.Provider value={valor}>
      {children}
      <CriarEspacoModal key={abertura} aberto={aberto} aoFechar={fechar} />
    </CriarEspacoContext.Provider>
  );
}
