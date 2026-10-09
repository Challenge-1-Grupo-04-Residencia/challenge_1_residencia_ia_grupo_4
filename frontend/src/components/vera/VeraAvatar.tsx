/**
 * O rosto da Vera, para o avatar da conversa.
 *
 * Era um SVG desenhado em código, com boca e sobrancelha trocadas por humor. A
 * arte oficial da personagem chegou em PNG e é incomparavelmente melhor, então o
 * desenho em código saiu — ver skill `vera-estilo`.
 *
 * Isso tem uma consequência que não dá para esconder: **a expressão não muda
 * mais** (RF-05). Quem passa a carregar o humor do resultado é a moldura em volta
 * do rosto, que assume a cor da faixa, e o pictograma do veredito ao lado. O
 * `aria-label` continua dizendo o humor, porque para quem usa leitor de tela a
 * moldura colorida não existe.
 */

import Image from "next/image";

import type { HumorDaVera } from "@/lib/veracidade";

interface Props {
  humor?: HumorDaVera;
  /** Lado do quadrado, em pixels. */
  tamanho?: number;
  /** Cor da moldura, como classe do Tailwind. Padrão: o traço preto. */
  moldura?: string;
  className?: string;
}

const DESCRICAO: Record<HumorDaVera, string> = {
  brava: "Senhora Vera, contrariada",
  desconfiada: "Senhora Vera, desconfiada",
  pensativa: "Senhora Vera, pensativa",
  satisfeita: "Senhora Vera, satisfeita",
  orgulhosa: "Senhora Vera, orgulhosa",
  investigando: "Senhora Vera, investigando",
};

export function VeraAvatar({
  humor = "pensativa",
  tamanho = 72,
  moldura = "border-tinta",
  className = "",
}: Props) {
  return (
    <span
      className={`inline-flex shrink-0 items-center justify-center overflow-hidden rounded-total border-[3px] bg-ocre-suave ${moldura} ${className}`}
      style={{ width: tamanho, height: tamanho }}
    >
      {/* `object-contain`, e não `cover`: a arte é um retrato de cabeça inteira,
          mais alta que larga, e o corte quadrado do `cover` comia o queixo e as
          laterais do rosto. Cabendo inteira, a cabeça fica menor dentro do
          círculo, e é por isso que o fundo ocre aparece atrás dela. */}
      <Image
        src="/vera-rosto.png"
        alt={DESCRICAO[humor]}
        width={tamanho}
        height={tamanho}
        className="h-full w-full scale-105 object-contain object-bottom"
        priority={tamanho >= 96}
      />
    </span>
  );
}
