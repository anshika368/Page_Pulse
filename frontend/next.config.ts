import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // NEXT_PUBLIC_API_URL is baked in at build time. For Vercel, set it in the
  // project dashboard under Settings → Environment Variables.
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000",
  },
};

export default nextConfig;
