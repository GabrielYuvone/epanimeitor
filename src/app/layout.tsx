import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Epanimeitor · Animador de GIFs",
  description: "Crea animaciones frame a frame y exportalas como GIF. Herramienta simple, colorida y gratuita de la Escuela para Animadores Rosario.",
  keywords: ["Epanimeitor", "animador", "GIF", "frame a frame", "animación", "Escuela para Animadores", "Rosario"],
  authors: [{ name: "Escuela para Animadores Rosario" }],
  openGraph: {
    title: "Epanimeitor",
    description: "Crea animaciones frame a frame y exportalas como GIF.",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Epanimeitor",
    description: "Crea animaciones frame a frame y exportalas como GIF.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground`}
      >
        {children}
        <Toaster />
      </body>
    </html>
  );
}
