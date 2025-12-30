'use client'

import Navbar from '../components/Navbar'
import Footer from '../components/Footer'

export default function PartnershipsPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-navy-900 via-primary-900 to-navy-900 text-white py-32 md:py-40 relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48Y2lyY2xlIGN4PSIzMCIgY3k9IjMwIiByPSIyIi8+PC9nPjwvZz48L3N2Zz4=')] opacity-30"></div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <h1 className="text-7xl md:text-8xl lg:text-9xl font-display font-bold mb-8 tracking-tight">
            <span className="bg-gradient-to-r from-white via-primary-200 to-white bg-clip-text text-transparent">
              Partnerships
            </span>
          </h1>
          <div className="w-24 h-0.5 bg-gradient-to-r from-transparent via-primary-400 to-transparent mx-auto mb-8"></div>
          <p className="text-xl md:text-2xl lg:text-3xl text-gray-200 font-display font-light italic tracking-wide">
            Join forces with StockPilot to deliver better inventory solutions
          </p>
        </div>
      </section>

      {/* Partnership Types */}
      <section className="py-32 bg-gradient-to-b from-navy-50 to-white relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-5xl md:text-6xl font-display font-bold text-center mb-6 tracking-tight">
              <span className="bg-gradient-to-r from-navy-900 via-primary-600 to-navy-900 bg-clip-text text-transparent">
                Partnership Opportunities
              </span>
            </h2>
            <div className="w-32 h-1 bg-gradient-to-r from-transparent via-primary-600 to-transparent mx-auto"></div>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 mb-16">
            {/* Integration Partners */}
            <div className="border-2 border-primary-300 rounded-2xl p-8 hover:shadow-2xl transition bg-gradient-to-br from-white to-primary-50 transform hover:scale-105">
              <div className="w-20 h-20 bg-gradient-to-br from-primary-600 to-primary-700 rounded-2xl flex items-center justify-center mb-6 shadow-lg">
                <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" />
                </svg>
              </div>
              <h3 className="text-2xl font-display font-bold text-navy-900 mb-4 tracking-tight">Integration Partners</h3>
              <p className="text-gray-600 mb-4">
                Connect StockPilot with e-commerce platforms, ERP systems, and inventory management tools. We're looking for partners to build seamless integrations.
              </p>
              <ul className="text-sm text-gray-600 space-y-2">
                <li>• E-commerce platforms (Shopify, WooCommerce)</li>
                <li>• ERP systems</li>
                <li>• Warehouse management systems</li>
                <li>• Accounting software</li>
              </ul>
            </div>

            {/* Technology Partners */}
            <div className="border-2 border-navy-300 rounded-2xl p-8 hover:shadow-2xl transition bg-gradient-to-br from-white to-navy-50 transform hover:scale-105">
              <div className="w-20 h-20 bg-gradient-to-br from-navy-600 to-navy-700 rounded-2xl flex items-center justify-center mb-6 shadow-lg">
                <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-2xl font-display font-bold text-navy-900 mb-4 tracking-tight">Technology Partners</h3>
              <p className="text-gray-600 mb-4">
                Collaborate on AI/ML research, data infrastructure, and cloud services. We work with technology providers to enhance our platform capabilities.
              </p>
              <ul className="text-sm text-gray-600 space-y-2">
                <li>• Cloud providers (AWS, GCP, Azure)</li>
                <li>• ML/AI platforms</li>
                <li>• Data analytics tools</li>
                <li>• Infrastructure providers</li>
              </ul>
            </div>

            {/* Channel Partners */}
            <div className="border-2 border-primary-300 rounded-2xl p-8 hover:shadow-2xl transition bg-gradient-to-br from-white to-primary-50 transform hover:scale-105">
              <div className="w-20 h-20 bg-gradient-to-br from-primary-600 to-primary-700 rounded-2xl flex items-center justify-center mb-6 shadow-lg">
                <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h3 className="text-2xl font-display font-bold text-navy-900 mb-4 tracking-tight">Channel Partners</h3>
              <p className="text-gray-600 mb-4">
                Resell or refer StockPilot to your customers. We offer attractive partner programs for consultants, agencies, and service providers.
              </p>
              <ul className="text-sm text-gray-600 space-y-2">
                <li>• Supply chain consultants</li>
                <li>• Digital agencies</li>
                <li>• Business advisors</li>
                <li>• Referral partners</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section className="py-32 bg-gradient-to-br from-primary-50 via-white to-navy-50 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-5xl md:text-6xl font-display font-bold text-center mb-6 tracking-tight">
              <span className="bg-gradient-to-r from-primary-600 via-navy-900 to-primary-600 bg-clip-text text-transparent">
                Partner Benefits
              </span>
            </h2>
            <div className="w-32 h-1 bg-gradient-to-r from-transparent via-primary-600 to-transparent mx-auto"></div>
          </div>
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="bg-white p-6 rounded-lg">
              <h3 className="text-xl font-display font-bold text-white mb-4 tracking-tight">For Integration Partners</h3>
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-start">
                  <span className="text-primary-400 mr-2 font-bold">✓</span>
                  <span>Co-marketing opportunities</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-400 mr-2 font-bold">✓</span>
                  <span>Technical support and documentation</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-400 mr-2 font-bold">✓</span>
                  <span>Dedicated partner manager</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-400 mr-2 font-bold">✓</span>
                  <span>Early access to new features</span>
                </li>
              </ul>
            </div>

            <div className="bg-gradient-to-br from-primary-600 to-primary-700 text-white p-8 rounded-2xl shadow-xl">
              <h3 className="text-xl font-display font-bold mb-4 tracking-tight">For Channel Partners</h3>
              <ul className="space-y-2">
                <li className="flex items-start">
                  <span className="text-white mr-2 font-bold">✓</span>
                  <span>Competitive commission structure</span>
                </li>
                <li className="flex items-start">
                  <span className="text-white mr-2 font-bold">✓</span>
                  <span>Sales and marketing materials</span>
                </li>
                <li className="flex items-start">
                  <span className="text-white mr-2 font-bold">✓</span>
                  <span>Training and certification</span>
                </li>
                <li className="flex items-start">
                  <span className="text-white mr-2 font-bold">✓</span>
                  <span>Partner portal access</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-32 bg-gradient-to-r from-primary-600 via-primary-700 to-navy-900 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48Y2lyY2xlIGN4PSIzMCIgY3k9IjMwIiByPSIyIi8+PC9nPjwvZz48L3N2Zz4=')] opacity-30"></div>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <h2 className="text-5xl md:text-6xl font-display font-bold mb-8 tracking-tight">Interested in Partnering?</h2>
          <div className="w-24 h-0.5 bg-white/50 mx-auto mb-8"></div>
          <p className="text-xl md:text-2xl mb-12 text-gray-100 font-display font-light italic tracking-wide">
            Let's discuss how we can work together to deliver value to your customers
          </p>
          <a
            href="/contact"
            className="bg-white text-primary-600 px-12 py-6 rounded-2xl hover:bg-gray-100 transition font-bold text-xl shadow-2xl transform hover:scale-105 inline-block"
          >
            Get in Touch
          </a>
        </div>
      </section>

      <Footer />
    </div>
  )
}

