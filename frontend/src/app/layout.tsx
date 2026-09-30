import type { Metadata } from "next";
import { Baloo_2, Caveat, Nunito } from "next/font/google";

import { BarraLateral } from "@/components/layout/BarraLateral";
import { BarraTopo } from "@/components/layout/BarraTopo";
import "./globals.css";

/**
 * Tipografia da Vera — ver .claude/skills/vera-estilo/SKILL.md.
 *
 * As três famílias carregam `latin-ext` porque português tem ã, õ, ç e acento
 * agudo: fonte que quebra acento está descartada de saída.
 */

/** Display: títulos, veredito, números. */
const display = Baloo_2({
  variable: "--fonte-display",
  subsets: ["latin", "latin-ext"],
  weight: ["500", "600", "700", "800"],
  display: "swap",
});

/** Texto: corpo e interface. Legível em 14px no celular. */
const texto = Nunito({
  variable: "--fonte-texto",
  subsets: ["latin", "latin-ext"],
  weight: ["400", "600", "700"],
  display: "swap",
});

/** Mão: frases curtas da Vera. Nunca carrega informação sozinha. */
const mao = Caveat({
  variable: "--fonte-mao",
  subsets: ["latin", "latin-ext"],
  weight: ["600", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Vera · Verificadora de Fatos",
  description:
    "Checagem de notícias em formato de conversa: a Vera cruza o que você leu com fontes confiáveis e explica por que aquilo parece verdadeiro ou falso.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="pt-BR"
      className={`${display.variable} ${texto.variable} ${mao.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body className="min-h-full">
        <div className="flex min-h-dvh">
          <BarraLateral />
          {/* pb-20 no celular abre espaço para a barra de navegação fixa. */}
          <div className="flex min-w-0 flex-1 flex-col pb-20 md:pb-0">
            <BarraTopo />
            <main className="flex-1">{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}
