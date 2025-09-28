/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  env: {
    NEXT_PUBLIC_ORCHESTRATOR_URL: process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || 'http://localhost:9000',
    NEXT_PUBLIC_VECTOR_AGENT_URL: process.env.NEXT_PUBLIC_VECTOR_AGENT_URL || 'http://localhost:9002',
    NEXT_PUBLIC_MSAL_CLIENT_ID: process.env.NEXT_PUBLIC_MSAL_CLIENT_ID || 'your-client-id',
    NEXT_PUBLIC_MSAL_TENANT_ID: process.env.NEXT_PUBLIC_MSAL_TENANT_ID || 'your-tenant-id',
  },
}

module.exports = nextConfig