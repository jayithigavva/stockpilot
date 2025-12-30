'use client'

import Image from 'next/image'
import Navbar from '../components/Navbar'
import Footer from '../components/Footer'

export default function AboutPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-navy-900 via-primary-900 to-navy-900 text-white py-32 md:py-40 relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48Y2lyY2xlIGN4PSIzMCIgY3k9IjMwIiByPSIyIi8+PC9nPjwvZz48L3N2Zz4=')] opacity-30"></div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <h1 className="text-7xl md:text-8xl lg:text-9xl font-display font-bold mb-8 tracking-tight">
            <span className="bg-gradient-to-r from-white via-primary-200 to-white bg-clip-text text-transparent">
              About Us
            </span>
          </h1>
          <div className="w-24 h-0.5 bg-gradient-to-r from-transparent via-primary-400 to-transparent mx-auto mb-8"></div>
          <p className="text-xl md:text-2xl lg:text-3xl text-gray-200 max-w-4xl mx-auto font-display font-light italic leading-relaxed tracking-wide">
            We're on a mission to help D2C brands optimize their inventory decisions using AI and data science.
          </p>
        </div>
      </section>

      {/* Founders Section */}
      <section className="py-32 bg-gradient-to-b from-navy-50 to-white relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-5xl md:text-6xl font-display font-bold text-center mb-6 tracking-tight">
              <span className="bg-gradient-to-r from-navy-900 via-primary-600 to-navy-900 bg-clip-text text-transparent">
                Meet Our Founders
              </span>
            </h2>
            <div className="w-32 h-1 bg-gradient-to-r from-transparent via-primary-600 to-transparent mx-auto"></div>
          </div>
          <div className="grid md:grid-cols-2 gap-16 max-w-6xl mx-auto">
            {/* Founder 1 - Jayithi Gavva */}
            <div className="text-center">
              <div className="w-80 h-80 md:w-96 md:h-96 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl mx-auto mb-8 flex items-center justify-center overflow-hidden shadow-xl">
                <Image
                  src="/founders/founder1.png"
                  alt="Jayithi Gavva"
                  width={384}
                  height={384}
                  className="w-full h-full object-cover"
                />
              </div>
              <h3 className="text-3xl font-display font-bold text-navy-900 mb-3 tracking-tight">Jayithi Gavva</h3>
              <p className="text-primary-600 font-heading font-semibold text-lg mb-6">Founder</p>
              <p className="text-gray-700 text-lg leading-relaxed">
                XXX
              </p>
            </div>

            {/* Founder 2 - Ariana Agarwal */}
            <div className="text-center">
              <div className="w-80 h-80 md:w-96 md:h-96 bg-gradient-to-br from-navy-500 to-navy-700 rounded-2xl mx-auto mb-8 flex items-center justify-center overflow-hidden shadow-xl">
                <Image
                  src="/founders/founder2.jpg"
                  alt="Ariana Agarwal"
                  width={384}
                  height={384}
                  className="w-full h-full object-cover"
                />
              </div>
              <h3 className="text-3xl font-display font-bold text-navy-900 mb-3 tracking-tight">Ariana Agarwal</h3>
              <p className="text-primary-600 font-heading font-semibold text-lg mb-6">Founder</p>
              <p className="text-gray-700 text-lg leading-relaxed">
                XXX
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Our Story */}
      <section className="py-32 bg-gradient-to-br from-primary-50 via-white to-navy-50 relative">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-5xl md:text-6xl font-display font-bold text-center mb-6 tracking-tight">
              <span className="bg-gradient-to-r from-primary-600 via-navy-900 to-primary-600 bg-clip-text text-transparent">
                Our Story
              </span>
            </h2>
            <div className="w-32 h-1 bg-gradient-to-r from-transparent via-primary-600 to-transparent mx-auto"></div>
          </div>
          <div className="space-y-6 text-gray-700 text-lg">
            <p>
              StockPilot was born from a simple observation: D2C brands were making inventory decisions based on gut feeling rather than data. We saw brands either overstocking (tying up cash) or understocking (losing sales), with no clear way to balance these trade-offs.
            </p>
            <p>
              As high school students passionate about technology and entrepreneurship, we realized that the same AI-powered inventory optimization tools used by Fortune 500 companies could be made accessible to growing D2C brands. The challenge wasn't just forecasting accuracy—it was about optimizing for business outcomes: minimizing economic loss while respecting cash constraints.
            </p>
            <p>
              Today, StockPilot helps D2C brands make smarter inventory decisions by combining probabilistic demand forecasting, Monte Carlo simulation, and economic cost modeling. We don't just predict demand—we help you optimize for cash efficiency and business outcomes.
            </p>
          </div>
        </div>
      </section>

      {/* Vision & Mission */}
      <section className="py-32 bg-gradient-to-b from-white to-navy-50 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-5xl md:text-6xl font-display font-bold text-center mb-6 tracking-tight">
              <span className="bg-gradient-to-r from-navy-900 via-primary-600 to-navy-900 bg-clip-text text-transparent">
                Vision & Mission
              </span>
            </h2>
            <div className="w-32 h-1 bg-gradient-to-r from-transparent via-primary-600 to-transparent mx-auto"></div>
          </div>
          <div className="grid md:grid-cols-2 gap-16">
            <div className="bg-gradient-to-br from-navy-900 to-navy-800 text-white p-10 rounded-3xl shadow-2xl">
              <h3 className="text-4xl font-display font-bold text-primary-400 mb-8 tracking-tight">Vision</h3>
              <p className="text-gray-200 text-lg leading-relaxed font-light">
                To become the decision engine that powers how modern D2C businesses manage inventory and cash, replacing gut instinct with economic clarity.
              </p>
            </div>
            <div className="bg-gradient-to-br from-primary-600 to-primary-700 text-white p-10 rounded-3xl shadow-2xl">
              <h3 className="text-4xl font-display font-bold mb-8 tracking-tight">Mission</h3>
              <p className="text-gray-200 text-lg leading-relaxed font-light">
                To help cash-constrained D2C founders make smarter inventory decisions by combining probabilistic forecasting, economic optimization, and transparent decision logic, so every reorder maximizes capital efficiency.
              </p>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  )
}

