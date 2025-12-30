'use client'

import { useState } from 'react'
import Navbar from '../components/Navbar'
import Footer from '../components/Footer'

interface FAQ {
  question: string
  answer: string
}

const faqs: FAQ[] = [
  {
    question: "What is StockPilot?",
    answer: "StockPilot is an AI-driven inventory management platform designed specifically for D2C brands. We use machine learning to forecast demand, simulate inventory scenarios, and provide optimized reorder recommendations that balance stockout risk with cash constraints."
  },
  {
    question: "How does the AI forecasting work?",
    answer: "Our system uses LightGBM (a gradient boosting framework) with quantile regression to produce probabilistic demand forecasts. We analyze your historical sales data, incorporate calendar features (day of week, seasonality), lag features, and rolling statistics to predict future demand with confidence intervals (P10, P50, P90)."
  },
  {
    question: "What data do I need to get started?",
    answer: "You need historical sales data (at least 30 days, preferably 90+ days) with dates and quantities sold. You'll also need to provide product information like unit costs, selling prices, lead times, and minimum order quantities. The more historical data you have, the better our forecasts become."
  },
  {
    question: "How accurate are the forecasts?",
    answer: "While we focus on business outcomes rather than just forecast accuracy, our models typically achieve strong performance. However, our primary goal is to minimize expected economic loss—balancing the costs of overstocking vs understocking—rather than just predicting demand accurately."
  },
  {
    question: "Can I use StockPilot with multiple SKUs?",
    answer: "Yes! StockPilot supports multiple products (SKUs). When you have cash constraints, our capital allocation feature ranks SKUs by economic efficiency (loss avoided per rupee spent) and optimally allocates your available capital across products."
  },
  {
    question: "What happens when I accept a recommendation?",
    answer: "When you accept a reorder recommendation, your inventory levels are automatically updated in the system. The decision is logged for audit purposes, and you can track the impact over time. You maintain full control—recommendations are suggestions, not auto-executed orders."
  },
  {
    question: "How do you handle cash constraints?",
    answer: "Our system explicitly models cash constraints. When you have limited working capital, we evaluate feasible order quantities and select the one that minimizes expected economic loss while respecting your cash budget. For multi-SKU scenarios, we allocate capital optimally across products."
  },
  {
    question: "Is my data secure?",
    answer: "Absolutely. We use industry-standard security practices including encrypted data transmission (HTTPS), secure authentication (JWT tokens), and multi-tenant data isolation. Your data is never shared with third parties."
  },
  {
    question: "What's the difference between StockPilot and traditional inventory management?",
    answer: "Traditional systems often rely on simple rules (like reorder points) or basic forecasting. StockPilot uses advanced AI to: (1) Provide probabilistic forecasts with uncertainty quantification, (2) Simulate thousands of scenarios to estimate risks, (3) Explicitly model economic costs (overstock vs understock), and (4) Optimize for business outcomes, not just forecast accuracy."
  },
  {
    question: "Do I need technical expertise to use StockPilot?",
    answer: "No! StockPilot is designed for business users. Our interface is intuitive, and we provide clear explanations of recommendations. You just need to upload your sales data and product information—we handle the complex AI modeling behind the scenes."
  },
  {
    question: "Can I integrate StockPilot with my existing systems?",
    answer: "Currently, StockPilot supports CSV uploads and API access. We're working on integrations with popular e-commerce platforms and inventory management systems. Contact us if you need a specific integration."
  },
  {
    question: "What's the pricing?",
    answer: "We offer flexible pricing plans based on your needs. Contact us for details on our pricing tiers, which are designed to scale with your business. We also offer a free trial so you can experience the platform before committing."
  }
]

export default function FAQsPage() {
  const [openIndex, setOpenIndex] = useState<number | null>(0)

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-navy-900 via-primary-900 to-navy-900 text-white py-32 md:py-40 relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48Y2lyY2xlIGN4PSIzMCIgY3k9IjMwIiByPSIyIi8+PC9nPjwvZz48L3N2Zz4=')] opacity-30"></div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <h1 className="text-7xl md:text-8xl lg:text-9xl font-display font-bold mb-8 tracking-tight">
            <span className="bg-gradient-to-r from-white via-primary-200 to-white bg-clip-text text-transparent">
              FAQs
            </span>
          </h1>
          <div className="w-24 h-0.5 bg-gradient-to-r from-transparent via-primary-400 to-transparent mx-auto mb-8"></div>
          <p className="text-xl md:text-2xl lg:text-3xl text-gray-200 font-display font-light italic tracking-wide">
            Everything you need to know about StockPilot
          </p>
        </div>
      </section>

      {/* FAQs Section */}
      <section className="py-24 bg-gradient-to-b from-navy-50 to-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div
                key={index}
                className="border-2 border-navy-200 rounded-xl overflow-hidden shadow-lg hover:shadow-xl transition bg-white"
              >
                <button
                  onClick={() => setOpenIndex(openIndex === index ? null : index)}
                  className={`w-full px-8 py-5 text-left flex justify-between items-center transition ${
                    openIndex === index 
                      ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white' 
                      : 'bg-gradient-to-r from-navy-50 to-white hover:from-navy-100 hover:to-navy-50 text-navy-900'
                  }`}
                >
                  <span className={`font-display font-bold text-lg tracking-tight ${openIndex === index ? 'text-white' : 'text-navy-900'}`}>{faq.question}</span>
                  <svg
                    className={`w-6 h-6 transition-transform ${
                      openIndex === index ? 'text-white transform rotate-180' : 'text-primary-600'
                    }`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {openIndex === index && (
                  <div className="px-8 py-6 bg-gradient-to-br from-primary-50 to-navy-50 text-gray-800 text-lg leading-relaxed border-t-2 border-primary-200 font-light">
                    {faq.answer}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Still Have Questions */}
      <section className="py-24 bg-gradient-to-r from-primary-600 via-primary-700 to-navy-900 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl md:text-5xl font-display font-bold text-white mb-6 tracking-tight">Still Have Questions?</h2>
          <p className="text-xl text-gray-100 mb-10 font-display font-light italic tracking-wide">
            Can't find the answer you're looking for? Please reach out to our friendly team.
          </p>
          <a
            href="/contact"
            className="bg-white text-primary-600 px-10 py-4 rounded-xl hover:bg-gray-100 transition font-heading font-semibold text-lg shadow-2xl transform hover:scale-105 inline-block"
          >
            Contact Us
          </a>
        </div>
      </section>

      <Footer />
    </div>
  )
}

