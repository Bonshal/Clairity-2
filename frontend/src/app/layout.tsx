import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Clairity — Market Intelligence Platform",
  description:
    "AI-powered market research, trend detection, and content strategy platform. Discover emerging opportunities before your competitors.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="bg-mesh" />
        {children}
      </body>
    </html>
  );
}
