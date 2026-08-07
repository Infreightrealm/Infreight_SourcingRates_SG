import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import { Toaster } from "sonner";
import "./globals.css";
import { ThemeProvider } from "@/components/ThemeProvider";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Infreight | Ocean & Air Rate Automation",
  description: "Instant carrier rate search, airfreight routing, and RFQ comparison platform.",
  metadataBase: new URL("https://frontend-production-a90a.up.railway.app"),
  icons: {
    icon: [
      { url: "/infreight_logo.png", type: "image/png" },
      { url: "/icon.png", type: "image/png" },
    ],
    shortcut: "/infreight_logo.png",
    apple: "/infreight_logo.png",
  },
  openGraph: {
    title: "Infreight | Ocean & Air Rate Automation",
    description: "Instant carrier rate search, airfreight routing, and RFQ comparison platform.",
    url: "https://frontend-production-a90a.up.railway.app",
    siteName: "Infreight Sourcing",
    images: [
      {
        url: "/infreight_logo.png",
        width: 1200,
        height: 630,
        alt: "Infreight Ocean & Air Rate Automation",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Infreight | Ocean & Air Rate Automation",
    description: "Instant carrier rate search, airfreight routing, and RFQ comparison platform.",
    images: ["/infreight_logo.png"],
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased bg-slate-50 dark:bg-[#060a14] text-slate-900 dark:text-white min-h-screen transition-colors duration-300 overflow-x-hidden`}>

        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
          <Toaster richColors position="top-right" />
        </ThemeProvider>
      </body>
    </html>
  );
}
