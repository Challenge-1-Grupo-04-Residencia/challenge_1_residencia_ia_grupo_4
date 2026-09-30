/**
 * Traduz o resultado técnico para a apresentação: cor, humor da Vera e frase.
 *
 * As cores vêm dos tokens de `globals.css`, que por sua vez vêm da tabela de
 * faixas de `docs/produto/classificacao.md`. Usar o token em vez do hex é o que
 * faz o tema escuro funcionar sem uma segunda tabela.
 *
 * Por RN-11 o humor da persona acompanha o resultado técnico e nunca o substitui.
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
  /** Classes do bloco de resultado. */
  cor: string;
  /** Classe da barra de porcentagem. */
  barra: string;
  /** Frase temática da Vera, no jeito pernambucano (ver skill `vera-voz`). */
  frase: string;
}

const ESTILOS: Record<Faixa, EstiloDaFaixa> = {
  "Provavelmente falsa": {
    humor: "brava",
    cor: "border-falsa bg-falsa-fundo text-tinta",
    barra: "bg-falsa",
    frase: "Ih, isso aí é conversa de portão. Ninguém sério publicou, não.",
  },
  Duvidosa: {
    humor: "desconfiada",
    cor: "border-duvidosa bg-duvidosa-fundo text-tinta",
    barra: "bg-duvidosa",
    frase: "Olha, eu que não acredito nesse povo. Fica de olho, visse?",
  },
  Inconclusiva: {
    humor: "pensativa",
    cor: "border-inconclusiva bg-inconclusiva-fundo text-tinta",
    barra: "bg-inconclusiva",
    frase:
      "Nem eu sei dessa ainda, e olha que eu sei de tudo. Espera sair mais coisa.",
  },
  "Provavelmente verdadeira": {
    humor: "satisfeita",
    cor: "border-verdadeira bg-verdadeira-fundo text-tinta",
    barra: "bg-verdadeira",
    frase: "Essa parece ser verdade, viu? Mas confere as fontes aí embaixo.",
  },
  "Confirmada por fontes": {
    humor: "orgulhosa",
    cor: "border-confirmada bg-confirmada-fundo text-tinta",
    barra: "bg-confirmada",
    frase: "Essa é quente e é verdade! Saiu em tudo que é jornal sério.",
  },
};

export function estiloDaFaixa(faixa: Faixa): EstiloDaFaixa {
  return ESTILOS[faixa] ?? ESTILOS.Inconclusiva;
}

/** Etapas mostradas durante a investigação (RF-03). */
export const ETAPAS: Record<Camada, string> = {
  N0: "Deixa eu ver se eu já não conferi isso antes…",
  N1: "Vou espiar quem foi que publicou…",
  N2: "Deixa eu ler com atenção o jeito que isso foi escrito…",
  N3: "Tô ligando pras minhas comadres pra ver quem mais publicou…",
  N4: "Agora eu confiro alegação por alegação. Tenha paciência.",
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
 * Converte a confiança 0–1 em texto. A porcentagem crua confunde: quem lê
 * "confiança de 42%" tende a somar com a veracidade, que é outra coisa.
 */
export function rotuloDeConfianca(confianca: number): string {
  if (confianca >= 0.8) return "Alta";
  if (confianca >= 0.6) return "Boa";
  if (confianca >= 0.4) return "Média";
  return "Baixa";
}

/**
 * Peso relativo de um sinal na explicação, para desenhar a barra de contribuição.
 * Sinal indisponível devolve 0 — não pesou no resultado.
 */
export function contribuicao(peso: number, score: number | null): number {
  if (score === null) return 0;
  return peso * Math.abs(score - 0.5) * 2;
}
