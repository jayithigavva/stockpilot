const path = require('path')

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [],
    unoptimized: false,
  },
  webpack: (config) => {
    // Explicitly resolve @ alias for Vercel builds
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname),
    }
    return config
  },
}

module.exports = nextConfig

