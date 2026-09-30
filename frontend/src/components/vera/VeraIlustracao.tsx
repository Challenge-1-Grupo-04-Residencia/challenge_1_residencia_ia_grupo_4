/**
 * Retrato da Vera para a abertura da página.
 *
 * A pose é a do protótipo: mão no queixo, olhar de canto, meio sorriso de quem
 * já desconfiou. É a postura que define a personagem — ela não está assustada
 * com a notícia, está avaliando. Uma Vera de olhos arregalados passaria a
 * mensagem errada: quem checa fatos não se apavora, examina.
 *
 * SVG inline em vez de imagem porque a expressão muda com o resultado da
 * checagem (RF-05): trocar de humor vira mudança de atributo, não download.
 */

import type { HumorDaVera } from "@/lib/veracidade";

interface Props {
  humor?: HumorDaVera;
  tamanho?: number;
  className?: string;
  /** Para passar `--atraso` na orquestração de entrada. */
  style?: React.CSSProperties;
}

/** Boca por humor. O padrão é um meio sorriso puxado para um lado. */
const BOCA: Record<HumorDaVera, string> = {
  brava: "M 86 150 Q 104 140 122 152",
  desconfiada: "M 86 148 Q 106 152 124 143",
  pensativa: "M 88 148 Q 106 149 122 147",
  satisfeita: "M 84 144 Q 104 160 124 143",
  orgulhosa: "M 80 142 Q 104 166 128 141",
  investigando: "M 88 149 Q 106 153 122 145",
};

/**
 * Sobrancelhas. A direita erguida é a marca da Vera desconfiada — é o gesto que
 * comunica "eu tô achando essa história estranha" sem uma palavra.
 */
const SOBRANCELHAS: Record<HumorDaVera, { e: string; d: string }> = {
  brava: { e: "M 68 96 Q 82 90 94 99", d: "M 142 96 Q 128 90 116 99" },
  desconfiada: { e: "M 68 98 Q 82 92 94 96", d: "M 144 86 Q 130 78 116 86" },
  pensativa: { e: "M 68 95 Q 82 90 94 94", d: "M 142 95 Q 128 90 116 94" },
  satisfeita: { e: "M 68 94 Q 82 86 94 92", d: "M 142 94 Q 128 86 116 92" },
  orgulhosa: { e: "M 68 92 Q 82 83 94 90", d: "M 142 92 Q 128 83 116 90" },
  investigando: { e: "M 68 97 Q 82 90 94 95", d: "M 143 88 Q 129 80 116 88" },
};

/** Deslocamento da pupila: olhar de canto na maioria dos humores. */
const OLHAR: Record<HumorDaVera, number> = {
  brava: 0,
  desconfiada: 3.5,
  pensativa: 2.5,
  satisfeita: 0,
  orgulhosa: 0,
  investigando: 3,
};

const DESCRICAO: Record<HumorDaVera, string> = {
  brava: "Senhora Vera de cenho franzido, contrariada",
  desconfiada: "Senhora Vera com uma sobrancelha erguida, desconfiada",
  pensativa: "Senhora Vera pensativa, com a mão no queixo",
  satisfeita: "Senhora Vera sorrindo, satisfeita",
  orgulhosa: "Senhora Vera com um sorriso largo, orgulhosa",
  investigando: "Senhora Vera investigando, olhando de canto",
};

