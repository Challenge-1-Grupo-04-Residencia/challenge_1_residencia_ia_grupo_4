/**
 * Avatar da Senhora Vera, em estilo flat conforme a direção de arte.
 *
 * O humor muda com a faixa de veracidade do resultado (RF-05). A arte é SVG inline e
 * não imagem: a extensão de navegador e o PWA precisam de algo leve, e a troca de
 * expressão vira mudança de atributo em vez de download de outro arquivo.
 */

import type { HumorDaVera } from "@/lib/veracidade";

interface Props {
  humor?: HumorDaVera;
  /** Lado do quadrado, em pixels. */
  tamanho?: number;
  className?: string;
}

/** Curva da boca por humor: positivo sorri, negativo entorta para baixo. */
const BOCA: Record<HumorDaVera, string> = {
  brava: "M 34 62 Q 42 56 50 62",
  desconfiada: "M 34 61 Q 42 59 50 61",
  pensativa: "M 34 61 L 50 61",
  satisfeita: "M 34 59 Q 42 65 50 59",
  orgulhosa: "M 32 58 Q 42 68 52 58",
  investigando: "M 35 61 Q 42 60 49 62",
};

/** Inclinação das sobrancelhas: franzidas para desconfiança e raiva. */
const SOBRANCELHAS: Record<HumorDaVera, { esquerda: string; direita: string }> = {
  brava: { esquerda: "M 28 38 L 38 42", direita: "M 56 38 L 46 42" },
  desconfiada: { esquerda: "M 28 40 L 38 38", direita: "M 56 41 L 46 41" },
  pensativa: { esquerda: "M 28 39 L 38 39", direita: "M 56 39 L 46 39" },
  satisfeita: { esquerda: "M 28 39 L 38 37", direita: "M 56 39 L 46 37" },
  orgulhosa: { esquerda: "M 28 38 L 38 36", direita: "M 56 38 L 46 36" },
  investigando: { esquerda: "M 28 40 L 38 37", direita: "M 56 40 L 46 37" },
};

const DESCRICAO: Record<HumorDaVera, string> = {
  brava: "Senhora Vera com expressão brava",
  desconfiada: "Senhora Vera com expressão desconfiada",
  pensativa: "Senhora Vera pensativa",
  satisfeita: "Senhora Vera satisfeita",
  orgulhosa: "Senhora Vera orgulhosa",
  investigando: "Senhora Vera investigando",
};

export function VeraAvatar({ humor = "pensativa", tamanho = 72, className = "" }: Props) {
  const boca = BOCA[humor];
  const { esquerda, direita } = SOBRANCELHAS[humor];
  const investigando = humor === "investigando";

  return (
    <svg
      width={tamanho}
      height={tamanho}
      viewBox="0 0 84 84"
      role="img"
      aria-label={DESCRICAO[humor]}
      className={className}
    >
      {/* Cabelo grisalho, em dois volumes para dar o coque da persona. */}
      <circle cx="42" cy="40" r="30" fill="#c9c4d6" />
      <circle cx="42" cy="18" r="11" fill="#c9c4d6" />
      {/* Rosto */}
      <circle cx="42" cy="44" r="24" fill="#f2cdb4" />
      {/* Óculos: a Vera confere tudo de perto. */}
      <circle cx="33" cy="48" r="9" fill="none" stroke="#3b3550" strokeWidth="2.5" />
      <circle cx="51" cy="48" r="9" fill="none" stroke="#3b3550" strokeWidth="2.5" />
      <path d="M 42 48 L 42 48" stroke="#3b3550" strokeWidth="2.5" />
      <line x1="42" y1="48" x2="42" y2="48" stroke="#3b3550" strokeWidth="2.5" />
      <path d="M 42 47 L 42 49" stroke="#3b3550" strokeWidth="2.5" />
      {/* Olhos */}
      <circle cx="33" cy="48" r="3" fill="#3b3550">
        {investigando && (
          <animate
            attributeName="cx"
            values="31;35;31"
            dur="1.6s"
            repeatCount="indefinite"
          />
        )}
      </circle>
      <circle cx="51" cy="48" r="3" fill="#3b3550">
        {investigando && (
          <animate
            attributeName="cx"
            values="49;53;49"
            dur="1.6s"
            repeatCount="indefinite"
          />
        )}
      </circle>
      {/* Sobrancelhas */}
      <path d={esquerda} stroke="#8a8199" strokeWidth="2.5" strokeLinecap="round" fill="none" />
      <path d={direita} stroke="#8a8199" strokeWidth="2.5" strokeLinecap="round" fill="none" />
      {/* Boca */}
      <path d={boca} stroke="#a8556b" strokeWidth="2.5" strokeLinecap="round" fill="none" />
      {/* Brincos de pérola */}
      <circle cx="17" cy="48" r="3" fill="#f6f2fb" />
      <circle cx="67" cy="48" r="3" fill="#f6f2fb" />
    </svg>
  );
}
