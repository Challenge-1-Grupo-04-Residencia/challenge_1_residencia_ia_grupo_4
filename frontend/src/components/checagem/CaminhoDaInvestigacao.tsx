"use client";

/**
 * O caminho da investigação, como um placar de carimbos (RF-03).
 *
 * Substitui a barrinha de progresso por tempo estimado. Aquela avançava em 400 ms,
 * 1,8 s, 1,2 s, 6 s e 12 s, sem relação com o que estava acontecendo: a camada de
 * busca leva de 1 a 25 s e a de inferência depende de um modelo externo. Num produto
 * cujo valor é a explicação, inventar o andamento é inventar parte do produto.
 *
 * ## Por que virou placar
 *
 * Era uma lista vertical com título, estado escrito, descrição e os nomes técnicos dos
 * sinais aparecendo um a um — quatro linhas de texto para dizer "estou trabalhando".
 * Agora são quatro quadros lado a lado, cada um com um pictograma, três palavras e um
 * carimbo quando fica pronto, mais o placar "3 de 4". É o único lugar do produto onde
 * cabe gamificar: a espera (ver skill `vera-gamificacao`).
 *
 * Três coisas carregam o estado de cada etapa, porque cor sozinha não serve a quem tem
 * daltonia: o pictograma, a palavra escrita e, na etapa em curso, o movimento.
 */

import { useEffect, useRef, useState } from "react";

import { Icone, type NomeDoIcone } from "@/components/ui/Icone";
import type { EtapaDoAndamento } from "@/lib/api";
import type { Camada, Sinal } from "@/types/checagem";

/** As etapas, na ordem em que a Vera as percorre. Nome com até três palavras. */
const ETAPAS: Array<{ camada: Camada; titulo: string; icone: NomeDoIcone; oQueFaz: string }> = [
  {
    camada: "TRIAGEM",
    titulo: "Vendo o pedido",
    icone: "conversa",
    oQueFaz: "é notícia ou é conversa?",
  },
  {
    camada: "N2",
    titulo: "Lendo o texto",
    icone: "texto",
    oQueFaz: "o jeito que foi escrito",
  },
  {
    camada: "N3",
    titulo: "Procurando nos jornais",
    icone: "jornal",
    oQueFaz: "outros veículos e checagens",
  },
  {
    camada: "N4",
    titulo: "Conferindo frase a frase",
    icone: "lupa",
    oQueFaz: "o que as fontes dizem",
  },
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
  return etapas.filter((e) => e.camada === camada).flatMap((e) => e.sinais ?? []);
}

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
      className="rounded-md border-[3px] border-tinta bg-papel-2 p-3 shadow-bloco-sm"
      role="status"
      aria-live="polite"
    >
      <button
        type="button"
        onClick={() => setAberto((a) => !a)}
        className="flex min-h-11 w-full items-center justify-between gap-3 text-left"
        aria-expanded={aberto}
      >
        <span className="flex items-center gap-2">
          <Icone nome={concluida ? "visto" : "lupa"} tamanho={22} />
          <span className="font-display text-xl">
            {concluida ? "O caminho que eu fiz" : "Tô atrás disso…"}
          </span>
        </span>
        <span className="flex shrink-0 items-center gap-2">
          {/* O placar em caixinhas: dá para contar sem ler. */}
          <span className="flex gap-1" aria-hidden>
            {ETAPAS.map((e, i) => (
              <span
                key={e.camada}
                className={`size-3 rounded-sm border-2 border-tinta ${
                  i < feitas ? "bg-confirmada" : "bg-papel-3"
                }`}
              />
            ))}
          </span>
          <span className="font-display text-lg tabular-nums">
            {feitas}/{ETAPAS.length}
          </span>
          <Icone nome="seta" tamanho={18} className={aberto ? "-rotate-90" : "rotate-90"} />
        </span>
      </button>

      {aberto && (
        <ol className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
          {ETAPAS.map((etapa) => {
            const estado = estadoDe(etapa.camada, etapas);
            const mensagem = mensagemDe(etapa.camada, etapas);
            const medidos = sinaisDe(etapa.camada, etapas).filter((s) => s.score !== null);

            return (
              <li
                key={etapa.camada}
                className={[
                  "relative flex flex-col items-center gap-1 rounded-md border-2 p-2 text-center",
                  estado === "feita" && "border-confirmada bg-verdadeira-fundo",
                  estado === "fazendo" && "border-vermelho bg-vermelho-suave",
                  estado === "pendente" && "border-borda bg-papel-3 opacity-60",
                  estado === "pulada" && "border-borda bg-papel-3 opacity-60",
                ]
                  .filter(Boolean)
                  .join(" ")}
                title={mensagem || etapa.oQueFaz}
              >
                <Icone
                  nome={etapa.icone}
                  tamanho={28}
                  className={estado === "fazendo" ? "etapa-ativa" : undefined}
                />
                <span className="text-xs font-bold leading-tight">{etapa.titulo}</span>
                <span className="text-[11px] text-tinta-2">
                  {ROTULO_DE_ESTADO[estado]}
                  {/* Quantos sinais saíram dali: é o que a etapa rendeu, em número,
                      sem despejar o nome técnico de cada um na cara de quem espera. */}
                  {estado === "feita" && medidos.length > 0 && ` · ${medidos.length}`}
                </span>

                {estado === "feita" && (
                  <span
                    className="bate-carimbo absolute -right-1.5 -top-1.5 flex size-6 items-center justify-center rounded-total border-2 border-tinta bg-confirmada text-white"
                    aria-hidden
                  >
                    <Icone nome="visto" tamanho={14} />
                  </span>
                )}
              </li>
            );
          })}
        </ol>
      )}
    </div>
  );
}
