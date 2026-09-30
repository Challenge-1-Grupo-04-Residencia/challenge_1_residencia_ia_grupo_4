"use client";

/**
 * Resultado de uma checagem (RF-32, RN-05).
 *
 * Por RN-05, todo resultado mostra porcentagem, rótulo da faixa, principais sinais e
 * fontes — resultado sem explicação não é exibido. Por RN-11, a frase da Vera aparece
 * **junto** com o dado técnico, nunca no lugar dele, e por RN-03 a porcentagem some
 * quando o conteúdo é opinião ou sátira.
 */

import { useState } from "react";

import { DetalheSinais } from "@/components/checagem/DetalheSinais";
import { VeraAvatar } from "@/components/vera/VeraAvatar";
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

  return (
    <article className={`rounded-2xl border p-5 ${estilo.cor}`}>
      <header className="flex items-start gap-4">
        <VeraAvatar humor={estilo.humor} tamanho={64} className="shrink-0" />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
            <h3 className="text-lg font-semibold">{resultado.faixa}</h3>
            {mostraPorcentagem && (
              <span className="text-2xl font-bold tabular-nums">
                {Math.round(resultado.veracidade!)}%
              </span>
            )}
          </div>
          <p className="mt-1 text-sm opacity-80">{estilo.frase}</p>
        </div>
      </header>

      {mostraPorcentagem && (
        <div
          className="mt-4 h-2 w-full overflow-hidden rounded-full bg-black/30"
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

      {/* A regra de negócio aplicada explica por que o resultado publicado difere do
          score calculado — sem isso o usuário vê um número que não fecha com os sinais. */}
      {resultado.regra_aplicada && (
        <p className="mt-4 rounded-lg border border-white/20 bg-black/20 p-3 text-sm">
          <span className="font-mono text-xs opacity-60">
            {resultado.regra_aplicada}
          </span>{" "}
          {resultado.explicacao}
        </p>
      )}

      {!resultado.regra_aplicada && resultado.explicacao && (
        <p className="mt-4 text-sm opacity-90">{resultado.explicacao}</p>
      )}

      <dl className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-xs opacity-70">
        <div>
          <dt className="inline">Confiança: </dt>
          <dd className="inline font-medium">
            {rotuloDeConfianca(resultado.confianca)}
          </dd>
        </div>
        <div>
          <dt className="inline">Sinais medidos: </dt>
          <dd className="inline font-medium">
            {Math.round(resultado.cobertura * 100)}% do total
          </dd>
        </div>
        <div>
          <dt className="inline">Parou em: </dt>
          <dd className="inline font-medium">{resultado.camada_parada}</dd>
        </div>
        <div>
          <dt className="inline">Dificuldade: </dt>
          <dd className="inline font-medium">
            {ROTULO_DIFICULDADE[resultado.dificuldade]}
          </dd>
        </div>
      </dl>

      {resultado.principais_sinais.length > 0 && (
        <section className="mt-4">
          <h4 className="text-xs font-semibold uppercase tracking-wide opacity-60">
            O que mais pesou
          </h4>
          <ul className="mt-2 space-y-1 text-sm">
            {resultado.principais_sinais.map((sinal) => (
              <li key={sinal.id} className="flex gap-2">
                <span aria-hidden>{(sinal.score ?? 0) >= 0.5 ? "▲" : "▼"}</span>
                <span className="opacity-90">{sinal.justificativa || sinal.nome}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {resultado.documentos_relacionados.length > 0 && (
        <section className="mt-4">
          <h4 className="text-xs font-semibold uppercase tracking-wide opacity-60">
            Quem mais publicou
          </h4>
          <ul className="mt-2 space-y-1.5 text-sm">
            {resultado.documentos_relacionados.map((doc, i) => (
              <li key={doc.url ?? i} className="flex items-baseline gap-2">
                <span
                  className="shrink-0 text-xs"
                  title={doc.fonte_confiavel ? "Veículo na base curada" : "Fora da base curada"}
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
                <span className="shrink-0 text-xs opacity-50">{doc.fonte}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <button
        type="button"
        onClick={() => setDetalhado((v) => !v)}
        aria-expanded={detalhado}
        className="mt-4 text-xs underline decoration-dotted underline-offset-2 opacity-70 hover:opacity-100"
      >
        {detalhado ? "Esconder o detalhamento" : "Ver sinal por sinal e o peso de cada um"}
      </button>

      {detalhado && (
        <div className="mt-4 border-t border-white/10 pt-4">
          <DetalheSinais sinais={resultado.sinais} />
        </div>
      )}
    </article>
  );
}
