import type { Metadata } from "next";
import { Toaster } from "sonner";

import "./globals.css";

export const metadata: Metadata = {
  title: "AeroRL — Autonomous Drone Path Finder",
  description:
    "Reinforcement Learning powered autonomous drone navigation dashboard.",
};

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body>
        {children}

        <Toaster
          position="top-right"
          richColors
          theme="dark"
          toastOptions={{
            style: {
              background: "#07111f",
              border: "1px solid rgba(34,211,238,0.25)",
              color: "#e6faff",
            },
          }}
        />
      </body>
    </html>
  );
}
