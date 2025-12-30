'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import Logo from './Logo'

export default function Navbar() {
  const pathname = usePathname()

  return (
    <nav className="bg-gradient-to-r from-navy-900 via-navy-800 to-navy-900 shadow-xl sticky top-0 z-50 border-b-2 border-primary-600">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          {/* Logo */}
          <Logo className="text-white" />

          {/* Navigation Links */}
          <div className="hidden md:flex space-x-6">
            <Link 
              href="/" 
              className={`${pathname === '/' ? 'text-primary-400 border-b-2 border-primary-400' : 'text-white hover:text-primary-300'} px-4 py-2 text-sm font-semibold transition transform hover:scale-105`}
            >
              Home
            </Link>
            <Link 
              href="/about" 
              className={`${pathname === '/about' ? 'text-primary-400 border-b-2 border-primary-400' : 'text-white hover:text-primary-300'} px-4 py-2 text-sm font-semibold transition transform hover:scale-105`}
            >
              About Us
            </Link>
            <Link 
              href="/faqs" 
              className={`${pathname === '/faqs' ? 'text-primary-400 border-b-2 border-primary-400' : 'text-white hover:text-primary-300'} px-4 py-2 text-sm font-semibold transition transform hover:scale-105`}
            >
              FAQs
            </Link>
            <Link 
              href="/partnerships" 
              className={`${pathname === '/partnerships' ? 'text-primary-400 border-b-2 border-primary-400' : 'text-white hover:text-primary-300'} px-4 py-2 text-sm font-semibold transition transform hover:scale-105`}
            >
              Partnerships
            </Link>
            <Link 
              href="/contact" 
              className={`${pathname === '/contact' ? 'text-primary-400 border-b-2 border-primary-400' : 'text-white hover:text-primary-300'} px-4 py-2 text-sm font-semibold transition transform hover:scale-105`}
            >
              Contact
            </Link>
          </div>

          {/* Login Button */}
          <Link
            href="/login"
            className="bg-gradient-to-r from-primary-600 to-primary-700 text-white px-8 py-3 rounded-lg hover:from-primary-700 hover:to-primary-800 transition font-semibold shadow-lg transform hover:scale-105"
          >
            Login
          </Link>
        </div>
      </div>
    </nav>
  )
}

