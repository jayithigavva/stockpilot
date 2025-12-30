'use client'

import Navbar from '../components/Navbar'
import Footer from '../components/Footer'

export default function ContactPage() {

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-navy-900 via-primary-900 to-navy-900 text-white py-32 md:py-40 relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48Y2lyY2xlIGN4PSIzMCIgY3k9IjMwIiByPSIyIi8+PC9nPjwvZz48L3N2Zz4=')] opacity-30"></div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <h1 className="text-7xl md:text-8xl lg:text-9xl font-display font-bold mb-8 tracking-tight">
            <span className="bg-gradient-to-r from-white via-primary-200 to-white bg-clip-text text-transparent">
              Get in Touch
            </span>
          </h1>
          <div className="w-24 h-0.5 bg-gradient-to-r from-transparent via-primary-400 to-transparent mx-auto mb-8"></div>
          <p className="text-xl md:text-2xl lg:text-3xl text-gray-200 font-display font-light italic tracking-wide">
            Get in touch with us. We're here to help.
          </p>
        </div>
      </section>

      {/* Contact Section */}
      <section className="py-24 bg-gradient-to-b from-navy-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-5xl md:text-6xl font-display font-bold text-center mb-6 tracking-tight">
            <span className="bg-gradient-to-r from-navy-900 via-primary-600 to-navy-900 bg-clip-text text-transparent">
              Contact Information
            </span>
          </h2>
          <div className="w-32 h-1 bg-gradient-to-r from-transparent via-primary-600 to-transparent mx-auto mb-12"></div>
          
          {/* Contact Tiles */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {/* Email Tile */}
            <div className="bg-gradient-to-br from-white to-primary-50 rounded-2xl p-6 shadow-xl border-2 border-primary-200 hover:shadow-2xl transition transform hover:scale-105">
              <div className="w-14 h-14 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center mb-4">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="font-display font-bold text-navy-900 mb-2 tracking-tight text-xl">Email</h3>
              <p className="text-gray-600">XXX</p>
            </div>

            {/* Phone 1 Tile */}
            <div className="bg-gradient-to-br from-white to-primary-50 rounded-2xl p-6 shadow-xl border-2 border-primary-200 hover:shadow-2xl transition transform hover:scale-105">
              <div className="w-14 h-14 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center mb-4">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
              </div>
              <h3 className="font-display font-bold text-navy-900 mb-2 tracking-tight text-xl">Phone</h3>
              <a href="tel:+919636177777" className="text-gray-600 hover:text-primary-600 transition block">
                +91 96361 77777
              </a>
              <p className="text-gray-500 text-xs mt-2">(WhatsApp & Call)</p>
            </div>

            {/* Phone 2 Tile */}
            <div className="bg-gradient-to-br from-white to-primary-50 rounded-2xl p-6 shadow-xl border-2 border-primary-200 hover:shadow-2xl transition transform hover:scale-105">
              <div className="w-14 h-14 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center mb-4">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
              </div>
              <h3 className="font-display font-bold text-navy-900 mb-2 tracking-tight text-xl">Phone</h3>
              <a href="tel:+918465968724" className="text-gray-600 hover:text-primary-600 transition block">
                +91 84659 68724
              </a>
              <p className="text-gray-500 text-xs mt-2">(WhatsApp only)</p>
            </div>

            {/* Office Tile */}
            <div className="bg-gradient-to-br from-white to-primary-50 rounded-2xl p-6 shadow-xl border-2 border-primary-200 hover:shadow-2xl transition transform hover:scale-105">
              <div className="w-14 h-14 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center mb-4">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h3 className="font-display font-bold text-navy-900 mb-2 tracking-tight text-xl">Office</h3>
              <p className="text-gray-600">Jaipur, Rajasthan, India</p>
            </div>
          </div>

          {/* Business Hours Tile */}
          <div className="max-w-2xl mx-auto">
            <div className="bg-gradient-to-br from-navy-900 to-navy-800 text-white rounded-2xl p-8 shadow-2xl">
              <h3 className="font-display font-bold mb-6 text-2xl tracking-tight text-center">Business Hours</h3>
              <div className="space-y-3">
                <p className="text-gray-200 text-lg text-center">Monday - Friday: 9:00 AM - 6:00 PM PST</p>
                <p className="text-gray-200 text-lg text-center">Saturday - Sunday: Closed</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  )
}

