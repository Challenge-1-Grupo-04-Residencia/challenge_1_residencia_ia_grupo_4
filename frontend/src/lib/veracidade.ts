/**
 * Traduz o resultado técnico para a apresentação: cor, humor da Vera e frase.
 *
 * As cores vêm dos tokens de `globals.css`, que por sua vez vêm da tabela de
 * faixas de `docs/produto/classificacao.md`. Usar o token em vez do hex é o que
 * faz o tema escuro funcionar sem uma segunda tabela.
 *
 * Por RN-11 o humor da persona acompanha o resultado técnico e nunca o substitui.
 */

import type { NomeDoIcone } from "@/components/ui/Icone";
import type { PoseDaVera } from "@/components/vera/VeraIlustracao";
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
  /** Pose do retrato que acompanha o resultado. */
  pose: PoseDaVera;
  /** Pictograma do veredito: é o que se lê primeiro (ver `vera-gamificacao`). */
  icone: NomeDoIcone;
  /**
   * A palavra curta do carimbo, de no máximo três palavras.
   *
   * Ela **não** substitui o rótulo oficial da faixa, que aparece escrito logo
   * abaixo: "MENTIRA" é bom de ler, mas o que o produto afirma é "provavelmente
   * falsa" (RN-12).
   */
  palavra: string;
  /** Classes do bloco de resultado. */
  cor: string;
  /** Classe da barra de porcentagem. */
  barra: string;
  /** Classe da cor sólida do carimbo. */
  carimbo: string;
  /** Frase temática da Vera, no jeito pernambucano (ver skill `vera-voz`). */
  frase: string;
}

/** As cinco faixas na ordem do termômetro, de pior para melhor. */
export const ORDEM_DAS_FAIXAS: Faixa[] = [
  "Provavelmente falsa",
  "Duvidosa",
  "Inconclusiva",
  "Provavelmente verdadeira",
  "Confirmada por fontes",
];

const ESTILOS: Record<Faixa, EstiloDaFaixa> = {
  // Não é resultado de checagem: a pessoa mandou um "oi" e a triagem do backend
  // devolveu conversa, sem pipeline e sem porcentagem. A frase da Vera vem da
  // `explicacao` da resposta, então aqui a frase fica vazia para não duplicar.
  Conversa: {
    humor: "satisfeita",
    pose: "apontando",
    icone: "conversa",
    palavra: "PROSA",
    cor: "border-tinta bg-papel-2 text-tinta",
    barra: "bg-inconclusiva",
    carimbo: "bg-ocre text-tinta",
    frase: "",
  },
  "Provavelmente falsa": {
    humor: "brava",
    pose: "queixo",
    icone: "mentira",
    palavra: "CONVERSA FIADA",
    cor: "border-falsa bg-falsa-fundo text-tinta",
    barra: "bg-falsa",
    carimbo: "bg-falsa text-white",
    frase: "Vixe, isso aí é conversa de portão.",
  },
  Duvidosa: {
    humor: "desconfiada",
    pose: "queixo",
    icone: "duvida",
    palavra: "DESCONFIE",
    cor: "border-duvidosa bg-duvidosa-fundo text-tinta",
    barra: "bg-duvidosa",
    carimbo: "bg-duvidosa text-white",
    frase: "Olha, eu fico de pé atrás com essa.",
  },
  Inconclusiva: {
    humor: "pensativa",
    pose: "queixo",
    icone: "espera",
    palavra: "AINDA NÃO SEI",
    cor: "border-inconclusiva bg-inconclusiva-fundo text-tinta",
    barra: "bg-inconclusiva",
    carimbo: "bg-inconclusiva text-tinta",
    frase: "Nem eu sei dessa ainda, meu bem. Espera.",
  },
  "Provavelmente verdadeira": {
    humor: "satisfeita",
    pose: "apontando",
    icone: "quase",
    palavra: "PARECE VERDADE",
    cor: "border-verdadeira bg-verdadeira-fundo text-tinta",
    barra: "bg-verdadeira",
    carimbo: "bg-verdadeira text-tinta",
    frase: "Parece ser verdade. Confere as fontes, visse?",
  },
  "Confirmada por fontes": {
    humor: "orgulhosa",
    pose: "apontando",
    icone: "verdade",
    palavra: "É VERDADE",
    cor: "border-confirmada bg-confirmada-fundo text-tinta",
    barra: "bg-confirmada",
    carimbo: "bg-confirmada text-white",
    frase: "Essa é quente e saiu em jornal sério!",
  },
};

export function estiloDaFaixa(faixa: Faixa): EstiloDaFaixa {
  return ESTILOS[faixa] ?? ESTILOS.Inconclusiva;
}

/** Etapas mostradas durante a investigação (RF-03). */
export const ETAPAS: Record<Camada, string> = {
  // A triagem não é etapa de investigação: ela decide se há investigação. Nunca aparece
  // como andamento, mas o contrato exige a entrada.
  TRIAGEM: "Deixa eu ver o que é que tu me mandou…",
  N0: "Deixa eu ver se eu já não conferi isso antes…",
  N1: "Vou espiar quem foi que publicou…",
  N2: "Deixa eu ler com atenção o jeito que isso foi escrito…",
  N3: "Tô ligando pras minhas comadres pra ver quem mais publicou…",
  N4: "Agora eu confiro alegação por alegação. Tenha paciência.",
};

/**
 * Cada posição do termômetro de cinco casas, com a cor da faixa correspondente.
 *
 * O número sozinho é abstrato: "62%" não diz nada para quem lê com dificuldade.
 * Cinco casas desenhadas, com a sua acesa, formam uma régua — e régua se lê de
 * relance. As duas coisas aparecem juntas (ver `vera-gamificacao`).
 */
export const CASAS_DO_TERMOMETRO: Array<{ faixa: Faixa; cor: string }> =
  ORDEM_DAS_FAIXAS.map((faixa) => ({ faixa, cor: ESTILOS[faixa].barra }));

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
