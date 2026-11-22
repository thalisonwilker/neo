import { headers } from 'next/headers';

import { originFromHeaders, resolvePostLoginRedirect } from './access';

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

/**
 * AC-3 e AC-4: destino pós-login de uma página de entrada ou cadastro, a partir da consulta
 * `redirect_url` (repetida: vale a primeira) e da origem do pedido.
 */
export async function getPostLoginRedirect(searchParams: SearchParams): Promise<string> {
  const params = await searchParams;
  const raw = Array.isArray(params.redirect_url) ? params.redirect_url[0] : params.redirect_url;
  return resolvePostLoginRedirect(raw, originFromHeaders(await headers()));
}
