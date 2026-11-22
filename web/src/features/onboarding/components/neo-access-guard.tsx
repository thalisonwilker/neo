'use client';

import { useAuth } from '@clerk/nextjs';
import { usePathname, useRouter } from 'next/navigation';
import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import type { ReactNode } from 'react';

import { useSignOut } from '@/features/auth/use-sign-out';
import { resolverAcaoDeRota } from '@/features/onboarding/routing';
import { lerBoasVindasPendentes } from '@/features/onboarding/welcome-state';
import { fetchMe, type ResultadoMe, type UsuarioDTO } from '@/lib/api';
import { AcessoNaoLiberadoView } from './acesso-nao-liberado-view';
import { ApiIndisponivelView } from './api-indisponivel-view';

interface UsuarioNeoContextValue {
  usuario: UsuarioDTO;
  recarregar: () => void;
}

const UsuarioNeoContext = createContext<UsuarioNeoContextValue | null>(null);

export function useUsuarioNeo(): UsuarioNeoContextValue | null {
  return useContext(UsuarioNeoContext);
}

type EstadoGuard = { carregando: true } | { carregando: false; resultadoMe: ResultadoMe };

/**
 * Guarda client-side das rotas protegidas (AC-11, AC-14, AC-15):
 * consulta GET /v1/me e só renderiza {children} quando o acesso é permitido.
 */
export function NeoAccessGuard({ children }: { children: ReactNode }) {
  const { isLoaded, getToken } = useAuth();
  const pathname = usePathname() ?? '/';
  const router = useRouter();
  const signOut = useSignOut();

  const getTokenRef = useRef(getToken);
  const routerRef = useRef(router);
  const signOutRef = useRef(signOut);
  const montadoRef = useRef(true);
  useEffect(() => {
    getTokenRef.current = getToken;
    routerRef.current = router;
    signOutRef.current = signOut;
  });

  useEffect(() => {
    montadoRef.current = true;
    return () => {
      montadoRef.current = false;
    };
  }, []);

  const [estado, setEstado] = useState<EstadoGuard>({ carregando: true });

  const executarConsulta = useCallback(async () => {
    const token = await getTokenRef.current();
    return fetchMe(token);
  }, []);

  const recarregar = useCallback(() => {
    setEstado({ carregando: true });
    void executarConsulta().then((resultadoMe) => {
      if (montadoRef.current) {
        setEstado({ carregando: false, resultadoMe });
      }
    });
  }, [executarConsulta]);

  useEffect(() => {
    if (!isLoaded) return;
    let ativo = true;

    void executarConsulta().then((resultadoMe) => {
      if (ativo) {
        setEstado({ carregando: false, resultadoMe });
      }
    });

    return () => {
      ativo = false;
    };
  }, [isLoaded, executarConsulta]);

  const acao = estado.carregando
    ? null
    : resolverAcaoDeRota({
        resultadoMe: estado.resultadoMe,
        pathname,
        boasVindasPendentes: lerBoasVindasPendentes() !== null
      });

  const tipoAcao = acao?.tipo ?? null;
  const destinoAcao = acao?.tipo === 'redirecionar' ? acao.destino : null;

  useEffect(() => {
    if (tipoAcao === 'redirecionar' && destinoAcao) {
      routerRef.current.replace(destinoAcao);
    } else if (tipoAcao === 'encerrar_sessao') {
      void signOutRef.current();
    }
  }, [tipoAcao, destinoAcao]);

  if (estado.carregando || !acao) {
    return (
      <div
        role='status'
        aria-live='polite'
        className='text-muted-foreground flex min-h-screen items-center justify-center text-sm'
      >
        Verificando acesso ao Neo…
      </div>
    );
  }

  if (acao.tipo === 'acesso_nao_liberado') {
    return <AcessoNaoLiberadoView />;
  }

  if (acao.tipo === 'api_indisponivel') {
    return <ApiIndisponivelView onRetry={recarregar} />;
  }

  if (acao.tipo !== 'permitir' || !estado.resultadoMe.ok) {
    return (
      <div
        role='status'
        aria-live='polite'
        className='text-muted-foreground flex min-h-screen items-center justify-center text-sm'
      >
        Redirecionando…
      </div>
    );
  }

  return (
    <UsuarioNeoContext.Provider value={{ usuario: estado.resultadoMe.usuario, recarregar }}>
      {children}
    </UsuarioNeoContext.Provider>
  );
}
