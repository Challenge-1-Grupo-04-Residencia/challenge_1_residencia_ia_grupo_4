"use client";

/**
 * Tela principal: o chat com a Senhora Vera.
 *
 * Mantém a conversa em memória do componente. Persistir o histórico entre sessões é
 * RF-42, que ainda não foi implementado — quando for, esta lista passa a vir do
 * backend em vez do estado local.
 */

import { useRef, useState } from "react";

import { CaixaDePergunta } from "@/components/checagem/CaixaDePergunta";
import { Investigando } from "@/components/checagem/Investigando";
import { ResultadoChecagem } from "@/components/checagem/ResultadoChecagem";
import { VeraAvatar } from "@/components/vera/VeraAvatar";
import { ErroDaVera, checar } from "@/lib/api";
import type { ChecagemResponse } from "@/types/checagem";

interface Troca {
  pergunta: string;
  resultado: ChecagemResponse | null;
  erro: string | null;
}

export default function Home() {
  const [trocas, setTrocas] = useState<Troca[]>([]);
  const [carregando, setCarregando] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  async function perguntar(texto: string) {
    // Uma pergunta nova cancela a anterior: a resposta antiga chegaria fora de ordem.
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setTrocas((anteriores) => [
      ...anteriores,
      { pergunta: texto, resultado: null, erro: null },
    ]);
    setCarregando(true);

    const ehUrl = /^https?:\/\/\S+$/.test(texto);

    try {
      const resultado = await checar(
        { texto, url: ehUrl ? texto : null },
        controller.signal,
      );
      setTrocas((anteriores) =>
        anteriores.map((t, i) =>
          i === anteriores.length - 1 ? { ...t, resultado } : t,
        ),
      );
    } catch (erro) {
      if (erro instanceof DOMException && erro.name === "AbortError") return;
      const mensagem =
        erro instanceof ErroDaVera
          ? erro.message
          : "Deu alguma coisa errada aqui. Tenta de novo?";
      setTrocas((anteriores) =>
        anteriores.map((t, i) =>
          i === anteriores.length - 1 ? { ...t, erro: mensagem } : t,
        ),
      );
    } finally {
      setCarregando(false);
    }
  }

  const vazio = trocas.length === 0;

  return (
    <main className="mx-auto flex min-h-dvh w-full max-w-2xl flex-col gap-6 px-4 py-10">
      <header className="text-center">
        <VeraAvatar humor="satisfeita" tamanho={96} className="mx-auto" />
        <h1 className="mt-3 text-2xl font-bold text-white">Senhora Vera</h1>
        <p className="mt-1 text-sm text-white/60">
          O que você quer saber que é verdade?
        </p>
      </header>

      {vazio && (
        <p className="rounded-2xl border border-white/10 bg-white/5 p-5 text-center text-sm text-white/70">
          Senta aqui, meu bem. Cola o link ou o texto que você recebeu, que eu vou
          conferir com as minhas fontes e te digo o que descobri — e de onde tirei.
        </p>
      )}

      <section className="flex flex-col gap-5" aria-live="polite">
        {trocas.map((troca, i) => (
          <div key={i} className="flex flex-col gap-3">
            <p className="self-end max-w-[85%] rounded-2xl rounded-br-sm bg-violet-500/20 px-4 py-2.5 text-sm text-white/90">
              {troca.pergunta}
            </p>

            {troca.resultado && <ResultadoChecagem resultado={troca.resultado} />}

            {troca.erro && (
              <p className="rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-100">
                {troca.erro}
              </p>
            )}

            {!troca.resultado && !troca.erro && carregando && <Investigando />}
          </div>
        ))}
      </section>

      <div className="sticky bottom-4 mt-auto">
        <CaixaDePergunta onPerguntar={perguntar} carregando={carregando} />
      </div>

      <footer className="text-center text-xs text-white/30">
        A Vera não afirma certeza absoluta. Confira sempre as fontes citadas.
      </footer>
    </main>
  );
}
