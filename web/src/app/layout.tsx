import Providers from '@/components/layout/providers';
import { Toaster } from '@/components/ui/sonner';
import { fontVariables } from '@/components/themes/font.config';
import ThemeProvider from '@/components/themes/theme-provider';
import { BRAND_PHRASE } from '@/features/auth/components/auth-shell';
import { cn } from '@/lib/utils';
import type { Metadata, Viewport } from 'next';
import NextTopLoader from 'nextjs-toploader';
import '../styles/globals.css';

/** 0039 AC-5: cor de fundo do tema NEO escuro. */
const NEO_BACKGROUND = '#050816';

export const metadata: Metadata = {
  ...(process.env.NEXT_PUBLIC_APP_URL
    ? { metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL) }
    : {}),
  // As páginas já definem o título completo no padrão "<página> | NEO".
  title: {
    default: 'NEO',
    template: '%s'
  },
  description: BRAND_PHRASE,
  applicationName: 'NEO'
};

export const viewport: Viewport = {
  themeColor: NEO_BACKGROUND,
  colorScheme: 'dark'
};

/** 0039 AC-5: tema único NEO, sempre escuro, em qualquer preferência do sistema. */
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang='pt-BR' suppressHydrationWarning data-theme='neo' className='dark'>
      <body
        className={cn(
          'bg-background overflow-x-hidden overscroll-none font-sans antialiased',
          fontVariables
        )}
      >
        <NextTopLoader color='var(--primary)' showSpinner={false} />
        <ThemeProvider attribute='class' forcedTheme='dark' disableTransitionOnChange>
          <Providers>
            <Toaster />
            {children}
          </Providers>
        </ThemeProvider>
      </body>
    </html>
  );
}
