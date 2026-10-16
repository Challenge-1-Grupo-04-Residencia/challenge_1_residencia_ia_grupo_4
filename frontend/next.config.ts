import type { NextConfig } from "next";

// Porta do backend (a 8000 costuma ter o mkdocs).
const PORTA_API = process.env.PORTA_API ?? "8010";

const nextConfig: NextConfig = {
  images: {
    // Avatares do GitHub da equipe, usados na tela de apresentação (/sobre).
    remotePatterns: [
      { protocol: "https", hostname: "avatars.githubusercontent.com" },
    ],
  },

  // O navegador fala só com a porta do frontend; o servidor do Next encaminha a API
  // para o backend. Assim nao ha segunda porta nem CORS, e o acesso pela rede funciona
  // igual em Windows, Mac, Linux e mobile (so a :3000 precisa estar acessivel).
  async rewrites() {
    return [
      { source: "/api/:caminho*", destination: `http://127.0.0.1:${PORTA_API}/api/:caminho*` },
      { source: "/health", destination: `http://127.0.0.1:${PORTA_API}/health` },
    ];
  },
};

export default nextConfig;
