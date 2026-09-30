"use client";

/**
 * O veredito, como um balão de fala da Vera (RF-02, RF-05, RF-32).
 *
 * Três regras moldam este componente:
 *
 * - **RN-05** — todo resultado mostra porcentagem, faixa, principais sinais e fontes.
 *   Resultado sem explicação não é exibido.
 * - **RN-11** — a frase da Vera acompanha o dado técnico e nunca o substitui: se o
 *   humor tomasse o lugar do número, a Vera viraria entretenimento.
 * - **RN-03** — opinião e sátira não recebem porcentagem.
 *
 * O balão fala em linguagem simples, sem jargão (RF-02). O vocabulário técnico vive no
 * detalhamento, que abre a um clique (RF-33).
 */

import { useState } from "react";

import { DetalheSinais } from "@/components/checagem/DetalheSinais";
import { VeraAvatar } from "@/components/vera/VeraAvatar";
import { explicarEmLinguagemSimples } from "@/lib/linguagem";
import { ROTULO_DIFICULDADE, estiloDaFaixa, rotuloDeConfianca } from "@/lib/veracidade";
import type { ChecagemResponse } from "@/types/checagem";

interface Props {
  resultado: ChecagemResponse;
}

export function ResultadoChecagem({ resultado }: Props) {
  const [detalhado, setDetalhado] = useState(false);
  const estilo = estiloDaFaixa(resultado.faixa);
  const mostraPorcentagem =
    resultado.exibe_porcentagem && resultado.veracidade !== null;

  // A fala em linguagem simples é a preferida; se nenhum sinal tem tradução, cai na
  // explicação vinda da API, para o balão nunca aparecer sem conteúdo (RN-05).
  const emLinguagemSimples = explicarEmLinguagemSimples(resultado.principais_sinais);
  const corpo = emLinguagemSimples || resultado.explicacao;

  return (
    <article className="flex gap-3">
      <VeraAvatar humor={estilo.humor} tamanho={44} className="mt-1 shrink-0" />

      <div className={`min-w-0 flex-1 rounded-2xl rounded-tl-sm border p-4 ${estilo.cor}`}>
        {/* A frase da persona vem primeiro, mas o dado técnico vem logo abaixo, nunca
            no lugar dela (RN-11). */}
        <p className="text-base">{estilo.frase}</p>

        <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1">
          <span className="text-sm font-semibold">{resultado.faixa}</span>
          {mostraPorcentagem && (
            <span className="text-2xl font-bold tabular-nums">
              {Math.round(resultado.veracidade!)}%
            </span>
          )}
        </div>

        {mostraPorcentagem && (
          <div
            className="mt-2 h-2 w-full overflow-hidden rounded-full bg-black/30"
            role="meter"
            aria-valuenow={Math.round(resultado.veracidade!)}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label="Score de veracidade"
          >
            <div
              className={`h-full rounded-full transition-all duration-700 ${estilo.barra}`}
              style={{ width: `${resultado.veracidade}%` }}
            />
          </div>
        )}

        {/* Quando uma regra de negócio decidiu, ela explica por que o resultado
            publicado não bate com a média dos sinais. Sem isso o número não fecha. */}
        {resultado.regra_aplicada && resultado.explicacao && (
          <p className="mt-3 rounded-lg border border-white/20 bg-black/20 p-3 text-sm">
            {resultado.explicacao}
          </p>
        )}

        {corpo && <p className="mt-3 text-sm opacity-90">{corpo}</p>}

        {resultado.documentos_relacionados.length > 0 && (
          <section className="mt-3">
            <h4 className="text-xs font-semibold uppercase tracking-wide opacity-60">
              Quem mais publicou
            </h4>
            <ul className="mt-1.5 space-y-1 text-sm">
              {resultado.documentos_relacionados.map((doc, i) => (
                <li key={doc.url ?? i} className="flex items-baseline gap-2">
                  <span
                    className="shrink-0 text-xs"
                    title={doc.fonte_confiavel ? "Veículo da base curada" : "Fora da base curada"}
                    aria-hidden
                  >
                    {doc.fonte_confiavel ? "✓" : "·"}
                  </span>
                  {doc.url ? (
                    <a
                      href={doc.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="underline decoration-dotted underline-offset-2 hover:decoration-solid"
                    >
                      {doc.titulo || doc.fonte}
                    </a>
                  ) : (
                    <span>{doc.titulo}</span>
                  )}
                </li>
              ))}
            </ul>
          </section>
        )}

        <dl className="mt-3 flex flex-wrap gap-x-5 gap-y-1 text-xs opacity-60">
          <div>
            <dt className="inline">O quanto eu tenho certeza: </dt>
            <dd className="inline font-medium">
              {rotuloDeConfianca(resultado.confianca)}
            </dd>
          </div>
          <div>
            <dt className="inline">O que consegui apurar: </dt>
            <dd className="inline font-medium">
              {Math.round(resultado.cobertura * 100)}%
            </dd>
          </div>
          <div>
            <dt className="inline">Dificuldade: </dt>
            <dd className="inline font-medium">
              {ROTULO_DIFICULDADE[resultado.dificuldade]}
            </dd>
          </div>
        </dl>

        <button
          type="button"
          onClick={() => setDetalhado((v) => !v)}
          aria-expanded={detalhado}
          className="mt-3 text-xs underline decoration-dotted underline-offset-2 opacity-70 hover:opacity-100"
        >
          {detalhado
            ? "Esconder as contas"
            : "Ver as contas: sinal por sinal, com o peso de cada um"}
        </button>

        {detalhado && (
          <div className="mt-3 border-t border-white/10 pt-3">
            <DetalheSinais
              sinais={resultado.sinais}
              fontes={resultado.fontes_citadas}
            />
          </div>
        )}
      </div>
    </article>
  );
}
