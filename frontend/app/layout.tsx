import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'CyberSOC | CODEX DEMO', description: 'Codex Ambassador — interaktywne demo z danymi syntetycznymi, bez zewnętrznych API.' };
export default function Layout({children}: Readonly<{children: React.ReactNode}>) { return <html lang="pl"><body>{children}</body></html>; }
