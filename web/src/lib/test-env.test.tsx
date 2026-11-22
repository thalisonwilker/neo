import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { cn } from '@/lib/utils';

// Teste de fumaça do ambiente de teste do painel (spec 0036, tarefa 2).
describe('AC-14: ambiente de teste do painel', () => {
  it('AC-14: resolve o alias "@" para src/', () => {
    expect(cn('a', undefined, 'c')).toBe('a c');
  });

  it('AC-14: renderiza componentes React no jsdom com os matchers do jest-dom', () => {
    render(<p>Painel NEO</p>);
    expect(screen.getByText('Painel NEO')).toBeInTheDocument();
  });
});
