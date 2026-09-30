/**
 * Traduz o resultado técnico para a apresentação: cores, humor da Vera e rótulos.
 *
 * As cores e os humores vêm da tabela de faixas em `docs/produto/classificacao.md`.
 * Por RN-11, o humor da persona acompanha o resultado técnico e nunca o substitui.
 */

import type { Camada, Dificuldade, Dimensao, Faixa } from "@/types/checagem";

/** Estados de animação da Vera. */
export type HumorDaVera =
  | "brava"
  | "desconfiada"
  | "pensativa"
  | "satisfeita"
  | "orgulhosa"
  | "investigando";

export interface EstiloDaFaixa {
  humor: HumorDaVera;
  /** Classes Tailwind do bloco de resultado. */
  cor: string;
  /** Classe da barra de porcentagem. */
  barra: string;
  /** Frase temática da Vera para esta faixa. */
  frase: string;
}

const ESTILOS: Record<Faixa, EstiloDaFaixa> = {
  "Provavelmente falsa": {
    humor: "brava",
    cor: "border-red-500/40 bg-red-500/10 text-red-100",
    barra: "bg-red-500",
    frase: "Ih, isso aí é conversa de portão. Ninguém sério publicou.",
  },
  Duvidosa: {
    humor: "desconfiada",
    cor: "border-orange-500/40 bg-orange-500/10 text-orange-100",
    barra: "bg-orange-500",
    frase: "Olha, eu que não acredito nesse povo. Fica de olho.",
  },
  Inconclusiva: {
    humor: "pensativa",
    cor: "border-amber-400/40 bg-amber-400/10 text-amber-100",
    barra: "bg-amber-400",
    frase: "Nem eu sei dessa ainda, e olha que eu sei de tudo. Espera sair mais coisa.",
  },
  "Provavelmente verdadeira": {
    humor: "satisfeita",
    cor: "border-lime-500/40 bg-lime-500/10 text-lime-100",
    barra: "bg-lime-500",
    frase: "Essa parece ser verdade, viu? Mas confere as fontes aí embaixo.",
  },
  "Confirmada por fontes": {
    humor: "orgulhosa",
    cor: "border-green-600/40 bg-green-600/10 text-green-100",
    barra: "bg-green-600",
    frase: "Essa é quente e é verdade! Saiu em tudo que é jornal sério.",
  },
};

export function estiloDaFaixa(faixa: Faixa): EstiloDaFaixa {
  return ESTILOS[faixa] ?? ESTILOS.Inconclusiva;
}

/** Etapas mostradas durante a investigação (RF-03). */
export const ETAPAS: Record<Camada, string> = {
  N0: "Vendo se já conferi isso antes…",
  N1: "Olhando quem publicou…",
  N2: "Lendo com atenção como está escrito…",
  N3: "Ligando pras minhas comadres pra ver quem mais publicou…",
  N4: "Conferindo alegação por alegação…",
};

export const ROTULO_DIFICULDADE: Record<Dificuldade, string> = {
  facil: "Fácil",
  mediano: "Mediano",
  dificil: "Difícil",
};

export const ROTULO_DIMENSAO: Record<Dimensao, string> = {
  fonte: "Fonte",
  conteudo: "Conteúdo",
  corroboracao: "Corroboração",
};

/**
 * Converte a confiança 0–1 em texto. A porcentagem crua confunde: quem lê "confiança
 * de 42%" tende a somar com a veracidade, que é outra coisa.
 */
export function rotuloDeConfianca(confianca: number): string {
  if (confianca >= 0.8) return "Alta";
  if (confianca >= 0.6) return "Boa";
  if (confianca >= 0.4) return "Média";
  return "Baixa";
}

/**
 * Peso relativo de um sinal na explicação, para desenhar a barra de contribuição.
 * Sinais indisponíveis devolvem 0 — não pesaram no resultado.
 */
export function contribuicao(peso: number, score: number | null): number {
  if (score === null) return 0;
  return peso * Math.abs(score - 0.5) * 2;
}
