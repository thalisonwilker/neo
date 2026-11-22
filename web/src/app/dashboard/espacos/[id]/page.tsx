import { auth } from '@clerk/nextjs/server';
import { EspacoView } from '@/features/espacos/components/espaco-dashboard';

/** 0040 AC-13 e AC-14: dashboard do Espaço. */
export default async function EspacoPage({ params }: { params: Promise<{ id: string }> }) {
  await auth.protect();
  const { id } = await params;
  return <EspacoView id={id} />;
}
