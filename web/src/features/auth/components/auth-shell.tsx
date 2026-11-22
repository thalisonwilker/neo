import { cn } from '@/lib/utils';
import type { ReactNode } from 'react';
import { InteractiveGridPattern } from './interactive-grid';

/** Frase da visão do produto (docs/product/vision.md). */
export const BRAND_PHRASE = 'Compreenda seus sistemas. Seja dono das suas escolhas.';

/** Moldura das telas de entrada e cadastro: painel da marca à esquerda e o formulário do Clerk à direita. */
export function AuthShell({ children }: { children: ReactNode }) {
  return (
    <div className='relative flex min-h-screen flex-col items-center justify-center overflow-hidden md:grid lg:max-w-none lg:grid-cols-2 lg:px-0'>
      <div className='relative hidden h-full flex-col p-10 lg:flex dark:border-r'>
        <div className='bg-sidebar absolute inset-0' />
        <div className='text-sidebar-foreground relative z-20 flex items-center gap-3'>
          <span
            aria-hidden='true'
            className='bg-primary text-primary-foreground grid size-9 place-items-center rounded-lg text-lg font-bold'
          >
            N
          </span>
          <span className='text-xl font-bold tracking-widest'>NEO</span>
        </div>
        <InteractiveGridPattern
          className={cn(
            'mask-[radial-gradient(400px_circle_at_center,white,transparent)]',
            'inset-x-0 inset-y-[0%] h-full skew-y-12'
          )}
        />
        <div className='text-sidebar-foreground relative z-20 mt-auto'>
          <p className='text-lg'>{BRAND_PHRASE}</p>
        </div>
      </div>
      <div className='flex h-full items-center justify-center p-4 lg:p-8'>
        <div className='flex w-full max-w-md flex-col items-center justify-center space-y-6'>
          {children}
        </div>
      </div>
    </div>
  );
}
