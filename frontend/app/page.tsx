'use client'

import Link from 'next/link'
import Navbar from './components/Navbar'
import Footer from './components/Footer'

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-navy-50 to-white">
      <Navbar />
      
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-navy-900 via-primary-900 to-navy-900 text-white py-32 md:py-40 relative overflow-hidden min-h-screen flex items-center">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48Y2lyY2xlIGN4PSIzMCIgY3k9IjMwIiByPSIyIi8+PC9nPjwvZz48L3N2Zz4=')] opacity-30"></div>
        <div className="absolute inset-0 bg-gradient-to-t from-navy-900/50 to-transparent"></div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full">
          <div className="text-center">
            <h1 className="text-7xl md:text-8xl lg:text-9xl font-display font-bold mb-8 leading-tight tracking-wide">
              <span className="bg-gradient-to-r from-white via-primary-200 to-white bg-clip-text text-transparent">
                StockPilot
              </span>
            </h1>
            <div className="w-24 h-0.5 bg-gradient-to-r from-transparent via-primary-400 to-transparent mx-auto mb-10"></div>
            <p className="text-xl md:text-2xl lg:text-3xl text-gray-200 mb-14 max-w-3xl mx-auto leading-relaxed font-display font-light tracking-wide italic">
              AI-driven inventory management that optimizes decisions, minimizes risk, and maximizes cash efficiency for D2C brands
            </p>
            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
              <Link
                href="/register"
                className="bg-gradient-to-r from-primary-600 via-primary-700 to-primary-800 text-white px-10 py-5 rounded-xl hover:from-primary-700 hover:via-primary-800 hover:to-primary-900 transition font-heading font-semibold text-lg shadow-2xl transform hover:scale-105 border-2 border-primary-400/50 tracking-wide"
              >
                Get Started Free
              </Link>
              <Link
                href="/contact"
                className="bg-white/10 backdrop-blur-lg text-white border-2 border-white/30 px-10 py-5 rounded-xl hover:bg-white/20 transition font-heading font-semibold text-lg shadow-2xl transform hover:scale-105 tracking-wide"
              >
                Schedule Demo
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-32 bg-gradient-to-b from-white via-primary-50 to-navy-50 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-24 space-y-6">
            <h2 className="text-5xl md:text-6xl font-display font-bold text-center tracking-tight">
              <span className="bg-gradient-to-r from-navy-900 via-primary-600 to-navy-900 bg-clip-text text-transparent">
                Why Choose StockPilot?
              </span>
            </h2>
            <div className="w-24 h-0.5 bg-gradient-to-r from-transparent via-primary-600 to-transparent mx-auto"></div>
            <p className="text-xl md:text-2xl text-gray-700 font-light max-w-2xl mx-auto tracking-wide">Powerful features for smart inventory management</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-gradient-to-br from-navy-900 to-navy-800 text-white p-8 rounded-2xl shadow-2xl transform hover:scale-105 transition">
              <div className="w-20 h-20 bg-primary-600 rounded-2xl flex items-center justify-center mb-6">
                <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-2xl font-display font-bold mb-4 tracking-tight">AI-Powered Forecasting</h3>
              <p className="text-gray-300 leading-relaxed">
                Advanced machine learning models predict demand with probabilistic forecasts, helping you make data-driven decisions with confidence.
              </p>
            </div>

            <div className="bg-gradient-to-br from-primary-600 to-primary-700 text-white p-8 rounded-2xl shadow-2xl transform hover:scale-105 transition">
              <div className="w-20 h-20 bg-white bg-opacity-20 rounded-2xl flex items-center justify-center mb-6">
                <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-2xl font-display font-bold mb-4 tracking-tight">Cash Optimization</h3>
              <p className="text-gray-100 leading-relaxed">
                Free up working capital by optimizing inventory levels. Balance stockout risk with cash constraints intelligently.
              </p>
            </div>

            <div className="bg-gradient-to-br from-navy-900 to-navy-800 text-white p-8 rounded-2xl shadow-2xl transform hover:scale-105 transition">
              <div className="w-20 h-20 bg-primary-600 rounded-2xl flex items-center justify-center mb-6">
                <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 className="text-2xl font-display font-bold mb-4 tracking-tight">Risk Management</h3>
              <p className="text-gray-300 leading-relaxed">
                Quantify stockout probabilities and inventory risks. Make informed decisions with clear risk metrics and visualizations.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-32 bg-gradient-to-br from-navy-50 via-primary-50 to-navy-50 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-24 space-y-6">
            <h2 className="text-5xl md:text-6xl font-display font-bold text-center tracking-tight">
              <span className="bg-gradient-to-r from-primary-600 via-navy-900 to-primary-600 bg-clip-text text-transparent">
                How It Works
              </span>
            </h2>
            <div className="w-24 h-0.5 bg-gradient-to-r from-transparent via-primary-600 to-transparent mx-auto"></div>
            <p className="text-xl md:text-2xl text-gray-700 font-light max-w-2xl mx-auto tracking-wide">Get started in four simple steps</p>
          </div>
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center bg-white p-8 rounded-2xl shadow-xl border-2 border-primary-200">
              <div className="w-16 h-16 bg-gradient-to-br from-primary-600 to-primary-700 text-white rounded-full flex items-center justify-center mx-auto mb-6 font-bold text-2xl shadow-lg">1</div>
              <h3 className="font-display font-bold text-navy-900 mb-3 text-lg tracking-tight">Upload Data</h3>
              <p className="text-gray-600">Connect your sales history and inventory data</p>
            </div>
            <div className="text-center bg-white p-8 rounded-2xl shadow-xl border-2 border-navy-200">
              <div className="w-16 h-16 bg-gradient-to-br from-navy-600 to-navy-700 text-white rounded-full flex items-center justify-center mx-auto mb-6 font-bold text-2xl shadow-lg">2</div>
              <h3 className="font-display font-bold text-navy-900 mb-3 text-lg tracking-tight">AI Analysis</h3>
              <p className="text-gray-600">Our AI forecasts demand and simulates scenarios</p>
            </div>
            <div className="text-center bg-white p-8 rounded-2xl shadow-xl border-2 border-primary-200">
              <div className="w-16 h-16 bg-gradient-to-br from-primary-600 to-primary-700 text-white rounded-full flex items-center justify-center mx-auto mb-6 font-bold text-2xl shadow-lg">3</div>
              <h3 className="font-display font-bold text-navy-900 mb-3 text-lg tracking-tight">Get Recommendations</h3>
              <p className="text-gray-600">Receive optimized reorder suggestions with risk metrics</p>
            </div>
            <div className="text-center bg-white p-8 rounded-2xl shadow-xl border-2 border-navy-200">
              <div className="w-16 h-16 bg-gradient-to-br from-navy-600 to-navy-700 text-white rounded-full flex items-center justify-center mx-auto mb-6 font-bold text-2xl shadow-lg">4</div>
              <h3 className="font-display font-bold text-navy-900 mb-3 text-lg tracking-tight">Take Action</h3>
              <p className="text-gray-600">Accept recommendations and update inventory</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 bg-gradient-to-r from-primary-600 via-primary-700 to-navy-900 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48Y2lyY2xlIGN4PSIzMCIgY3k9IjMwIiByPSIyIi8+PC9nPjwvZz48L3N2Zz4=')] opacity-30"></div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10 space-y-8">
          <h2 className="text-5xl md:text-6xl font-display font-bold tracking-tight">Ready to Optimize Your Inventory?</h2>
          <div className="w-24 h-0.5 bg-white/50 mx-auto"></div>
          <p className="text-xl md:text-2xl mb-12 text-gray-100 font-light max-w-3xl mx-auto tracking-wide">
            Join D2C brands using AI to make smarter inventory decisions
          </p>
          <Link
            href="/register"
            className="bg-white text-primary-600 px-12 py-6 rounded-xl hover:bg-gray-100 transition font-bold text-xl shadow-2xl transform hover:scale-105 inline-block"
          >
            Start Free Trial
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  )
}
