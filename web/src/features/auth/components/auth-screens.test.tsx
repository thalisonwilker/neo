import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

// Clerk simulado: nenhuma chamada externa real.
vi.mock('@clerk/nextjs', () => ({
  SignIn: () => <div data-testid='clerk-sign-in' />,
  SignUp: () => <div data-testid='clerk-sign-up' />
}));

import { metadata as signInMetadata } from '@/app/auth/sign-in/[[...sign-in]]/page';
import { metadata as signUpMetadata } from '@/app/auth/sign-up/[[...sign-up]]/page';
import SignInViewPage from './sign-in-view';
import SignUpViewPage from './sign-up-view';

const PHRASE = 'Compreenda seus sistemas. Seja dono das suas escolhas.';

describe.each([
  ['entrada', () => <SignInViewPage redirectUrl='/dashboard/overview' />, 'clerk-sign-in'],
  ['cadastro', () => <SignUpViewPage redirectUrl='/dashboard/overview' />, 'clerk-sign-up']
])('AC-9: tela de %s sem placeholders', (_nome, view, formTestId) => {
  it('AC-9: não contém o logo nem o depoimento de exemplo do template', () => {
    const { container } = render(view());
    expect(container).not.toHaveTextContent('Logo');
    expect(container).not.toHaveTextContent('Random Dude');
    expect(container).not.toHaveTextContent('This starter template');
  });

  it('AC-9: exibe a marca NEO e a frase da visão em português', () => {
    render(view());
    expect(screen.getByText('NEO')).toBeInTheDocument();
    expect(screen.getByText(PHRASE)).toBeInTheDocument();
  });

  it('AC-9: mantém o formulário do Clerk', () => {
    render(view());
    expect(screen.getByTestId(formTestId)).toBeInTheDocument();
  });
});

describe('AC-9: títulos das páginas em português', () => {
  it('AC-9: entrada e cadastro têm título e descrição em pt-BR', () => {
    expect(signInMetadata.title).toBe('Entrar | NEO');
    expect(signUpMetadata.title).toBe('Cadastrar | NEO');
    expect(String(signInMetadata.description)).toMatch(/painel/i);
    expect(String(signUpMetadata.description)).toMatch(/painel/i);
  });
});
