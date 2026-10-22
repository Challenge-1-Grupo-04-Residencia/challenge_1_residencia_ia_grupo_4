import type { NextConfig } from "next";

// Porta do backend (a 8000 costuma ter o mkdocs).
const PORTA_API = process.env.PORTA_API ?? "8010";
// Na Vercel não existe backend em 127.0.0.1: lá o destino dos rewrites precisa ser a
// URL pública da API (ex.: https://...onrender.com). Localmente continua a porta 8010.
const DESTINO_API = (
  process.env.BACKEND_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  `http://127.0.0.1:${PORTA_API}`
).replace(/\/+$/, "");

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
      { source: "/api/:caminho*", destination: `${DESTINO_API}/api/:caminho*` },
      { source: "/health", destination: `${DESTINO_API}/health` },
    ];
  },
};

export default nextConfig;
