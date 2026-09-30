/**
 * Selo de veredito, como no protótipo (URGENTE / EM ANÁLISE / VERDADEIRO).
 *
 * O protótipo traz "VERDADEIRO", mas RN-12 proíbe a Vera de afirmar certeza
 * absoluta: os rótulos usam "provavelmente" e "confirmada **por fontes**". O selo
 * então carrega a forma curta da faixa real, não um carimbo de verdade.
 *
 * Cor nunca é o único portador da informação — o rótulo vem escrito dentro do
 * selo, porque vermelho e verde é justamente o eixo que quem tem daltonia perde.
 */

import type { Faixa } from "@/types/checagem";

/** Forma curta de cada faixa, para caber no selo sem perder o sentido. */
const ROTULO_CURTO: Record<Faixa, string> = {
  "Provavelmente falsa": "PROVAVELMENTE FALSA",
  Duvidosa: "DUVIDOSA",
  Inconclusiva: "EM ANÁLISE",
  "Provavelmente verdadeira": "PROVAVELMENTE VERDADEIRA",
  "Confirmada por fontes": "CONFIRMADA POR FONTES",
};

const CORES: Record<Faixa, string> = {
  "Provavelmente falsa": "bg-falsa text-white",
  Duvidosa: "bg-duvidosa text-white",
  Inconclusiva: "bg-inconclusiva text-tinta",
  "Provavelmente verdadeira": "bg-verdadeira text-tinta",
  "Confirmada por fontes": "bg-confirmada text-white",
};

interface Props {
  faixa: Faixa;
  className?: string;
}

export function Selo({ faixa, className = "" }: Props) {
  return (
    <span
      className={`inline-block rounded-sm px-2.5 py-1 font-display text-xs font-bold tracking-wide ${CORES[faixa]} ${className}`}
    >
      {ROTULO_CURTO[faixa]}
    </span>
  );
}
