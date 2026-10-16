import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    // Avatares do GitHub da equipe, usados na tela de apresentação (/sobre).
    remotePatterns: [
      { protocol: "https", hostname: "avatars.githubusercontent.com" },
    ],
  },
};

export default nextConfig;
