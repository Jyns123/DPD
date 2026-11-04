import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "InmoScore — Tu próximo hogar, con más claridad",
  description: "Compara viviendas de Lima según tu presupuesto, tus prioridades y una referencia de precio explicable.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es-PE">
      <body className="antialiased">{children}</body>
    </html>
  );
}
