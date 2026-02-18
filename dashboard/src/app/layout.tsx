import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Sidebar from '@/components/sidebar'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
})

export const metadata: Metadata = {
  title: 'A&J Content Engine',
  description: 'Dashboard de aprobacion para el pipeline de contenido de A&J Phygital Group',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className={inter.variable}>
      <body className="font-sans">
        <Sidebar />
        <main className="ml-60 min-h-screen p-8">
          {children}
        </main>
      </body>
    </html>
  )
}