export function VeraIlustracao({
  humor = "desconfiada",
  tamanho = 300,
  className = "",
  style,
}: Props) {
  const { e, d } = SOBRANCELHAS[humor];
  const olhar = OLHAR[humor];

  return (
    <svg
      width={tamanho}
      height={tamanho}
      viewBox="0 0 220 220"
      role="img"
      aria-label={DESCRICAO[humor]}
      className={className}
      style={style}
    >
      <g stroke="#1a1410" strokeWidth="3.5" strokeLinejoin="round">
        {/* Ombros e vestido florido */}
        <path d="M 22 220 Q 34 178 78 168 L 142 168 Q 186 178 198 220 Z" fill="#3a3f7a" />
        <g stroke="none">
          <circle cx="58" cy="198" r="7" fill="#e8504f" />
          <circle cx="84" cy="210" r="5.5" fill="#f5b8c4" />
          <circle cx="132" cy="204" r="6.5" fill="#e8504f" />
          <circle cx="160" cy="194" r="5" fill="#f5b8c4" />
          <circle cx="106" cy="192" r="4.5" fill="#f5d547" />
          <circle cx="44" cy="214" r="4" fill="#f5d547" />
        </g>

        {/* Pescoço */}
        <path d="M 88 148 L 88 172 Q 110 182 132 172 L 132 148 Z" fill="#e09355" stroke="none" />

        {/* Cabelo: volume grisalho com a onda puxada para cima */}
        <path
          d="M 42 112 Q 32 46 110 38 Q 188 46 178 112 Q 176 136 166 142 Q 168 96 146 78 Q 122 92 92 82 Q 62 92 54 142 Q 44 136 42 112 Z"
          fill="#cfcad6"
        />
        <path d="M 62 66 Q 88 44 110 52" fill="none" stroke="#a49dae" strokeWidth="3.5" strokeLinecap="round" />
        <path d="M 124 48 Q 152 54 166 76" fill="none" stroke="#a49dae" strokeWidth="3.5" strokeLinecap="round" />

        {/* Rosto */}
        <ellipse cx="110" cy="114" rx="56" ry="58" fill="#f0a868" />

        {/* Bochechas */}
        <g stroke="none">
          <ellipse cx="72" cy="128" rx="13" ry="9" fill="#e07a63" opacity="0.4" />
          <ellipse cx="148" cy="128" rx="13" ry="9" fill="#e07a63" opacity="0.4" />
        </g>

        {/* Pálpebras superiores dão o olhar de quem está avaliando */}
        <path d={e} fill="none" stroke="#8b8494" strokeWidth="5.5" strokeLinecap="round" />
        <path d={d} fill="none" stroke="#8b8494" strokeWidth="5.5" strokeLinecap="round" />

        <g strokeWidth="3">
          <ellipse cx="84" cy="112" rx="13" ry="10" fill="#ffffff" />
          <ellipse cx="136" cy="112" rx="13" ry="10" fill="#ffffff" />
        </g>
        <g stroke="none" fill="#1a1410">
          <circle cx={84 + olhar} cy="112" r="5.5">
            {humor === "investigando" && (
              <animate attributeName="cx" values="80;90;80" dur="2.2s" repeatCount="indefinite" />
            )}
          </circle>
          <circle cx={136 + olhar} cy="112" r="5.5">
            {humor === "investigando" && (
              <animate attributeName="cx" values="132;142;132" dur="2.2s" repeatCount="indefinite" />
            )}
          </circle>
        </g>

        {/* Nariz */}
        <path d="M 110 116 Q 104 132 113 135" fill="none" stroke="#c9763f" strokeWidth="3.5" strokeLinecap="round" />

        {/* Boca */}
        <path d={BOCA[humor]} fill="none" stroke="#b03e56" strokeWidth="4.5" strokeLinecap="round" />

        {/* Mão no queixo: o gesto de quem está avaliando a história */}
        <path
          d="M 132 176 Q 150 172 158 156 Q 162 146 155 143 Q 148 141 145 150 Q 143 158 134 160 Z"
          fill="#f0a868"
        />
        <path d="M 147 152 Q 152 148 156 150" fill="none" stroke="#c9763f" strokeWidth="2.5" strokeLinecap="round" />

        {/* Brincos de pérola */}
        <circle cx="52" cy="126" r="7" fill="#fdf6ec" />
        <circle cx="168" cy="126" r="7" fill="#fdf6ec" />
      </g>
    </svg>
  );
}
