'use client'

import Link from 'next/link'
import Logo from './Logo'

export default function Footer() {
  return (
    <footer className="bg-gradient-to-br from-navy-900 via-navy-800 to-navy-900 text-white border-t-2 border-primary-600">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div>
            <div className="mb-4">
              <Logo className="text-white" />
            </div>
            <p className="text-gray-400 text-sm">
              AI-driven inventory management for D2C brands. Optimize your inventory decisions with data-driven insights.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2 text-sm">
              <li><Link href="/" className="text-gray-400 hover:text-white transition">Home</Link></li>
              <li><Link href="/about" className="text-gray-400 hover:text-white transition">About Us</Link></li>
              <li><Link href="/faqs" className="text-gray-400 hover:text-white transition">FAQs</Link></li>
              <li><Link href="/contact" className="text-gray-400 hover:text-white transition">Contact</Link></li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="font-semibold mb-4">Resources</h3>
            <ul className="space-y-2 text-sm">
              <li><Link href="/partnerships" className="text-gray-400 hover:text-white transition">Partnerships</Link></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition">Documentation</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition">Blog</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition">Support</a></li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="font-semibold mb-4">Get in Touch</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>Email: emaillllll</li>
              <li>Phone: +91 96361 77777, +91 84659 68724</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-navy-700 mt-8 pt-8 text-center text-sm text-gray-400">
          <p>&copy; {new Date().getFullYear()} StockPilot. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}

