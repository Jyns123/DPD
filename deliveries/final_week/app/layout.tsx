import type { Metadata } from "next";
import "./globals.css";
import InmoScoreApp from "../components/inmoscore-app";
import { getCaptureDate, getListings } from "../lib/catalog";

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
      <body className="antialiased"><InmoScoreApp listingCount={getListings().length} captureDate={getCaptureDate()} />{children}</body>
    </html>
  );
}
