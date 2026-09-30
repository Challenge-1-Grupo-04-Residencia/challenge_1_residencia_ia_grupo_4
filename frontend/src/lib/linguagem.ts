/**
 * Tradução dos sinais para a linguagem da conversa (RF-02).
 *
 * O critério de aceite é explícito: o vocabulário do chat **não** pode ter jargão de
 * machine learning. "Classificador estilístico TF-IDF + SVM" diz muito para quem
 * construiu o sistema e nada para quem recebeu uma corrente no mensageiro.
 *
 * Por isso há duas linguagens no produto, e elas não se misturam:
 *
 * - **a conversa** usa estas frases, no jeito da Vera;
 * - **a auditoria** (RF-33) mantém ID, peso e nome técnico do sinal, porque ali o
 *   objetivo é justamente permitir conferir a decisão.
 *
 * Esconder o detalhe técnico do chat não é escondê-lo: ele está a um clique, na seção
 * de detalhamento.
 */

import type { Sinal } from "@/types/checagem";

/** Como cada sinal é dito na conversa, conforme apontou a favor ou contra. */
interface FalaDoSinal {
  favor: string;
  contra: string;
}

const FALAS: Record<string, FalaDoSinal> = {
  "S-01": {
    favor: "o site que publicou é conhecido e sério",
    contra: "o site que publicou já me deu motivo pra desconfiar",
  },
  "S-02": {
    favor: "esse site não anda espalhando mentira",
    contra: "esse site já publicou coisa falsa nos últimos meses",
  },
  "S-03": {
    favor: "o site existe há bastante tempo",
    contra: "esse site nasceu ontem, querida",
  },
  "S-04": {
    favor: "a página diz quem escreveu e quando",
    contra: "a página não diz quem escreveu nem quando",
  },
  "S-05": {
    favor: "tem um autor com nome e história",
    contra: "não tem autor nenhum assinando",
  },
  "S-06": {
    favor: "está escrito com jeito de notícia de verdade",
    contra: "está escrito com aquele jeitão de corrente",
  },
  "S-07": {
    favor: "o texto é calmo, sem gritaria",
    contra: "o texto grita: caixa alta, ponto de exclamação e pressa pra você repassar",
  },
  "S-08": {
    favor: "o texto não apela para o medo nem para a raiva",
    contra: "o texto mexe com medo e raiva, que é o que faz a gente compartilhar sem pensar",
  },
  "S-09": {
    favor: "o texto mostra de onde tirou o que afirma",
    contra: "o texto afirma um monte de coisa e não mostra de onde tirou",
  },
  "S-10": {
    favor: "não parece texto feito por máquina",
    contra: "pode ter sido escrito por máquina",
  },
  "S-11": {
    favor: "outros jornais sérios publicaram o mesmo",
    contra: "nenhum jornal sério publicou isso",
  },
  "S-12": {
    favor: "o que eu encontrei confirma o que está escrito",
    contra: "o que eu encontrei contradiz o que está escrito",
  },
  "S-13": {
    favor: "o texto parece original",
    contra: "o texto é cópia mexida de outro lugar",
  },
};

/** Acima disto o sinal aponta a favor da veracidade. */
const NEUTRO = 0.5;

export function sinalAponta(sinal: Sinal): "favor" | "contra" | "indisponivel" {
  if (sinal.score === null) return "indisponivel";
  return sinal.score >= NEUTRO ? "favor" : "contra";
}

/**
 * A frase da conversa para um sinal. Devolve `null` para sinal sem dado — na conversa
 * o que não foi medido não vira frase, só aparece na auditoria.
 */
export function falaDoSinal(sinal: Sinal): string | null {
  const direcao = sinalAponta(sinal);
  if (direcao === "indisponivel") return null;
  return FALAS[sinal.id]?.[direcao] ?? null;
}

/**
 * Junta as frases numa lista natural: "a, b e c".
 *
 * Vírgula em tudo ficaria com cara de relatório; a Vera fala, não relata.
 */
export function juntarFrases(frases: string[]): string {
  if (frases.length === 0) return "";
  if (frases.length === 1) return frases[0];
  return `${frases.slice(0, -1).join(", ")} e ${frases[frases.length - 1]}`;
}

/**
 * O parágrafo que a Vera fala no chat, a partir dos sinais que mais pesaram.
 *
 * Fica vazio quando nenhum sinal tem frase: nesse caso a interface cai na explicação
 * que veio da API, em vez de mostrar um balão sem conteúdo (RN-05).
 */
export function explicarEmLinguagemSimples(sinais: Sinal[], limite = 3): string {
  const aFavor: string[] = [];
  const contra: string[] = [];

  for (const sinal of sinais) {
    const fala = falaDoSinal(sinal);
    if (!fala) continue;
    (sinalAponta(sinal) === "favor" ? aFavor : contra).push(fala);
  }

  const partes: string[] = [];
  if (contra.length > 0) {
    partes.push(`O que me deixou de pé atrás: ${juntarFrases(contra.slice(0, limite))}.`);
  }
  if (aFavor.length > 0) {
    partes.push(`O que jogou a favor: ${juntarFrases(aFavor.slice(0, limite))}.`);
  }
  return partes.join(" ");
}
