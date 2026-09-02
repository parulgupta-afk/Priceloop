import "./globals.css";

export const metadata = {
  title: "Priceloop",
  description: "Watch every price move before your competitors do.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
