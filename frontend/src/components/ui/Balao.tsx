/**
 * Balão de fala com rabicho (ver skill `vera-estilo`).
 *
 * É o elemento onde o traço grosso do cordel é gasto: quando a Vera fala, o
 * contorno pesado é o que separa a fala dela do resto da tela. Card de lista e
 * campo de formulário ficam discretos de propósito — se tudo tem contorno de 3px,
 * nada tem.
 *
 * O rabicho é desenhado com dois triângulos sobrepostos (um da cor do traço,
 * outro do fundo) em vez de SVG, porque assim ele herda `currentColor` e
 * acompanha o tema claro/escuro sem precisar de variante.
 */

import type { ReactNode } from "react";

type Lado = "esquerda" | "direita";

interface Props {
  children: ReactNode;
  /** De que lado sai o rabicho. `esquerda` = a Vera fala. */
  lado?: Lado;
  /** Cor de fundo, como classe do Tailwind. Padrão: papel do cartão. */
  fundo?: string;
  className?: string;
}

export function Balao({
  children,
  lado = "esquerda",
  fundo = "bg-papel-2",
  className = "",
}: Props) {
  const naEsquerda = lado === "esquerda";

  return (
    <div className={`relative ${className}`}>
      <div
        className={`rounded-lg border-[3px] border-tinta p-4 shadow-bloco ${fundo}`}
      >
        {children}
      </div>

      {/* Rabicho: o triângulo de trás faz o contorno, o da frente tapa o miolo. */}
      <span
        aria-hidden
        className={`absolute top-6 h-0 w-0 border-y-[10px] border-y-transparent ${
          naEsquerda
            ? "-left-[13px] border-r-[13px] border-r-tinta"
            : "-right-[13px] border-l-[13px] border-l-tinta"
        }`}
      />
      <span
        aria-hidden
        className={`absolute top-6 h-0 w-0 border-y-[8px] border-y-transparent ${
          naEsquerda
            ? "-left-[8px] border-r-[10px] border-r-[var(--papel-2)]"
            : "-right-[8px] border-l-[10px] border-l-[var(--papel-2)]"
        }`}
      />
    </div>
  );
}
