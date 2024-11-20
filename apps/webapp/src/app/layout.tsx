import './globals.css'

import type { Metadata } from 'next'

import LayoutNavbar from '@/components/navbar'
import { ThemeProvider } from '@/components/theme-provider'
import { Toaster } from '@/components/ui/toaster'

export const metadata: Metadata = {
  title: 'Electro Cloud',
  icons: {
    icon: '/icon.svg'
  }
}

export default function RootLayout ({
  children
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-slate-50 dark:bg-slate-950 text-foreground">
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <LayoutNavbar />
          {children}
        </ThemeProvider>
        <Toaster />
      </body>
    </html>
  )
}
