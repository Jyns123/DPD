import type { Metadata } from "next";
import "./globals.css";
import "./editorial.css";
import "./luminous.css";
import AnalyticsConsent from '../components/analytics-consent';

export const metadata: Metadata = {
  title: "InmoScore — Viviendas en Lima",
  description: "Explora avisos históricos de viviendas en Lima y compara precio, entorno y espacio según tus prioridades.",
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
      <body className="antialiased">{children}<AnalyticsConsent /></body>
    </html>
  );
}
