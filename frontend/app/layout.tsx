import './globals.css'
import type { Metadata } from 'next'
import { Inter, Playfair_Display, Poppins } from 'next/font/google'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap'
})

const playfair = Playfair_Display({ 
  subsets: ['latin'],
  variable: '--font-playfair',
  display: 'swap'
})

const poppins = Poppins({ 
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700', '800'],
  variable: '--font-poppins',
  display: 'swap'
})

export const metadata: Metadata = {
  title: 'StockPilot - AI-Driven Inventory Management for D2C Brands',
  description: 'Optimize your inventory decisions with AI-powered forecasting. Minimize stockouts, reduce overstocking, and free up working capital.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${playfair.variable} ${poppins.variable} font-sans`}>{children}</body>
    </html>
  )
}

