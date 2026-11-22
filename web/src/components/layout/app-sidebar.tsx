'use client';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  useSidebar
} from '@/components/ui/sidebar';
import { UserAvatarProfile } from '@/components/user-avatar-profile';
import { MINHA_CONTA_PATH, navItems } from '@/config/nav-config';
import { SIGN_OUT_LABEL, useSignOut } from '@/features/auth/use-sign-out';
import { useUser } from '@clerk/nextjs';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Icons } from '../icons';

const itemClass =
  'text-sidebar-foreground/80 hover:bg-sidebar-accent/60 hover:text-sidebar-foreground data-active:bg-sidebar-accent data-active:font-medium data-active:text-sidebar-accent-foreground data-active:hover:bg-sidebar-accent [&>svg]:text-sidebar-foreground/60 data-active:[&>svg:first-child]:text-sidebar-primary';
// 4px horizontal padding on the icon rail lets 32px buttons fit the 2.375rem rail
const railPadding = 'group-data-[collapsible=icon]:px-1';

const isActivePath = (pathname: string, url: string) =>
  pathname === url || pathname.startsWith(`${url}/`);

/** 0039 AC-2: marca NEO no topo do menu lateral. */
function MarcaNeo() {
  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <SidebarMenuButton
          size='lg'
          tooltip='NEO'
          render={<Link href='/dashboard/overview' aria-label='NEO — Início' />}
        >
          <span
            aria-hidden='true'
            className='bg-primary text-primary-foreground grid size-8 flex-none place-items-center rounded-lg font-bold'
          >
            N
          </span>
          <span className='font-bold tracking-widest'>NEO</span>
        </SidebarMenuButton>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}

export default function AppSidebar() {
  const pathname = usePathname() ?? '';
  const { isMobile, setOpenMobile } = useSidebar();

  return (
    <Sidebar collapsible='icon' variant='inset'>
      <SidebarHeader className={railPadding}>
        <MarcaNeo />
      </SidebarHeader>
      <SidebarContent className='overflow-x-hidden'>
        <SidebarGroup className={railPadding}>
          <SidebarMenu className='gap-0.5' aria-label='Menu principal'>
            {navItems.map((item) => {
              const Icon = item.icon ? Icons[item.icon] : Icons.logo;
              const active = isActivePath(pathname, item.url);
              return (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    tooltip={item.title}
                    isActive={active}
                    className={itemClass}
                    render={
                      <Link
                        href={item.url}
                        aria-label={item.title}
                        aria-current={active ? 'page' : undefined}
                      />
                    }
                    onClick={() => {
                      if (isMobile) setOpenMobile(false);
                    }}
                  >
                    <Icon />
                    <span>{item.title}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              );
            })}
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className={railPadding}>
        <NavUser />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}

/** 0039 AC-2 e AC-3: usuário no rodapé, com "Minha conta" e "Sair". */
function NavUser() {
  const { user } = useUser();
  const signOut = useSignOut();
  const router = useRouter();

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger
            render={
              <SidebarMenuButton
                size='lg'
                className='data-popup-open:bg-sidebar-accent data-popup-open:text-sidebar-accent-foreground'
              />
            }
          >
            {user && <UserAvatarProfile className='size-8 rounded-lg' showInfo user={user} />}
            <Icons.chevronsUpDown className='text-muted-foreground ml-auto size-4' />
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className='min-w-56 rounded-lg'
            side='right'
            align='end'
            sideOffset={4}
          >
            <DropdownMenuGroup>
              <DropdownMenuLabel className='p-0 font-normal'>
                <div className='px-1 py-1.5'>
                  {user && <UserAvatarProfile className='size-8 rounded-lg' showInfo user={user} />}
                </div>
              </DropdownMenuLabel>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            <DropdownMenuGroup>
              <DropdownMenuItem onClick={() => router.push(MINHA_CONTA_PATH)}>
                <Icons.account />
                Minha conta
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={signOut}>
              <Icons.logout aria-hidden />
              {SIGN_OUT_LABEL}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}
