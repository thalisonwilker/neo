import type { NavItem } from '@/types';

/** 0039 AC-2: itens do menu lateral do Neo. */
export const navItems: NavItem[] = [
  {
    title: 'Início',
    url: '/dashboard/overview',
    icon: 'dashboard'
  }
];

/** 0039 AC-3: página de conta do Usuário, aberta pelo menu do usuário. */
export const MINHA_CONTA_PATH = '/dashboard/profile';
