"use client";

/**
 * A conversa com a Vera: checagem (RF-01, RF-02) e perguntas de acompanhamento
 * sobre o resultado já entregue (RF-04).
 *
 * O histórico vive no estado do componente. Persistir entre sessões é RF-42, que
 * ainda não foi feito — quando for, esta lista passa a vir do backend.
 */

import { useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { CaixaDePergunta } from "@/components/checagem/CaixaDePergunta";
import { Investigando } from "@/components/checagem/Investigando";
import { ResultadoChecagem } from "@/components/checagem/ResultadoChecagem";
import { VeraAvatar } from "@/components/vera/VeraAvatar";
import { ErroDaVera, checar, perguntar } from "@/lib/api";
import { classificarEntrada } from "@/lib/entrada";
import type { ChecagemResponse } from "@/types/checagem";

type Mensagem =
  | { tipo: "pergunta"; texto: string }
  | { tipo: "veredito"; resultado: ChecagemResponse }
  | { tipo: "fala"; texto: string; fontes: string[] }
  | { tipo: "erro"; texto: string };

export function Conversa() {
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [carregando, setCarregando] = useState(false);
  const [idChecagem, setIdChecagem] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const parametros = useSearchParams();
  const consultaInicial = parametros.get("q");
  const jaDisparou = useRef(false);

  function acrescentar(m: Mensagem) {
    setMensagens((anteriores) => [...anteriores, m]);
  }

  async function novaChecagem(texto: string) {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    acrescentar({ tipo: "pergunta", texto });
    setCarregando(true);

    const { url } = classificarEntrada(texto);

    try {
      const resultado = await checar({ texto, url }, controller.signal);
      setIdChecagem(resultado.id);
      acrescentar({ tipo: "veredito", resultado });
    } catch (erro) {
      if (erro instanceof DOMException && erro.name === "AbortError") return;
      acrescentar({
        tipo: "erro",
        texto:
          erro instanceof ErroDaVera
            ? erro.message
            : "Deu chabu aqui do meu lado. Tenta de novo?",
      });
    } finally {
      setCarregando(false);
    }
  }

  async function acompanhamento(texto: string) {
    if (!idChecagem) return;

    acrescentar({ tipo: "pergunta", texto });
    setCarregando(true);

    try {
      const resposta = await perguntar(idChecagem, texto);
      acrescentar({
        tipo: "fala",
        texto: resposta.texto,
        fontes: resposta.fontes,
      });
    } catch (erro) {
      acrescentar({
        tipo: "erro",
        texto:
          erro instanceof ErroDaVera
            ? erro.message
            : "Deu chabu aqui do meu lado. Tenta de novo?",
      });
    } finally {
      setCarregando(false);
    }
  }

  /**
   * Depois do primeiro veredito, o campo passa a servir para perguntar sobre o
   * resultado. Uma entrada que parece link ou texto de notícia volta a ser
   * checagem nova: quem cola outra notícia quer checá-la, não discutir a
   * anterior.
   */
  function enviar(texto: string) {
    const { tipo } = classificarEntrada(texto);
    const ehNovaNoticia = tipo !== "afirmacao";

    if (idChecagem && !ehNovaNoticia) {
      void acompanhamento(texto);
    } else {
      void novaChecagem(texto);
    }
  }

  // A busca do topo empurra `?q=`; dispara uma vez só.
  useEffect(() => {
    if (consultaInicial && !jaDisparou.current) {
      jaDisparou.current = true;
      void novaChecagem(consultaInicial);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [consultaInicial]);

  const vazio = mensagens.length === 0;

  return (
    <div className="mt-6 flex flex-col gap-5">
      {vazio && (
        <div className="flex items-start gap-3">
          <VeraAvatar humor="satisfeita" tamanho={44} className="shrink-0" />
          <p className="rounded-lg rounded-tl-sm border border-borda bg-papel-2 p-4 text-base">
            Senta aqui, meu bem. O que é que tu quer saber que é verdade?
          </p>
        </div>
      )}

      <section className="flex flex-col gap-5" aria-live="polite">
        {mensagens.map((m, i) => {
          if (m.tipo === "pergunta") {
            return (
              <p
                key={i}
                className="max-w-[85%] self-end rounded-lg rounded-br-sm bg-vermelho px-4 py-2.5 text-base text-tinta"
              >
                {m.texto}
              </p>
            );
          }

          if (m.tipo === "veredito") {
            return <ResultadoChecagem key={i} resultado={m.resultado} />;
          }

          if (m.tipo === "fala") {
            return (
              <div key={i} className="flex items-start gap-3">
                <VeraAvatar humor="pensativa" tamanho={44} className="mt-1 shrink-0" />
                <div className="min-w-0 flex-1 rounded-lg rounded-tl-sm border border-borda bg-papel-2 p-4">
                  <p className="text-base">{m.texto}</p>
                  {m.fontes.length > 0 && (
                    <ul className="mt-2 space-y-1 text-sm">
                      {m.fontes.map((url) => (
                        <li key={url}>
                          <a
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="break-all text-vermelho underline decoration-dotted underline-offset-2"
                          >
                            {url}
                          </a>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            );
          }

          return (
            <p
              key={i}
              className="rounded-lg border border-falsa/40 bg-falsa-fundo p-4 text-base text-tinta"
            >
              {m.texto}
            </p>
          );
        })}

        {carregando && <Investigando />}
      </section>

      <div className="sticky bottom-24 mt-2 md:bottom-4">
        <CaixaDePergunta
          onPerguntar={enviar}
          carregando={carregando}
          modoAcompanhamento={idChecagem !== null}
        />
      </div>
    </div>
  );
}
