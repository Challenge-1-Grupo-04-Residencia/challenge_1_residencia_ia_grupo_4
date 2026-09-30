"use client";

/**
 * Feedback de carregamento em etapas (RF-03).
 *
 * O backend hoje responde só no fim, então as etapas avançam por tempo estimado em vez
 * de por evento real. É uma aproximação honesta enquanto não existe streaming: o
 * usuário precisa ver que a investigação anda, e a Vera leva até 20 s no pior caso.
 * Quando a API expuser progresso, trocar o temporizador pelo evento.
 */

import { useEffect, useState } from "react";

import { VeraAvatar } from "@/components/vera/VeraAvatar";
import { ETAPAS } from "@/lib/veracidade";
import type { Camada } from "@/types/checagem";

/** Tempo estimado de cada camada, alinhado com as metas de latência da documentação. */
const SEQUENCIA: Array<{ camada: Camada; ms: number }> = [
  { camada: "N0", ms: 400 },
  { camada: "N1", ms: 1800 },
  { camada: "N2", ms: 1200 },
  { camada: "N3", ms: 6000 },
  { camada: "N4", ms: 12000 },
];

export function Investigando() {
  const [indice, setIndice] = useState(0);

  useEffect(() => {
    if (indice >= SEQUENCIA.length - 1) return;
    const id = setTimeout(() => setIndice((i) => i + 1), SEQUENCIA[indice].ms);
    return () => clearTimeout(id);
  }, [indice]);

  return (
    <div
      className="rounded-2xl border border-violet-400/30 bg-violet-500/10 p-5"
      role="status"
      aria-live="polite"
    >
      <div className="flex items-center gap-4">
        <VeraAvatar humor="investigando" tamanho={56} className="shrink-0" />
        <div className="min-w-0">
          <p className="text-sm text-violet-100">{ETAPAS[SEQUENCIA[indice].camada]}</p>
          <ol className="mt-2 flex gap-1.5" aria-hidden>
            {SEQUENCIA.map((etapa, i) => (
              <li
                key={etapa.camada}
                className={`h-1 w-8 rounded-full transition-colors ${
                  i <= indice ? "bg-violet-400" : "bg-white/15"
                }`}
              />
            ))}
          </ol>
        </div>
      </div>
    </div>
  );
}
