export type TipoEspaco = 'trabalho' | 'estudos' | 'hobbies' | 'pessoal';

export interface EspacoDTO {
  id: string;
  nome: string;
  tipo: TipoEspaco;
  criado_em: string;
}

export interface UsuarioDTO {
  id: string;
  email: string;
  nome_exibicao: string | null;
  primeiro_acesso_concluido: boolean;
  espacos: EspacoDTO[];
}

export interface ErroApiDTO {
  erro: string;
  mensagem: string;
  campo?: string;
}

export type ResultadoMe =
  | { ok: true; status: 200; usuario: UsuarioDTO }
  | { ok: false; status: 401; erro: ErroApiDTO }
  | { ok: false; status: 403; erro: ErroApiDTO }
  | { ok: false; status: 500 | 503; erro: ErroApiDTO };

export type ResultadoPrimeiroAcesso =
  | { ok: true; status: 201; usuario: UsuarioDTO }
  | { ok: false; status: 401 | 403 | 409 | 422 | 500 | 503; erro: ErroApiDTO };

export interface PrimeiroAcessoPayload {
  nome_exibicao: string;
  espaco: {
    nome: string;
    tipo: TipoEspaco;
  };
}

const DEFAULT_API_URL = 'http://localhost:8000';
const ERRO_INDISPONIVEL: ErroApiDTO = {
  erro: 'api_indisponivel',
  mensagem: 'Não foi possível falar com o Neo agora'
};

export function getNeoApiBaseUrl(): string {
  const configured = process.env.NEXT_PUBLIC_NEO_API_URL?.trim();
  const base = configured && configured.length > 0 ? configured : DEFAULT_API_URL;
  return base.replace(/\/+$/, '');
}

async function parseErroJson(res: Response): Promise<ErroApiDTO> {
  try {
    const data = (await res.json()) as Partial<ErroApiDTO>;
    if (typeof data.erro === 'string' && typeof data.mensagem === 'string') {
      return {
        erro: data.erro,
        mensagem: data.mensagem,
        ...(typeof data.campo === 'string' ? { campo: data.campo } : {})
      };
    }
  } catch {
    // Corpo nao JSON cai no erro padrao de indisponibilidade/status.
  }
  return res.status === 401
    ? { erro: 'token_invalido', mensagem: 'Sessão inválida ou expirada.' }
    : ERRO_INDISPONIVEL;
}

export async function fetchMe(
  token: string | null,
  fetchImpl: typeof fetch = fetch
): Promise<ResultadoMe> {
  if (!token) {
    return {
      ok: false,
      status: 401,
      erro: { erro: 'token_invalido', mensagem: 'Sessão inválida ou expirada.' }
    };
  }

  let res: Response;
  try {
    res = await fetchImpl(`${getNeoApiBaseUrl()}/v1/me`, {
      method: 'GET',
      headers: { Authorization: `Bearer ${token}` },
      cache: 'no-store'
    });
  } catch {
    return { ok: false, status: 503, erro: ERRO_INDISPONIVEL };
  }

  if (res.status === 200) {
    const usuario = (await res.json()) as UsuarioDTO;
    return { ok: true, status: 200, usuario };
  }

  const erro = await parseErroJson(res);
  if (res.status === 401) return { ok: false, status: 401, erro };
  if (res.status === 403) return { ok: false, status: 403, erro };
  return { ok: false, status: res.status === 500 ? 500 : 503, erro };
}

export async function submitPrimeiroAcesso(
  token: string | null,
  payload: PrimeiroAcessoPayload,
  fetchImpl: typeof fetch = fetch
): Promise<ResultadoPrimeiroAcesso> {
  if (!token) {
    return {
      ok: false,
      status: 401,
      erro: { erro: 'token_invalido', mensagem: 'Sessão inválida ou expirada.' }
    };
  }

  let res: Response;
  try {
    res = await fetchImpl(`${getNeoApiBaseUrl()}/v1/primeiro-acesso`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
  } catch {
    return { ok: false, status: 503, erro: ERRO_INDISPONIVEL };
  }

  if (res.status === 201) {
    const usuario = (await res.json()) as UsuarioDTO;
    return { ok: true, status: 201, usuario };
  }

  const erro = await parseErroJson(res);
  if (
    res.status === 401 ||
    res.status === 403 ||
    res.status === 409 ||
    res.status === 422 ||
    res.status === 500 ||
    res.status === 503
  ) {
    return { ok: false, status: res.status, erro };
  }
  return { ok: false, status: 503, erro };
}
