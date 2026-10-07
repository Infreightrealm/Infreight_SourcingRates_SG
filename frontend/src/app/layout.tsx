import type { Metadata, Viewport } from "next";
import { Instrument_Sans, Inter } from "next/font/google";
import { Toaster } from "sonner";
import "./globals.css";
import { ThemeProvider } from "@/components/ThemeProvider";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

// Body face for the v2 layout (globals.css switches to it under [data-layout="v2"]).
const instrumentSans = Instrument_Sans({
  subsets: ["latin"],
  variable: "--font-instrument",
});

export const metadata: Metadata = {
  title: "Infreight | Ocean & Air Rate Automation",
  description: "Instant carrier rate search, airfreight routing, and RFQ comparison platform.",
  metadataBase: new URL("https://frontend-production-a90a.up.railway.app"),
  icons: {
    icon: [
      { url: "/infreight_logo.png?v=20260807", type: "image/png" },
      { url: "/icon.png?v=20260807", type: "image/png" },
      { url: "/favicon.ico?v=20260807" },
    ],
    shortcut: "/infreight_logo.png?v=20260807",
    apple: "/infreight_logo.png?v=20260807",
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
  // Lets fixed bottom bars pad for the home indicator via env(safe-area-inset-bottom).
  viewportFit: "cover",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} ${instrumentSans.variable} min-h-screen overflow-x-hidden bg-background font-sans text-foreground antialiased transition-colors duration-300`}>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              try {
                document.documentElement.dataset.layout = 'v2';
                const raw = localStorage.getItem('infreight.workspace.v1');
                if (raw) {
                  const p = JSON.parse(raw);
                  if (p.layout === 'classic') document.documentElement.dataset.layout = 'classic';
                  if (p.accent) document.documentElement.dataset.accent = p.accent;
                  if (p.density) document.documentElement.dataset.density = p.density;
                  if (p.brightness) document.documentElement.dataset.brightness = p.brightness;
                }
              } catch (e) {}
            `,
          }}
        />
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
          <Toaster
            richColors
            position="top-right"
            toastOptions={{
              classNames: {
                toast:
                  "!rounded-xl !border-border !bg-popover !text-popover-foreground !shadow-card-hover",
                description: "!text-muted-foreground",
              },
            }}
          />
        </ThemeProvider>
      </body>
    </html>
  );
}
