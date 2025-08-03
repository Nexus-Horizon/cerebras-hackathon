import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import BrowserExtensionHandler from '../components/BrowserExtensionHandler';
import Logo from '@/components/Logo';
import { Metadata } from "next";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: 'AutoModel',
  description: 'You ask. You upload. We benchmark. Instantly.',
}

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark:bg-gray-900 dark:text-white">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased pt-[102px]`}
      >
        <BrowserExtensionHandler>
          <Logo />
          {children}
        </BrowserExtensionHandler>
      </body>
    </html>
  );
}
