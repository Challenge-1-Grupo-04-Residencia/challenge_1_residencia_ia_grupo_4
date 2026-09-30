/**
 * Cartão lateral: o que observar antes de acreditar, e o atalho para checar.
 *
 * Ensinar os sinais é o ponto do produto. A Vera existe para fortalecer o
 * pensamento crítico de quem pergunta, não para substituí-lo — alguém que
 * aprende a reconhecer um título alarmista precisa dela menos da próxima vez, e
 * isso é sucesso, não perda de uso.
 */

import Link from "next/link";

export function DicaDeSeguranca() {
  return (
    <aside className="flex flex-col gap-4 rounded-md bg-papel-rosa p-5 md:p-6">
      <h2 className="sr-only">O que olhar antes de acreditar numa notícia</h2>

      {/* Jornal com o carimbo de fake news. */}
      <div className="relative mx-auto w-full max-w-64" aria-hidden>
        <svg viewBox="0 0 160 120" className="w-full text-tinta">
          <rect
            x="14"
            y="10"
            width="120"
            height="100"
            rx="4"
            fill="var(--papel-2)"
            stroke="currentColor"
            strokeWidth="3"
            transform="rotate(-4 74 60)"
          />
          <g transform="rotate(-4 74 60)">
            <rect x="26" y="26" width="44" height="30" fill="currentColor" opacity="0.18" />
            <path
              d="M78 28h44M78 38h44M78 48h30M26 66h96M26 76h96M26 86h62"
              stroke="currentColor"
              strokeWidth="3"
              strokeLinecap="round"
              opacity="0.35"
            />
          </g>
          <g transform="rotate(6 110 46)">
            <rect x="72" y="32" width="76" height="26" rx="4" fill="var(--vermelho)" />
            <text
              x="110"
              y="50"
              textAnchor="middle"
              fill="#fff"
              fontSize="16"
              fontWeight="800"
              fontFamily="var(--fonte-display), sans-serif"
            >
              FAKE NEWS
            </text>
          </g>
        </svg>
      </div>

      <div className="flex gap-3 rounded-md bg-vermelho-suave p-4">
        <svg
          viewBox="0 0 24 24"
          className="size-7 shrink-0 text-vermelho"
          fill="currentColor"
          aria-hidden
        >
          <circle cx="12" cy="12" r="11" />
          <path d="M12 6.5v7" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" />
          <circle cx="12" cy="17.5" r="1.4" fill="#fff" />
        </svg>
        <p className="text-sm leading-relaxed text-tinta">
          Desconfia de manchete que grita, de texto que não diz de onde tirou e
          de quem te apressa pra repassar. É a pressa que faz a mentira viajar,
          visse?
        </p>
      </div>

      <Link
        href="/checar"
        className="pressiona flex items-center justify-center gap-2 rounded-total border-[3px] border-tinta bg-vermelho px-6 py-3 font-display text-lg font-bold text-white shadow-bloco-sm hover:bg-vermelho-forte"
      >
        Me manda uma notícia
        <svg viewBox="0 0 24 24" className="size-5" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden>
          <path d="M4 12h15m-6-6 6 6-6 6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </Link>
    </aside>
  );
}
