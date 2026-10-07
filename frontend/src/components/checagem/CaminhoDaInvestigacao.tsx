"use client";

/**
 * O caminho da investigação, etapa por etapa (RF-03).
 *
 * Substitui a barrinha de progresso por tempo estimado. Aquela avançava em 400 ms,
 * 1,8 s, 1,2 s, 6 s e 12 s, sem relação com o que estava acontecendo: a camada de
 * busca leva de 1 a 25 s e a de inferência depende de um modelo externo. Num produto
 * cujo valor é a explicação, inventar o andamento é inventar parte do produto.
 *
 * Fica na tela **depois** do veredito também, recolhido. É a pergunta que o usuário faz
 * primeiro — "como é que tu chegaste nisso?" — e a resposta é o caminho percorrido.
 *
 * Três coisas carregam o estado de cada etapa, porque cor sozinha não serve a quem tem
 * daltonia: o símbolo, o texto do rótulo e, na etapa em curso, o movimento.
 */

import { useEffect, useRef, useState } from "react";

import type { EtapaDoAndamento } from "@/lib/api";
import type { Camada, Sinal } from "@/types/checagem";

/** As etapas, na ordem em que a Vera as percorre. */
const ETAPAS: Array<{ camada: Camada; titulo: string; oQueFaz: string }> = [
  { camada: "TRIAGEM", titulo: "Entendendo o pedido", oQueFaz: "é notícia ou é conversa?" },
  { camada: "N2", titulo: "Lendo o texto", oQueFaz: "o jeito que foi escrito" },
  { camada: "N3", titulo: "Procurando quem publicou", oQueFaz: "outros veículos e checagens" },
  { camada: "N4", titulo: "Conferindo o conteúdo", oQueFaz: "o que as fontes dizem" },
];

type Estado = "pendente" | "fazendo" | "feita" | "pulada";

export interface Props {
  etapas: EtapaDoAndamento[];
  /** Quando a investigação acabou, o caminho vira resumo recolhível. */
  concluida?: boolean;
}

function estadoDe(camada: Camada, etapas: EtapaDoAndamento[]): Estado {
  const minhas = etapas.filter((e) => e.camada === camada);
  if (minhas.some((e) => e.tipo === "pulou")) return "pulada";
  if (minhas.some((e) => e.tipo === "concluiu")) return "feita";
  if (minhas.some((e) => e.tipo === "iniciou")) return "fazendo";
  return "pendente";
}

function mensagemDe(camada: Camada, etapas: EtapaDoAndamento[]): string {
  const minhas = etapas.filter((e) => e.camada === camada && e.mensagem);
  return minhas.length > 0 ? minhas[minhas.length - 1].mensagem : "";
}

function sinaisDe(camada: Camada, etapas: EtapaDoAndamento[]): Sinal[] {
  return etapas
    .filter((e) => e.camada === camada)
    .flatMap((e) => e.sinais ?? []);
}

const SIMBOLO: Record<Estado, string> = {
  pendente: "",
  fazendo: "",
  feita: "✓",
  pulada: "–",
};

const ROTULO_DE_ESTADO: Record<Estado, string> = {
  pendente: "ainda não",
  fazendo: "agora",
  feita: "pronto",
  pulada: "não precisou",
};

export function CaminhoDaInvestigacao({ etapas, concluida = false }: Props) {
  const [aberto, setAberto] = useState(!concluida);
  const jaConcluiu = useRef(false);

  // Recolhe sozinho quando o veredito chega: durante a investigação o caminho é o
  // conteúdo principal; depois, o conteúdo principal é o resultado.
  useEffect(() => {
    if (concluida && !jaConcluiu.current) {
      jaConcluiu.current = true;
      setAberto(false);
    }
  }, [concluida]);

  const feitas = ETAPAS.filter((e) => estadoDe(e.camada, etapas) === "feita").length;

  return (
    <div
      className="rounded-md border border-borda bg-papel-2 p-4"
      role="status"
      aria-live="polite"
    >
      <button
        type="button"
        onClick={() => setAberto((a) => !a)}
        className="flex w-full items-center justify-between gap-3 text-left"
        aria-expanded={aberto}
      >
        <span className="font-display text-sm font-semibold">
          {concluida ? "O caminho que eu fiz" : "Investigando…"}
        </span>
        <span className="text-xs text-tinta-2">
          {feitas} de {ETAPAS.length} etapas {aberto ? "▲" : "▼"}
        </span>
      </button>

      {aberto && (
        <ol className="mt-3 space-y-0">
          {ETAPAS.map((etapa, i) => {
            const estado = estadoDe(etapa.camada, etapas);
            const mensagem = mensagemDe(etapa.camada, etapas);
            const sinais = sinaisDe(etapa.camada, etapas);
            const medidos = sinais.filter((s) => s.score !== null);
            const ultima = i === ETAPAS.length - 1;

            return (
              <li key={etapa.camada} className="flex gap-3">
                {/* Marcador e trilha: a coluna da esquerda desenha o percurso. */}
                <div className="flex w-5 shrink-0 flex-col items-center">
                  <span
                    className={[
                      "mt-0.5 flex size-5 items-center justify-center rounded-total text-[11px] font-bold",
                      estado === "feita" && "bg-confirmada text-white",
                      estado === "fazendo" && "etapa-ativa bg-vermelho text-white",
                      estado === "pendente" && "border border-borda bg-papel-3 text-tinta-3",
                      estado === "pulada" && "bg-papel-3 text-tinta-3",
                    ]
                      .filter(Boolean)
                      .join(" ")}
                    aria-hidden
                  >
                    {SIMBOLO[estado]}
                  </span>
                  {!ultima && (
                    <span
                      className={[
                        "w-0.5 flex-1",
                        estado === "feita" ? "trilha-feita bg-confirmada" : "bg-borda",
                      ].join(" ")}
                      aria-hidden
                    />
                  )}
                </div>

                <div className={`min-w-0 flex-1 ${ultima ? "pb-0" : "pb-4"}`}>
                  <p className="text-sm font-semibold">
                    {etapa.titulo}
                    <span className="ml-2 text-xs font-normal text-tinta-3">
                      {ROTULO_DE_ESTADO[estado]}
                    </span>
                  </p>
                  <p className="text-xs text-tinta-2">
                    {mensagem || etapa.oQueFaz}
                  </p>
                  {medidos.length > 0 && (
                    <ul className="mt-1 flex flex-wrap gap-1">
                      {medidos.map((s) => (
                        <li
                          key={s.id}
                          className="rounded-sm bg-papel-3 px-1.5 py-0.5 text-[11px] text-tinta-2"
                          title={s.justificativa}
                        >
                          {s.nome.length > 28 ? `${s.nome.slice(0, 28)}…` : s.nome}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </li>
            );
          })}
        </ol>
      )}
    </div>
  );
}
