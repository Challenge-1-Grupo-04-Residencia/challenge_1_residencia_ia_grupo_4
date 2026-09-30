"use client";

/**
 * Feed das últimas checagens (RF-43).
 *
 * Os dados vêm de `GET /api/v1/checagens/recentes`. O histórico do backend é em
 * memória por enquanto, então a lista zera quando o servidor reinicia — é por
 * isso que o estado vazio existe de verdade aqui, e não como enfeite.
 *
 * O feed serve a quem chega sem uma dúvida específica: ver o que já foi
 * desmentido é prevenção, que é mais barato do que checar depois de acreditar.
 */

import { useEffect, useState } from "react";

import { Selo } from "@/components/ui/Selo";
import { checagensRecentes } from "@/lib/api";
import type { ChecagemDoFeed } from "@/types/checagem";

/** "Hoje, 14:32" · "Ontem, 18:45" · "27/09, 09:10" */
function quando(iso: string): string {
  const data = new Date(iso);
  if (Number.isNaN(data.getTime())) return "";

  const hora = data.toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });

  const hoje = new Date();
  const mesmoDia = (a: Date, b: Date) =>
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate();

  const ontem = new Date(hoje);
  ontem.setDate(hoje.getDate() - 1);

  if (mesmoDia(data, hoje)) return `Hoje, ${hora}`;
  if (mesmoDia(data, ontem)) return `Ontem, ${hora}`;

  return `${data.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" })}, ${hora}`;
}

export function UltimasChecagens() {
  const [checagens, setChecagens] = useState<ChecagemDoFeed[] | null>(null);

  useEffect(() => {
    let ativo = true;
    checagensRecentes(6).then((lista) => {
      if (ativo) setChecagens(lista);
    });
    return () => {
      ativo = false;
    };
  }, []);

  return (
    <section className="rounded-md bg-papel-2 p-5 shadow-card md:p-6">
      <header className="flex items-baseline justify-between gap-3">
        <h2 className="font-display text-xl font-bold">O que eu já conferi</h2>
        <a
          href="/historico"
          className="text-sm font-semibold text-tinta-2 hover:text-vermelho"
        >
          Ver tudo →
        </a>
      </header>

      {checagens === null && (
        <p className="mt-6 text-sm text-tinta-3">Deixa eu ver o que eu já conferi…</p>
      )}

      {checagens?.length === 0 && (
        <div className="mt-6 rounded-md border border-dashed border-borda p-6 text-center">
          <p className="text-base text-tinta-2">
            Tô meio borocoxô: ainda não me trouxeram nada hoje.
          </p>
          <p className="mt-1 text-sm text-tinta-3">
            Me manda uma notícia lá em cima que eu vou atrás na hora.
          </p>
        </div>
      )}

      {checagens && checagens.length > 0 && (
        <ul className="mt-4 divide-y divide-borda">
          {checagens.map((c, i) => (
            // Escalonar a entrada faz a lista "cair" em cascata, o que deixa
            // claro que são itens separados e chegaram juntos.
            <li
              key={c.id}
              className="surge"
              style={{ "--atraso": `${i * 60}ms` } as React.CSSProperties}
            >
              <a
                href={`/checagem/${c.id}`}
                className="flex items-start gap-4 py-4 hover:bg-papel-3"
              >
                <div className="min-w-0 flex-1">
                  <Selo faixa={c.faixa} />
                  <p className="mt-2 text-base font-semibold leading-snug">
                    {c.trecho}
                  </p>
                  <p className="mt-1 text-sm text-tinta-3">
                    {quando(c.checada_em)}
                    {c.exibe_porcentagem && c.veracidade !== null && (
                      <> · {Math.round(c.veracidade)}% de veracidade</>
                    )}
                  </p>
                </div>

                <svg
                  viewBox="0 0 24 24"
                  className="mt-6 size-5 shrink-0 text-tinta-3"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  aria-hidden
                >
                  <path d="m9 5 7 7-7 7" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </a>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
