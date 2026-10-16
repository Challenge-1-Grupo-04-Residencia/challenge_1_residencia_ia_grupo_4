"use client";

/**
 * Demonstração ao vivo dentro da apresentação.
 *
 * Não é mock: chama o pipeline real (`checarComAndamento`) e mostra o caminho da
 * investigação animado e o resultado, os mesmos componentes do chat. Serve para o slide
 * "veja a Vera trabalhando" simular um prompt de verdade na frente de quem assiste.
 *
 * Exige o backend no ar (e o Ollama, para a N4). Se cair, mostra o recado da Vera e a
 * apresentação segue normalmente. A demo é um extra e não trava o slide.
 */

import { useRef, useState } from "react";

import { CaminhoDaInvestigacao } from "@/components/checagem/CaminhoDaInvestigacao";
import { ResultadoChecagem } from "@/components/checagem/ResultadoChecagem";
import { Icone } from "@/components/ui/Icone";
import { VeraAvatar } from "@/components/vera/VeraAvatar";
import { ErroDaVera, checarComAndamento, type EtapaDoAndamento } from "@/lib/api";
import type { ChecagemResponse } from "@/types/checagem";

/** Prompts prontos: um boato conhecido e um fato, para a demo mostrar os dois lados. */
const EXEMPLOS = [
  "A vacina da Covid tem chip?",
  "O Brasil teve segundo turno nas eleições de 2026",
  "A Terra é plana e a Nasa esconde isso",
];

export function DemoAoVivo() {
  const [atual, setAtual] = useState<string | null>(null);
  const [etapas, setEtapas] = useState<EtapaDoAndamento[]>([]);
  const [carregando, setCarregando] = useState(false);
  const [resultado, setResultado] = useState<ChecagemResponse | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  async function rodar(texto: string) {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setAtual(texto);
    setResultado(null);
    setErro(null);
    setEtapas([]);
    setCarregando(true);

    const percorridas: EtapaDoAndamento[] = [];
    try {
      const r = await checarComAndamento(
        { texto },
        (etapa) => {
          percorridas.push(etapa);
          setEtapas([...percorridas]);
        },
        controller.signal,
      );
      setResultado(r);
    } catch (e) {
      if (e instanceof DOMException && e.name === "AbortError") return;
      setErro(
        e instanceof ErroDaVera
          ? e.message
          : "A demo precisa do motor no ar. Sobe o backend e tenta de novo, visse?",
      );
    } finally {
      setCarregando(false);
    }
  }

  return (
    <div className="flex w-full flex-col gap-4">
      {/* Prompts prontos: um toque dispara a checagem real. */}
      <div className="flex flex-wrap justify-center gap-2">
        {EXEMPLOS.map((exemplo) => (
          <button
            key={exemplo}
            type="button"
            onClick={() => rodar(exemplo)}
            disabled={carregando}
            className="pressiona flex min-h-11 items-center gap-1.5 rounded-total border-[3px] border-tinta bg-papel-2 px-4 text-base font-semibold text-tinta shadow-bloco-sm transition-colors hover:bg-vermelho-suave disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Icone nome="lupa" tamanho={20} className="text-vermelho" />
            {exemplo}
          </button>
        ))}
      </div>

      {/* A pergunta "digitada", como um balão do usuário. */}
      {atual && (
        <p className="surge max-w-[85%] self-end rounded-lg rounded-br-sm border-[3px] border-tinta bg-vermelho px-4 py-2.5 text-lg font-semibold text-white shadow-bloco-sm">
          {atual}
        </p>
      )}

      {/* Enquanto trabalha: avatar investigando + o placar das camadas, ao vivo. */}
      {carregando && (
        <div className="surge flex items-start gap-3">
          <VeraAvatar humor="investigando" tamanho={60} className="mt-1" />
          <div className="min-w-0 flex-1">
            <CaminhoDaInvestigacao
              etapas={
                etapas.length > 0
                  ? etapas
                  : [
                      {
                        tipo: "iniciou",
                        camada: "TRIAGEM",
                        mensagem: "Vendo o que é que tu me mandaste…",
                        sinais: [],
                      },
                    ]
              }
            />
          </div>
        </div>
      )}

      {/* O veredito, com o mesmo componente do chat. */}
      {resultado && (
        <div className="flex flex-col gap-3">
          <CaminhoDaInvestigacao etapas={etapas} concluida />
          <ResultadoChecagem resultado={resultado} />
        </div>
      )}

      {erro && (
        <p className="surge flex items-center gap-3 rounded-lg border-[3px] border-falsa bg-falsa-fundo p-4 text-lg text-tinta">
          <Icone nome="alerta" tamanho={35} className="shrink-0 text-falsa" />
          {erro}
        </p>
      )}

      {!atual && (
        <p className="text-center text-base text-tinta-3">
          Toca num exemplo e me vê trabalhar de verdade, meu bem.
        </p>
      )}
    </div>
  );
}
