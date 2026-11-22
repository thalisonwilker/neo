import { BOAS_VINDAS_PATH, PRIMEIRO_ACESSO_PATH } from '@/features/auth/access';
import type { ResultadoMe } from '@/lib/api';

export const DASHBOARD_ROOT_PATH = '/dashboard';

export type AcaoDeRota =
  | { tipo: 'permitir' }
  | { tipo: 'redirecionar'; destino: string }
  | { tipo: 'encerrar_sessao' }
  | { tipo: 'acesso_nao_liberado' }
  | { tipo: 'api_indisponivel' };

const isUnder = (pathname: string, base: string): boolean =>
  pathname === base || pathname.startsWith(`${base}/`);

/**
 * Matriz de decisão pura do direcionamento pós-login (spec 0037, AC-11, AC-13, AC-14, AC-15).
 */
export function resolverAcaoDeRota(params: {
  resultadoMe: ResultadoMe;
  pathname: string;
  boasVindasPendentes: boolean;
}): AcaoDeRota {
  const { resultadoMe, pathname, boasVindasPendentes } = params;

  if (!resultadoMe.ok) {
    if (resultadoMe.status === 401) return { tipo: 'encerrar_sessao' };
    if (resultadoMe.status === 403) return { tipo: 'acesso_nao_liberado' };
    return { tipo: 'api_indisponivel' };
  }

  const concluido = resultadoMe.usuario.primeiro_acesso_concluido;

  if (!concluido) {
    return isUnder(pathname, PRIMEIRO_ACESSO_PATH)
      ? { tipo: 'permitir' }
      : { tipo: 'redirecionar', destino: PRIMEIRO_ACESSO_PATH };
  }

  if (isUnder(pathname, BOAS_VINDAS_PATH)) {
    return boasVindasPendentes
      ? { tipo: 'permitir' }
      : { tipo: 'redirecionar', destino: DASHBOARD_ROOT_PATH };
  }

  if (isUnder(pathname, PRIMEIRO_ACESSO_PATH)) {
    return { tipo: 'redirecionar', destino: DASHBOARD_ROOT_PATH };
  }

  return { tipo: 'permitir' };
}
