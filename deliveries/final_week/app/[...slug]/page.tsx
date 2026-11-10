import { notFound } from 'next/navigation';
export const dynamic = 'force-dynamic';
export default async function Page({ params }: { params: Promise<{ slug: string[] }> }) {
  const { slug } = await params;
  const pages = ['explorar', 'registro', 'ingresar', 'perfil', 'guardados', 'cuenta'];
  if (!(slug.length === 1 && pages.includes(slug[0])) && !(slug.length === 2 && slug[0] === 'inmueble')) notFound();
  return null;
}
