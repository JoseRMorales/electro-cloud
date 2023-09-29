import './globals.css'
import 'flowbite'

import type { Metadata } from 'next'

import LayoutNavbar from '../components/navbar'
import { ThemeProvider } from '../components/theme-provider'

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
    <html lang='en'>
      <body>
        <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
          >
          <LayoutNavbar />
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
