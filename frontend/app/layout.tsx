<<<<<<< HEAD
import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";

export const metadata: Metadata = {
  title: "AegisFlow AI",
  description: "AI-assisted command center for accountable business workflows.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

=======
import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";
import "./prototype.css";

export const metadata: Metadata = {
  title: "Byapari",
  description: "AI-assisted command center for accountable business workflows.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
>>>>>>> 3ffc1b091eeeb5d0c2ea50affbb8c90e7a14e16e
