import type { Metadata } from "next";
import { Bangers, Nunito, Patrick_Hand } from "next/font/google";

import { BarraLateral } from "@/components/layout/BarraLateral";
import "./globals.css";

/**
 * Tipografia da Vera — ver .claude/skills/vera-estilo/SKILL.md.
 *
 * As três famílias carregam `latin-ext` porque português tem ã, õ, ç e acento
 * agudo: fonte que quebra acento está descartada de saída. Foi o que descartou a
 * Comic Neue, candidata óbvia de quadrinho, que só tem `latin`.
 */

/**
 * Display: letreiro de quadrinho para título, veredito e número.
 *
 * A Bangers tem um peso só. Pedir `font-bold` dela faz o navegador fabricar um
 * negrito sintético, que engrossa o traço de forma irregular e suja o desenho da
 * letra — por isso o peso aparece aqui e em lugar nenhum mais.
 */
const display = Bangers({
  variable: "--fonte-display",
  subsets: ["latin", "latin-ext"],
  weight: ["400"],
  display: "swap",
});

/** Texto: corpo e interface. Legível em 14px no celular. */
const texto = Nunito({
  variable: "--fonte-texto",
  subsets: ["latin", "latin-ext"],
  weight: ["400", "600", "700"],
  display: "swap",
});

/** Mão: frases curtas da Vera, com traço de letreirista. Nunca carrega
 * informação sozinha — ver `vera-estilo`. */
const mao = Patrick_Hand({
  variable: "--fonte-mao",
  subsets: ["latin", "latin-ext"],
  weight: ["400"],
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
        {/* Não há barra de topo. Ela tinha uma busca que fazia o mesmo que a
            caixa do chat, mais um sino e um avatar que não levavam a lugar
            nenhum — e comia a altura de que a abertura e o chat precisam para
            caber juntos na primeira tela. */}
        <div className="flex min-h-dvh">
          <BarraLateral />
          {/* pb-20 no celular abre espaço para a barra de navegação fixa. */}
          <div className="flex min-w-0 flex-1 flex-col pb-20 md:pb-0">
            <main className="flex-1">{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}
