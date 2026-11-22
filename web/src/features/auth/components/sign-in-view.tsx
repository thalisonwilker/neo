import { SignIn as ClerkSignInForm } from '@clerk/nextjs';
import { AuthShell } from './auth-shell';

/** `redirectUrl` já vem validado por `getPostLoginRedirect` (AC-3 e AC-4). */
export default function SignInViewPage({ redirectUrl }: { redirectUrl: string }) {
  return (
    <AuthShell>
      <ClerkSignInForm forceRedirectUrl={redirectUrl} />
    </AuthShell>
  );
}
