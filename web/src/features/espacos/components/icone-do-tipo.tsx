import { IconBook, IconFolder, IconHeart, IconSparkles } from '@tabler/icons-react';

import { PERFIS_DE_TIPO, type IconeDoTipo } from '../perfis';
import type { TipoEspaco } from '@/lib/api';

const ICONES: Record<IconeDoTipo, typeof IconFolder> = {
  pasta: IconFolder,
  livro: IconBook,
  brilho: IconSparkles,
  coracao: IconHeart
};

/** Ícone do Tipo de espaço, na cor do tipo. */
export function IconeDoTipoEspaco({
  tipo,
  size = 18,
  className
}: {
  tipo: TipoEspaco;
  size?: number;
  className?: string;
}) {
  const perfil = PERFIS_DE_TIPO[tipo];
  const Icone = ICONES[perfil.icone];
  return <Icone size={size} aria-hidden className={className} style={{ color: perfil.cor }} />;
}
