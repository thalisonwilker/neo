/**
 * Regras de acesso do painel (spec 0036, domínio "Painel Web (Acesso)").
 *
 * São funções puras, sem Clerk e sem Next: o proxy, o layout e a página raiz
 * consomem estas regras, e os testes as exercitam diretamente.
 */

export const SIGN_IN_PATH = '/auth/sign-in';
export const SIGN_UP_PATH = '/auth/sign-up';
export const PRIMEIRO_ACESSO_PATH = '/primeiro-acesso';
export const BOAS_VINDAS_PATH = '/boas-vindas';
export const DEFAULT_POST_LOGIN_PATH = '/dashboard/overview';

const MAX_REDIRECT_LENGTH = 2048;

const isUnder = (pathname: string, base: string): boolean =>
  pathname === base || pathname.startsWith(`${base}/`);

/**
 * 0036 AC-1 e 0037 AC-11: /dashboard, /api, /primeiro-acesso e /boas-vindas exigem sessão;
 * o restante (inclusive entrada e cadastro) é público.
 */
export function isProtectedPath(pathname: string): boolean {
  return (
    isUnder(pathname, '/dashboard') ||
    isUnder(pathname, '/api') ||
    isUnder(pathname, PRIMEIRO_ACESSO_PATH) ||
    isUnder(pathname, BOAS_VINDAS_PATH)
  );
}

/** Rotas de entrada e cadastro, inclusive as etapas do Clerk (ex.: /auth/sign-in/factor-one). */
function isAuthFlowPath(path: string): boolean {
  const pathOnly = path.split('?')[0];
  return isUnder(pathOnly, SIGN_IN_PATH) || isUnder(pathOnly, SIGN_UP_PATH);
}

/** Caracteres de controle (inclui tabulação e quebra de linha), que o navegador remove ao interpretar a URL. */
function hasControlCharacter(value: string): boolean {
  for (let i = 0; i < value.length; i++) {
    const code = value.charCodeAt(i);
    if (code < 0x20 || code === 0x7f) return true;
  }
  return false;
}

/** Reduz uma URL absoluta da MESMA origem a caminho + consulta; qualquer outra absoluta vira `null`. */
function toInternalCandidate(raw: string, origin?: string): string | null {
  if (!/^[a-z][a-z0-9+.-]*:/i.test(raw)) return raw;
  if (!origin) return null;
  try {
    const url = new URL(raw);
    if (url.origin !== new URL(origin).origin) return null;
    return `${url.pathname}${url.search}`;
  } catch {
    return null;
  }
}

/**
 * Devolve o caminho interno seguro ou `null`.
 *
 * Aceita só caminhos internos (um único "/" inicial) e descarta o fragmento. Rejeita
 * URLs externas, "//host", barra invertida, caracteres de controle, esquemas
 * (javascript:, data:), destinos longos demais e as rotas de entrada (evita laço).
 */
function toSafeInternalPath(raw: string, origin?: string): string | null {
  const candidate = toInternalCandidate(raw.split('#')[0], origin);
  if (candidate === null) return null;

  const isInternalPath =
    candidate.length > 0 &&
    candidate.length <= MAX_REDIRECT_LENGTH &&
    candidate.startsWith('/') &&
    !candidate.startsWith('//') &&
    !candidate.includes('\\') &&
    !hasControlCharacter(candidate);

  return isInternalPath && !isAuthFlowPath(candidate) ? candidate : null;
}

/** AC-3 e AC-4: destino pós-login. Em qualquer rejeição, vale o padrão `/dashboard/overview`. */
export function resolvePostLoginRedirect(raw?: string | null, origin?: string): string {
  if (!raw) return DEFAULT_POST_LOGIN_PATH;
  return toSafeInternalPath(raw, origin) ?? DEFAULT_POST_LOGIN_PATH;
}

/**
 * AC-2: URL da tela de entrada que guarda o destino pedido em `redirect_url`.
 * O destino passa pela mesma validação do pós-login; se for inválido, a URL sai sem `redirect_url`.
 */
export function buildSignInUrl(pathname: string, search = ''): string {
  const safe = toSafeInternalPath(`${pathname}${search}`);
  return safe ? `${SIGN_IN_PATH}?redirect_url=${encodeURIComponent(safe)}` : SIGN_IN_PATH;
}

/**
 * AC-3: origem do pedido (protocolo + host), usada para reconhecer uma URL absoluta da mesma
 * origem em `redirect_url`. Considera os cabeçalhos de um proxy reverso (`x-forwarded-*`).
 * Sem host, a origem é desconhecida e qualquer URL absoluta é rejeitada.
 */
export function originFromHeaders(headers: {
  get(name: string): string | null;
}): string | undefined {
  const host = headers.get('x-forwarded-host')?.split(',')[0].trim() || headers.get('host');
  if (!host) return undefined;

  const forwarded = headers.get('x-forwarded-proto')?.split(',')[0].trim();
  const isLocal = /^(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$/.test(host);
  const protocol =
    forwarded === 'http' || forwarded === 'https' ? forwarded : isLocal ? 'http' : 'https';
  return `${protocol}://${host}`;
}

/** AC-5: para onde a raiz `/` (e o índice `/dashboard`) leva o visitante, conforme a sessão. */
export function resolveRootDestination(isSignedIn: boolean): string {
  return isSignedIn ? DEFAULT_POST_LOGIN_PATH : SIGN_IN_PATH;
}
