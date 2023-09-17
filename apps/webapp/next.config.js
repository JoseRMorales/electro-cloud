/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
      return [
      {
        source: '/api/:path*',
        // Trailing slash is optional, see below
        destination: 'http://localhost:8001/api/:path*/'
      }
    ]
  },
  compiler: {
    styledComponents: true,
  },
}

module.exports = nextConfig

