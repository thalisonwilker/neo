import { SignUp as ClerkSignUpForm } from '@clerk/nextjs';
import { AuthShell } from './auth-shell';

/** `redirectUrl` já vem validado por `getPostLoginRedirect` (AC-3 e AC-4). */
export default function SignUpViewPage({ redirectUrl }: { redirectUrl: string }) {
  return (
    <AuthShell>
      <ClerkSignUpForm forceRedirectUrl={redirectUrl} />
    </AuthShell>
  );
}
