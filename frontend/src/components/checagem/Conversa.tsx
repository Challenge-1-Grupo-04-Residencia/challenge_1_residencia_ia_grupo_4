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
import { Icone } from "@/components/ui/Icone";
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

interface Props {
  /**
   * Mostra o balão de saudação enquanto não há conversa.
   *
   * A página inicial manda `false`: a faixa de abertura, logo acima, já diz a
   * mesma coisa com as mesmas palavras. Dois convites iguais, um embaixo do
   * outro, não convidam o dobro — só empurram a caixa de pergunta para fora da
   * primeira tela.
   */
  saudacao?: boolean;
  /**
   * Avisa que a conversa saiu do zero.
   *
   * Serve à página inicial, que recolhe a abertura e o feed quando a pessoa
   * manda a primeira mensagem: a partir dali a tela é um chat, e a apresentação
   * da Vera só ocuparia o lugar da resposta.
   */
  aoComecar?: () => void;
}

export function Conversa({ saudacao = true, aoComecar }: Props = {}) {
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [carregando, setCarregando] = useState(false);
  const [etapas, setEtapas] = useState<EtapaDoAndamento[]>([]);
  const [idChecagem, setIdChecagem] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const fimDaConversa = useRef<HTMLDivElement | null>(null);
  const parametros = useSearchParams();
  const consultaInicial = parametros.get("q");
  // Guarda a última consulta disparada, e não um "já disparou": a busca do topo
  // empurra `?q=` sem trocar de rota, então a tela não remonta. Com um booleano,
  // a segunda pergunta feita pela busca não acontecia — a pessoa digitava, dava
  // Enter e nada mudava.
  const ultimaConsulta = useRef<string | null>(null);

  function acrescentar(m: Mensagem) {
    setMensagens((anteriores) => [...anteriores, m]);
  }

  // Dispara uma vez só, na primeira mensagem. Chamar a cada mensagem faria a
  // página inicial recalcular layout a cada linha da conversa.
  const jaAvisou = useRef(false);
  useEffect(() => {
    if (mensagens.length > 0 && !jaAvisou.current) {
      jaAvisou.current = true;
      aoComecar?.();
    }
  }, [mensagens.length, aoComecar]);

  /**
   * Leva a conversa para o fim a cada mudança.
   *
   * Roda também a cada etapa do andamento, porque o bloco da investigação cresce
   * enquanto a Vera trabalha: sem isso a pessoa manda uma pergunta, a tela fica onde
   * estava e parece que nada aconteceu. `scroll-behavior` suave vem do CSS e é
   * desligado por `prefers-reduced-motion`.
   */
  useEffect(() => {
    // Sem conversa nenhuma não há o que acompanhar — e rolar aqui empurraria para
    // fora da tela a abertura da página inicial, onde esta conversa agora mora.
    if (mensagens.length === 0 && !carregando) return;

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
            : "Deu chabu aqui do meu lado. Tenta de novo, visse?",
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
            : "Deu chabu aqui do meu lado. Tenta de novo, visse?",
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
            : "Deu chabu aqui do meu lado. Tenta de novo, visse?",
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
    if (consultaInicial && ultimaConsulta.current !== consultaInicial) {
      ultimaConsulta.current = consultaInicial;
      void novaChecagem(consultaInicial);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [consultaInicial]);

  const vazio = mensagens.length === 0;

  return (
    <div className="mt-3 flex flex-col gap-4">
      {/* Só o rosto, e uma linha. A Vera inteira já está na abertura logo acima:
          repetir a arte aqui empurrava a caixa de texto para fora da primeira
          tela, que é justamente onde ela precisa estar. */}
      {vazio && saudacao && (
        <div className="surge flex items-start gap-3">
          <VeraAvatar humor="satisfeita" tamanho={48} />
          <div className="relative min-w-0 flex-1 rounded-lg border-[3px] border-tinta bg-papel-2 p-3 shadow-bloco-sm">
            <p className="text-base">
              <strong className="font-display text-xl">Senta aqui, meu bem!</strong>{" "}
              Cola a notícia aí embaixo que eu vou atrás.
            </p>
            {/* Rabicho apontando para a Vera. */}
            <span
              aria-hidden
              className="absolute -left-[13px] top-4 h-0 w-0 border-y-[10px] border-r-[13px] border-y-transparent border-r-tinta"
            />
            <span
              aria-hidden
              className="absolute -left-[8px] top-4 h-0 w-0 border-y-[8px] border-r-[10px] border-y-transparent border-r-[var(--papel-2)]"
            />
          </div>
        </div>
      )}

      <section className="flex flex-col gap-5" aria-live="polite">
        {mensagens.map((m, i) => {
          if (m.tipo === "pergunta") {
            return (
              <p
                key={i}
                className="surge max-w-[85%] self-end rounded-lg rounded-br-sm border-[3px] border-tinta bg-vermelho px-4 py-2.5 text-base font-semibold text-white shadow-bloco-sm"
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
                <VeraAvatar humor="pensativa" tamanho={48} className="mt-1" />
                <div className="min-w-0 flex-1 rounded-lg rounded-tl-sm border-[3px] border-tinta bg-papel-2 p-4 shadow-bloco-sm">
                  <p className="text-base">{m.texto}</p>
                  {m.fontes.length > 0 && (
                    <ul className="mt-2 space-y-1.5 text-sm">
                      {m.fontes.map((fonte) => (
                        <li key={fonte.url} className="flex items-baseline gap-2">
                          <span
                            className={`flex size-6 shrink-0 items-center justify-center rounded-total ${
                              fonte.confiavel
                                ? "bg-confirmada text-white"
                                : "border border-borda text-tinta-3"
                            }`}
                            title={
                              fonte.confiavel
                                ? "Veículo da base curada"
                                : "Fora da base curada"
                            }
                          >
                            <Icone nome={fonte.confiavel ? "visto" : "duvida"} tamanho={14} />
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
                                {fonte.veiculo}
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
              className="surge flex items-center gap-3 rounded-lg border-[3px] border-falsa bg-falsa-fundo p-4 text-base text-tinta"
            >
              <Icone nome="alerta" tamanho={28} className="shrink-0 text-falsa" />
              {m.texto}
            </p>
          );
        })}

        {/* Enquanto a Vera trabalha, o caminho é o conteúdo principal da tela: é o
            que responde "o que está acontecendo?" sem a pessoa ter de adivinhar. */}
        {carregando && etapas.length > 0 && (
          <div className="surge flex items-start gap-3">
            <VeraAvatar humor="investigando" tamanho={48} className="mt-1" />
            <div className="min-w-0 flex-1">
              <CaminhoDaInvestigacao etapas={etapas} />
            </div>
          </div>
        )}
        {carregando && etapas.length === 0 && (
          <p className="surge flex items-center gap-2 text-base text-tinta-2">
            <Icone nome="relogio" tamanho={22} className="etapa-ativa" />
            Já vou ver isso, meu bem…
          </p>
        )}

      </section>

      {/* `sticky` com `bottom`: a caixa ocupa o espaço dela no fim da conversa e só
          flutua quando a pessoa rola para cima. Deixá-la fora do fluxo, ou puxá-la com
          margem negativa, fazia a última mensagem, a que se quer ler, ficar escondida
          atrás dela.

          Com a conversa vazia ela **não** gruda: `bottom` puxa o elemento para cima
          dentro do próprio bloco, e numa página curta isso jogava a caixa por cima da
          Vera do estado vazio. Só há o que perseguir quando já existe conversa. */}
      <div
        className={`z-10 mt-2 ${
          vazio && !carregando ? "" : "sticky bottom-24 md:bottom-4"
        }`}
      >
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
