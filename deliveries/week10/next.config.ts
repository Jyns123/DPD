import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  poweredByHeader: false,
  devIndicators: false,
  agentRules: false,
  serverExternalPackages: ['node:sqlite'],
};

export default nextConfig;
