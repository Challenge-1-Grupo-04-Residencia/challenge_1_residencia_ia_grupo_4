/**
 * Retrato ilustrado da Vera para o topo da página, no estilo do protótipo.
 *
 * É SVG inline em vez de imagem porque a expressão muda com o resultado da
 * checagem (RF-05): trocar de humor vira mudança de atributo, não download de
 * outro arquivo — o que importa na extensão e no celular.
 *
 * O avatar pequeno do chat é outro componente (`VeraAvatar`): aqui há detalhe
 * que só faz sentido em tamanho grande, e lá há legibilidade que só existe
 * simplificando.
 */

import type { HumorDaVera } from "@/lib/veracidade";

interface Props {
  humor?: HumorDaVera;
  tamanho?: number;
  className?: string;
}

/** Curva da boca por humor. */
const BOCA: Record<HumorDaVera, string> = {
  brava: "M 78 138 Q 100 126 122 138",
  desconfiada: "M 80 136 Q 100 131 120 137",
  pensativa: "M 80 135 Q 100 135 120 135",
  satisfeita: "M 78 132 Q 100 148 122 132",
  orgulhosa: "M 74 130 Q 100 154 126 130",
  investigando: "M 80 136 Q 100 133 120 138",
};

/** Sobrancelhas: franzidas para desconfiança e raiva, erguidas para alegria. */
const SOBRANCELHAS: Record<HumorDaVera, { e: string; d: string }> = {
  brava: { e: "M 62 88 L 88 97", d: "M 138 88 L 112 97" },
  desconfiada: { e: "M 62 94 L 88 86", d: "M 138 92 L 112 92" },
  pensativa: { e: "M 62 90 L 88 89", d: "M 138 90 L 112 89" },
  satisfeita: { e: "M 62 90 L 88 82", d: "M 138 90 L 112 82" },
  orgulhosa: { e: "M 62 88 L 88 79", d: "M 138 88 L 112 79" },
  investigando: { e: "M 62 93 L 88 84", d: "M 138 91 L 112 88" },
};

const DESCRICAO: Record<HumorDaVera, string> = {
  brava: "Senhora Vera com expressão brava",
  desconfiada: "Senhora Vera desconfiada, com uma sobrancelha erguida",
  pensativa: "Senhora Vera pensativa",
  satisfeita: "Senhora Vera sorrindo",
  orgulhosa: "Senhora Vera orgulhosa",
  investigando: "Senhora Vera investigando",
};

export function VeraIlustracao({
  humor = "desconfiada",
  tamanho = 300,
  className = "",
}: Props) {
  const { e, d } = SOBRANCELHAS[humor];

  return (
    <svg
      width={tamanho}
      height={tamanho}
      viewBox="0 0 200 200"
      role="img"
      aria-label={DESCRICAO[humor]}
      className={className}
    >
      <defs>
        <clipPath id="vera-corte">
          <circle cx="100" cy="100" r="100" />
        </clipPath>
      </defs>

      <g clipPath="url(#vera-corte)">
        {/* Ombros e vestido florido */}
        <path
          d="M 20 200 Q 30 158 100 152 Q 170 158 180 200 Z"
          fill="#2d3561"
          stroke="#1a1410"
          strokeWidth="3"
        />
        <circle cx="55" cy="182" r="6" fill="#e8504f" />
        <circle cx="82" cy="192" r="5" fill="#f2b6c0" />
        <circle cx="120" cy="188" r="6" fill="#e8504f" />
        <circle cx="148" cy="180" r="5" fill="#f2b6c0" />
        <circle cx="100" cy="176" r="4" fill="#f5d547" />

        {/* Pescoço */}
        <path d="M 84 138 L 84 160 L 116 160 L 116 138 Z" fill="#e8a06a" />

        {/* Cabelo grisalho: volume atrás e onda em cima */}
        <path
          d="M 38 104 Q 30 44 100 36 Q 170 44 162 104 Q 158 130 148 132 L 52 132 Q 42 130 38 104 Z"
          fill="#c7c2cc"
          stroke="#1a1410"
          strokeWidth="3"
        />
        <path
          d="M 52 72 Q 74 52 100 58 Q 126 52 148 72"
          fill="none"
          stroke="#9a94a3"
          strokeWidth="3"
          strokeLinecap="round"
        />

        {/* Rosto */}
        <ellipse
          cx="100"
          cy="106"
          rx="52"
          ry="56"
          fill="#f0a868"
          stroke="#1a1410"
          strokeWidth="3"
        />

        {/* Bochechas coradas */}
        <ellipse cx="66" cy="118" rx="12" ry="8" fill="#e8776a" opacity="0.45" />
        <ellipse cx="134" cy="118" rx="12" ry="8" fill="#e8776a" opacity="0.45" />

        {/* Sobrancelhas */}
        <path
          d={e}
          stroke="#7d7684"
          strokeWidth="5"
          strokeLinecap="round"
          fill="none"
        />
        <path
          d={d}
          stroke="#7d7684"
          strokeWidth="5"
          strokeLinecap="round"
          fill="none"
        />

        {/* Olhos */}
        <ellipse cx="78" cy="106" rx="11" ry="9" fill="#ffffff" stroke="#1a1410" strokeWidth="2.5" />
        <ellipse cx="122" cy="106" rx="11" ry="9" fill="#ffffff" stroke="#1a1410" strokeWidth="2.5" />
        <circle cx="80" cy="106" r="4.5" fill="#1a1410">
          {humor === "investigando" && (
            <animate attributeName="cx" values="76;84;76" dur="1.8s" repeatCount="indefinite" />
          )}
        </circle>
        <circle cx="124" cy="106" r="4.5" fill="#1a1410">
          {humor === "investigando" && (
            <animate attributeName="cx" values="120;128;120" dur="1.8s" repeatCount="indefinite" />
          )}
        </circle>

        {/* Nariz */}
        <path
          d="M 100 110 Q 96 122 103 124"
          fill="none"
          stroke="#c97f4a"
          strokeWidth="3"
          strokeLinecap="round"
        />

        {/* Boca */}
        <path
          d={BOCA[humor]}
          stroke="#a8384f"
          strokeWidth="4"
          strokeLinecap="round"
          fill="none"
        />

        {/* Brincos de pérola */}
        <circle cx="46" cy="116" r="6" fill="#fdf6ec" stroke="#1a1410" strokeWidth="2.5" />
        <circle cx="154" cy="116" r="6" fill="#fdf6ec" stroke="#1a1410" strokeWidth="2.5" />
      </g>
    </svg>
  );
}
