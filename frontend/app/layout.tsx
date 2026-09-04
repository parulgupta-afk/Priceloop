import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PriceLoop AI",
  description: "AI-Powered Competitive Pricing Intelligence",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <header className="header">
          <div className="container">
            <strong>PriceLoop AI</strong>
            <nav>
              <a href="/">Dashboard</a>
              <a href="/products">Products</a>
              <a href="/login">Login</a>
            </nav>
          </div>
        </header>
        <main className="container">{children}</main>
      </body>
    </html>
  );
}
