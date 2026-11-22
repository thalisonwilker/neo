import { enUS } from '@clerk/localizations';
import { describe, expect, it } from 'vitest';

import { localization } from './localization';

type Tree = { [key: string]: Tree | string | undefined };

/** Caminhos de textos que existem em inglês e estão vazios na localização. */
function untranslated(en: Tree, pt: Tree | undefined, path = ''): string[] {
  return Object.entries(en).flatMap(([key, value]) => {
    const translated = pt?.[key];
    if (value && typeof value === 'object') {
      return untranslated(value, translated as Tree | undefined, `${path}${key}.`);
    }
    return typeof value === 'string' && !translated ? [`${path}${key}`] : [];
  });
}

// Telas e mensagens do fluxo de entrada, cadastro, erros e menu do usuário.
const FLOW =
  /^(signIn|signUp|unstable__errors|form|socialButtons|dividerText|footerAction|backButton|userButton)/;
// Recursos que o painel não habilita: SSO empresarial, passkeys, chaves de API e organizações.
const OUT_OF_SCOPE =
  /^(signIn\.(enterpriseSSO|passkeyMfa|ssoBypass)|unstable__errors\.(api_key|insufficient_seats|sso_bypass))/;

describe('AC-13: textos do fluxo de login em português', () => {
  it('AC-13: nenhum texto do fluxo de entrada e cadastro fica em inglês', () => {
    const missing = untranslated(enUS as Tree, localization as Tree).filter(
      (path) => FLOW.test(path) && !OUT_OF_SCOPE.test(path)
    );
    expect(missing).toEqual([]);
  });

  it('AC-13: o complemento cobre o campo de senha do cadastro', () => {
    expect(localization.formFieldInputPlaceholder__signUpPassword).toBe('Crie uma senha');
  });

  it('AC-13: mantém o pacote oficial pt-BR como base', () => {
    expect(localization.locale).toBe('pt-BR');
    expect(localization.formButtonPrimary).toBe('Continuar');
  });
});
