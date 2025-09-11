import './globals.css';

export const metadata = {
  title: 'Worksie',
  description: 'AI-powered estimates for field operations.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
