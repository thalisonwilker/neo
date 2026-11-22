import { ptBR } from '@clerk/localizations';

/**
 * Localização do Clerk para o painel: o pacote oficial `ptBR` mais as traduções que ele ainda
 * não traz para o fluxo de entrada e cadastro (pacote 4.26.x deixa esses textos em inglês).
 * Fica de fora o que o painel não habilita: SSO empresarial, passkeys, chaves de API e organizações.
 */
export const localization: typeof ptBR = {
  ...ptBR,
  formFieldInputPlaceholder__signUpPassword: 'Crie uma senha',
  signIn: {
    ...ptBR.signIn,
    emailLink: {
      ...ptBR.signIn?.emailLink,
      verifiedTransferable: {
        title: 'E-mail verificado',
        subtitle: 'Volte à aba original para continuar'
      }
    },
    protectCheck: {
      loading: 'Carregando…',
      retryButton: 'Tentar novamente',
      subtitle: 'Aguarde enquanto verificamos sua solicitação.',
      title: 'Verificando sua solicitação'
    }
  },
  signUp: {
    ...ptBR.signUp,
    protectCheck: {
      loading: 'Carregando…',
      retryButton: 'Tentar novamente',
      subtitle: 'Aguarde enquanto verificamos sua solicitação.',
      title: 'Verificando sua solicitação'
    }
  },
  unstable__errors: {
    ...ptBR.unstable__errors,
    action_blocked:
      'Não foi possível concluir esta ação. Tente novamente mais tarde ou fale com o suporte se o problema persistir.',
    external_account_not_found:
      'Conta não encontrada. Cadastre-se ou tente entrar com outra conta.',
    form_password_matches_identifier:
      'A senha não pode ser igual ao seu e-mail, telefone ou nome de usuário. Por segurança, use uma senha diferente.',
    oauth_access_denied: 'Você não concedeu acesso à sua conta.',
    protect_check_execution_failed: 'A verificação não foi concluída. Tente novamente.',
    protect_check_invalid_script:
      'Não foi possível carregar a verificação. Fale com o suporte se o problema persistir.',
    protect_check_invalid_sdk_url: 'Não foi possível iniciar a verificação. Fale com o suporte.',
    protect_check_required:
      'Este acesso exige uma etapa extra de verificação que não pode ser exibida aqui. Tente novamente ou use outra forma de entrar.',
    protect_check_script_load_failed:
      'Não foi possível carregar a verificação. Pode ser um problema de rede ou uma política de segurança que bloqueia o script. Tente novamente ou fale com o suporte.',
    protect_check_timed_out: 'A verificação não foi concluída a tempo. Tente novamente.',
    protect_check_unsupported_environment:
      'A verificação não é compatível com este ambiente. Continue em um navegador padrão ou fale com o suporte.',
    signup_rate_limit_exceeded: 'Muitas solicitações. Tente novamente em instantes.',
    something_went_wrong: 'Algo deu errado. Tente novamente.',
    ticket_expired_code: 'Este link expirou. Comece de novo ou peça um novo link.',
    ticket_invalid_code:
      'Este link não é mais válido ou já foi usado. Comece de novo ou peça um novo link.',
    too_many_requests: 'Muitas solicitações. Tente novamente em instantes.',
    too_many_unverified_identifications:
      'Há verificações pendentes demais nesta conta. Remova um e-mail, telefone ou carteira não verificado que você não usa mais, ou aguarde alguns minutos, e tente de novo.'
  }
};
