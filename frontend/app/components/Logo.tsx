'use client'

import Image from 'next/image'
import Link from 'next/link'

interface LogoProps {
  className?: string
}

export default function Logo({ className = '' }: LogoProps) {
  // TODO: Replace this with your actual logo
  // Place your logo file in: frontend/public/logo.png or logo.svg
  // Then uncomment the Image component below and remove the placeholder div
  
  const isDark = className.includes('text-white')
  
  return (
    <Link href="/" className={`flex items-center space-x-2 ${className}`}>
      <Image
        src="/logo.jpeg"
        alt="StockPilot Logo"
        width={40}
        height={40}
        className="h-10 w-auto object-contain"
      />
      <span className={`font-display font-bold text-xl tracking-tight ${isDark || className.includes('text-white') ? 'text-white' : 'text-navy-900'}`}>StockPilot</span>
    </Link>
  )
}

