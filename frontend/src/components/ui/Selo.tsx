/**
 * Selo de veredito, como carimbo de quadrinho.
 *
 * O protótipo traz "VERDADEIRO", mas RN-12 proíbe a Vera de afirmar certeza
 * absoluta: os rótulos usam "provavelmente" e "confirmada **por fontes**". O selo
 * carrega a forma curta da faixa real, não um carimbo de verdade.
 *
 * Cor nunca é o único portador da informação: o selo traz o pictograma e o rótulo
 * escrito juntos — vermelho e verde é justamente o eixo que quem tem daltonia
 * perde, e parte de quem usa a Vera lê com dificuldade (ver `vera-gamificacao`).
 */

import { Icone } from "@/components/ui/Icone";
import { estiloDaFaixa } from "@/lib/veracidade";
import type { Faixa } from "@/types/checagem";

/** Forma curta de cada faixa, para caber no selo sem perder o sentido. */
const ROTULO_CURTO: Record<Faixa, string> = {
  // A entrada não era notícia, então não há veredito para carimbar: quem chama o selo
  // nesse caso é que está errado, mas o rótulo existe para não exibir `undefined`.
  Conversa: "CONVERSA",
  "Provavelmente falsa": "PROVAVELMENTE FALSA",
  Duvidosa: "DUVIDOSA",
  Inconclusiva: "EM ANÁLISE",
  "Provavelmente verdadeira": "PROVAVELMENTE VERDADEIRA",
  "Confirmada por fontes": "CONFIRMADA POR FONTES",
};

interface Props {
  faixa: Faixa;
  className?: string;
}

export function Selo({ faixa, className = "" }: Props) {
  const estilo = estiloDaFaixa(faixa);

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-sm border-2 border-tinta px-2 py-1 font-display text-base leading-none ${estilo.carimbo} ${className}`}
    >
      <Icone nome={estilo.icone} tamanho={18} />
      {ROTULO_CURTO[faixa]}
    </span>
  );
}
