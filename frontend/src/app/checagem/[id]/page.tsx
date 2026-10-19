"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { ResultadoChecagem } from "@/components/checagem/ResultadoChecagem";
import { Icone } from "@/components/ui/Icone";
import { VeraAvatar } from "@/components/vera/VeraAvatar";
import { ErroDaVera, buscarChecagem } from "@/lib/api";
import type { ChecagemResponse } from "@/types/checagem";

export default function DetalheChecagemPage() {
  const params = useParams<{ id: string }>();
  const id = params?.id ?? "";

  const [resultado, setResultado] = useState<ChecagemResponse | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    if (!id) return;
    const controller = new AbortController();
    setCarregando(true);
    setErro(null);

    buscarChecagem(id, controller.signal)
      .then((dados) => {
        setResultado(dados);
      })
      .catch((e) => {
        if (e instanceof DOMException && e.name === "AbortError") return;
        setErro(
          e instanceof ErroDaVera
            ? e.message
            : "Não consegui recuperar essa checagem agora, meu bem.",
        );
      })
      .finally(() => {
        setCarregando(false);
      });

    return () => controller.abort();
  }, [id]);

  return (
    <div className="mx-auto w-full max-w-3xl px-4 py-8 md:px-8">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <Link
          href="/historico"
          className="inline-flex items-center gap-1.5 text-sm font-bold text-tinta-2 hover:text-vermelho"
        >
          <Icone nome="seta" tamanho={16} className="rotate-180" />
          Voltar ao histórico
        </Link>
        <Link
          href="/checar"
          className="pressiona inline-flex items-center gap-1.5 rounded-sm border-2 border-tinta bg-papel-2 px-3 py-1.5 text-sm font-bold text-tinta shadow-bloco-sm hover:bg-papel-3"
        >
          <Icone nome="lupa" tamanho={16} className="text-vermelho" />
          Nova checagem
        </Link>
      </div>

      {carregando && (
        <div className="painel flex items-center gap-4 p-6">
          <VeraAvatar humor="investigando" tamanho={56} />
          <p className="text-lg font-semibold text-tinta-2">
            Deixa eu puxar essa checagem do meu caderninho…
          </p>
        </div>
      )}

      {!carregando && erro && (
        <div className="painel flex flex-col gap-4 p-6">
          <div className="flex items-center gap-4">
            <VeraAvatar humor="pensativa" tamanho={56} />
            <p className="text-lg font-semibold text-tinta">{erro}</p>
          </div>
          <div>
            <Link
              href="/checar"
              className="pressiona inline-flex items-center gap-2 rounded-sm border-2 border-tinta bg-vermelho px-4 py-2 text-base font-bold text-white shadow-bloco-sm"
            >
              <Icone nome="lupa" tamanho={18} />
              Conferir uma notícia agora
            </Link>
          </div>
        </div>
      )}

      {!carregando && resultado && (
        <div className="flex flex-col gap-4">
          {resultado.trecho && (
            <div className="rounded-lg rounded-br-sm border-[3px] border-tinta bg-vermelho px-4 py-3 text-lg font-semibold text-white shadow-bloco-sm">
              {resultado.trecho}
            </div>
          )}
          <ResultadoChecagem resultado={resultado} />
        </div>
      )}
    </div>
  );
}

