import type { Metadata } from "next";
import { Baloo_2, Caveat, Nunito } from "next/font/google";
import "./globals.css";

/**
 * Tipografia da Vera — ver .claude/skills/vera-estilo/SKILL.md.
 *
 * As três famílias carregam `latin-ext` porque português tem ã, õ, ç e acento
 * agudo: fonte que quebra acento está descartada de saída.
 */

/** Display: títulos, veredito, números. Densidade de capa de cordel. */
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

/** Mão: frases curtas da Vera e ênfases. Nunca carrega informação sozinha. */
const mao = Caveat({
  variable: "--fonte-mao",
  subsets: ["latin", "latin-ext"],
  weight: ["600", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Senhora Vera",
  description:
    "Checagem de notícias em formato de conversa: a Vera cruza o que você leu com fontes confiáveis e explica por que aquilo parece verdadeiro ou falso.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="pt-BR"
      className={`${display.variable} ${texto.variable} ${mao.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col">{children}</body>
    </html>
  );
}
