import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';

import { DEFAULT_POST_LOGIN_PATH, SIGN_IN_PATH, SIGN_UP_PATH } from './access';

// Os testes rodam a partir de web/ (`npm run test`), então o diretório atual é a raiz do painel.
const fromWebRoot = (relative: string) => resolve(process.cwd(), relative);

/** Lê `CHAVE=valor` (com ou sem aspas e comentário no fim da linha) de um arquivo de ambiente. */
function parseEnvFile(path: string): Record<string, string> {
  const values: Record<string, string> = {};
  for (const line of readFileSync(path, 'utf8').split('\n')) {
    const match = line.match(/^([A-Z0-9_]+)\s*=\s*("([^"]*)"|[^#\s]*)/);
    if (match) values[match[1]] = match[3] ?? match[2];
  }
  return values;
}

describe('AC-7: configuração coerente e rotas únicas', () => {
  const env = parseEnvFile(fromWebRoot('env.example.txt'));

  it('AC-7: env.example.txt aponta a entrada e o cadastro para /auth/...', () => {
    expect(env.NEXT_PUBLIC_CLERK_SIGN_IN_URL).toBe(SIGN_IN_PATH);
    expect(env.NEXT_PUBLIC_CLERK_SIGN_UP_URL).toBe(SIGN_UP_PATH);
  });

  it('AC-7: env.example.txt leva a /dashboard/overview depois de entrar ou cadastrar', () => {
    expect(env.NEXT_PUBLIC_CLERK_SIGN_IN_FALLBACK_REDIRECT_URL).toBe(DEFAULT_POST_LOGIN_PATH);
    expect(env.NEXT_PUBLIC_CLERK_SIGN_UP_FALLBACK_REDIRECT_URL).toBe(DEFAULT_POST_LOGIN_PATH);
  });

  it('AC-7: as rotas oficiais /auth/sign-in e /auth/sign-up existem', () => {
    expect(existsSync(fromWebRoot('src/app/auth/sign-in'))).toBe(true);
    expect(existsSync(fromWebRoot('src/app/auth/sign-up'))).toBe(true);
  });

  it('AC-7: as rotas /sign-in e /sign-up não existem', () => {
    expect(existsSync(fromWebRoot('src/app/sign-in'))).toBe(false);
    expect(existsSync(fromWebRoot('src/app/sign-up'))).toBe(false);
  });
});
