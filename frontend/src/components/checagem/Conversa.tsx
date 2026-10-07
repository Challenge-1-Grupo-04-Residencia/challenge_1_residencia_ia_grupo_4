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
import { CaminhoDaInvestigacao } from "@/components/checagem/CaminhoDaInvestigacao";
import { ResultadoChecagem } from "@/components/checagem/ResultadoChecagem";
import { VeraAvatar } from "@/components/vera/VeraAvatar";
import type { EtapaDoAndamento } from "@/lib/api";
import { ErroDaVera, checarComAndamento, perguntar, triar } from "@/lib/api";
import { classificarEntrada } from "@/lib/entrada";
import type { ChecagemResponse, FonteCitada } from "@/types/checagem";

type Mensagem =
  | { tipo: "pergunta"; texto: string }
  /** O caminho percorrido acompanha o veredito: é a primeira coisa que se pergunta. */
  | { tipo: "veredito"; resultado: ChecagemResponse; etapas: EtapaDoAndamento[] }
  | { tipo: "fala"; texto: string; fontes: FonteCitada[] }
  | { tipo: "erro"; texto: string };

export function Conversa() {
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [carregando, setCarregando] = useState(false);
  const [etapas, setEtapas] = useState<EtapaDoAndamento[]>([]);
  const [idChecagem, setIdChecagem] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const fimDaConversa = useRef<HTMLDivElement | null>(null);
  const parametros = useSearchParams();
  const consultaInicial = parametros.get("q");
  const jaDisparou = useRef(false);

  function acrescentar(m: Mensagem) {
    setMensagens((anteriores) => [...anteriores, m]);
  }

  /**
   * Leva a conversa para o fim a cada mudança.
   *
   * Roda também a cada etapa do andamento, porque o bloco da investigação cresce
   * enquanto a Vera trabalha: sem isso a pessoa manda uma pergunta, a tela fica onde
   * estava e parece que nada aconteceu. `scroll-behavior` suave vem do CSS e é
   * desligado por `prefers-reduced-motion`.
   */
  useEffect(() => {
    // `scrollIntoView` não obedece ao `scroll-behavior` do CSS, então a preferência de
    // movimento reduzido é checada aqui. Quem a marcou costuma ter enxaqueca
    // vestibular; rolagem suave é exatamente o que incomoda.
    const semMovimento = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;
    fimDaConversa.current?.scrollIntoView({
      block: "end",
      behavior: semMovimento ? "auto" : "smooth",
    });
  }, [mensagens, etapas, carregando]);

  async function novaChecagem(
    texto: string,
    opcoes: { jaRegistrouPergunta?: boolean } = {},
  ) {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    if (!opcoes.jaRegistrouPergunta) acrescentar({ tipo: "pergunta", texto });
    setCarregando(true);
    setEtapas([]);

    const { url } = classificarEntrada(texto);
    const percorridas: EtapaDoAndamento[] = [];

    try {
      const resultado = await checarComAndamento(
        { texto, url },
        (etapa) => {
          percorridas.push(etapa);
          setEtapas([...percorridas]);
        },
        controller.signal,
      );
      setIdChecagem(resultado.id);
      acrescentar({ tipo: "veredito", resultado, etapas: percorridas });
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
      setEtapas([]);
    }
  }

  async function acompanhamento(
    texto: string,
    opcoes: { jaRegistrouPergunta?: boolean } = {},
  ) {
    if (!idChecagem) return;

    if (!opcoes.jaRegistrouPergunta) acrescentar({ tipo: "pergunta", texto });
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
   * Decide o destino da mensagem perguntando à API (RF-01, RF-02, RF-04).
   *
   * A decisão **não** é tomada aqui. Era, e pelo número de palavras: qualquer
   * entrada com menos de 25 ia para o acompanhamento depois da primeira
   * checagem. Como quase toda alegação de fato é curta — "Lula jogou a bandeira
   * do Brasil no chão após votar" tem nove palavras —, o efeito era a Vera
   * responder "essa sua pergunta eu ainda não sei responder direito" a tudo o
   * que a pessoa mandasse depois da primeira mensagem.
   *
   * Quem sabe distinguir "por que você achou isso?" de "por que o governo vai
   * taxar o Pix em 15%?" é a triagem do núcleo, que olha marca de alegação e
   * tema reconhecido. A interface só obedece.
   */
  async function enviar(texto: string) {
    acrescentar({ tipo: "pergunta", texto });
    setCarregando(true);

    let natureza: string;
    let resposta: string | null;
    try {
      const triagem = await triar(texto, idChecagem !== null);
      natureza = triagem.natureza;
      resposta = triagem.resposta;
    } catch (erro) {
      acrescentar({
        tipo: "erro",
        texto:
          erro instanceof ErroDaVera
            ? erro.message
            : "Deu chabu aqui do meu lado. Tenta de novo?",
      });
      setCarregando(false);
      return;
    }

    setCarregando(false);

    if (natureza === "alegacao") {
      void novaChecagem(texto, { jaRegistrouPergunta: true });
      return;
    }
    if (natureza === "acompanhamento") {
      void acompanhamento(texto, { jaRegistrouPergunta: true });
      return;
    }
    // Saudação, conversa ou agradecimento: a fala já vem pronta do núcleo, sem
    // gastar busca externa nem modelo.
    acrescentar({ tipo: "fala", texto: resposta ?? "", fontes: [] });
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
                className="surge max-w-[85%] self-end rounded-lg rounded-br-sm bg-vermelho px-4 py-2.5 text-base text-white"
              >
                {m.texto}
              </p>
            );
          }

          if (m.tipo === "veredito") {
            return (
              <div key={i} className="flex flex-col gap-3">
                <CaminhoDaInvestigacao etapas={m.etapas} concluida />
                <ResultadoChecagem resultado={m.resultado} />
              </div>
            );
          }

          if (m.tipo === "fala") {
            return (
              <div key={i} className="surge flex items-start gap-3">
                <VeraAvatar humor="pensativa" tamanho={44} className="mt-1 shrink-0" />
                <div className="min-w-0 flex-1 rounded-lg rounded-tl-sm border border-borda bg-papel-2 p-4">
                  <p className="text-base">{m.texto}</p>
                  {m.fontes.length > 0 && (
                    <ul className="mt-2 space-y-1.5 text-sm">
                      {m.fontes.map((fonte) => (
                        <li key={fonte.url} className="flex items-baseline gap-2">
                          <span
                            className="shrink-0 text-xs"
                            title={
                              fonte.confiavel
                                ? "Veículo da base curada"
                                : "Fora da base curada"
                            }
                            aria-hidden
                          >
                            {fonte.confiavel ? "✓" : "·"}
                          </span>
                          <span className="min-w-0">
                            <a
                              href={fonte.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-vermelho underline decoration-dotted underline-offset-2 hover:decoration-solid"
                            >
                              {fonte.titulo}
                            </a>
                            {fonte.veiculo && (
                              <span className="ml-1.5 opacity-60">
                                — {fonte.veiculo}
                              </span>
                            )}
                          </span>
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
              className="surge rounded-lg border border-falsa/40 bg-falsa-fundo p-4 text-base text-tinta"
            >
              {m.texto}
            </p>
          );
        })}

        {/* Enquanto a Vera trabalha, o caminho é o conteúdo principal da tela: é o
            que responde "o que está acontecendo?" sem a pessoa ter de adivinhar. */}
        {carregando && etapas.length > 0 && (
          <div className="surge flex items-start gap-3">
            <VeraAvatar humor="investigando" tamanho={44} className="mt-1 shrink-0" />
            <div className="min-w-0 flex-1">
              <CaminhoDaInvestigacao etapas={etapas} />
            </div>
          </div>
        )}
        {carregando && etapas.length === 0 && (
          <p className="surge text-sm text-tinta-2">Já vou ver isso, meu bem…</p>
        )}

      </section>

      {/* `sticky` com `bottom`: a caixa ocupa o espaço dela no fim da conversa e só
          flutua quando a pessoa rola para cima. Deixá-la fora do fluxo, ou puxá-la com
          margem negativa, fazia a última mensagem — a que se quer ler — ficar escondida
          atrás dela. */}
      <div className="sticky bottom-24 z-10 mt-2 md:bottom-4">
        <CaixaDePergunta
          onPerguntar={enviar}
          carregando={carregando}
          modoAcompanhamento={idChecagem !== null}
        />
      </div>

      {/* Âncora da rolagem automática, **depois** da caixa de pergunta.
          Antes dela, o navegador parava com a última mensagem rente ao fim da janela —
          e a caixa, que é `sticky`, aterrissava justamente em cima dela. Rolando até
          aqui, a caixa fica inteira na tela e a mensagem acima dela também. */}
      <div ref={fimDaConversa} aria-hidden className="h-2 shrink-0" />
    </div>
  );
}
