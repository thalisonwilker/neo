import { Separator } from '../ui/separator';
import { Breadcrumbs } from '../breadcrumbs';
import { SidebarToggle } from './sidebar-toggle';

/** 0039 AC-4: cabeçalho com o botão de recolher o menu e a trilha da página. */
export default function Header() {
  return (
    <header className='flex h-14 shrink-0 items-center gap-3 border-b px-3 md:px-4'>
      <div className='flex min-w-0 flex-1 items-center'>
        <SidebarToggle />
        <Separator
          orientation='vertical'
          className='mr-3 ml-1.5 data-vertical:h-4 data-vertical:self-center'
        />
        <Breadcrumbs />
      </div>
    </header>
  );
}
