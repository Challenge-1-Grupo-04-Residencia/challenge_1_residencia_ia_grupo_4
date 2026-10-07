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
 * ## O que saiu daqui, e por quê
 *
 * O cartão mostrava, de uma vez: a frase da Vera, a faixa, a porcentagem, a barra, um
 * parágrafo com o motivo da regra, **outro** parágrafo com a narração técnica de cada
 * camada, a fala em linguagem simples, duas listas de publicações, três métricas em
 * `<dl>` e o botão de detalhamento. Era muito texto jogado junto, e o que o leitor
 * precisa primeiro — o veredito e o motivo — ficava disputando espaço com o resto.
 *
 * Agora a ordem é a da pergunta que a pessoa faz: **o que é** (selo e porcentagem),
 * **por quê** (uma frase), **o que pesou** (as três maiores evidências, com barra), e só
 * então as fontes. Número de confiança, cobertura e dificuldade foram para dentro do
 * detalhamento: são metadados de auditoria, não a resposta.
 *
 * O balão fala em linguagem simples, sem jargão (RF-02). O vocabulário técnico vive no
 * detalhamento, que abre a um clique (RF-33).
 */

import { useState } from "react";

import { DetalheSinais } from "@/components/checagem/DetalheSinais";
import { VeraAvatar } from "@/components/vera/VeraAvatar";
import { falaDoSinal } from "@/lib/linguagem";
import {
  ROTULO_DIFICULDADE,
  contribuicao,
  estiloDaFaixa,
  rotuloDeConfianca,
} from "@/lib/veracidade";
import type { ChecagemResponse, Sinal } from "@/types/checagem";

interface Props {
  resultado: ChecagemResponse;
}

/** Quantas evidências aparecem no resumo antes do detalhamento. */
const EVIDENCIAS_EM_DESTAQUE = 3;

export function ResultadoChecagem({ resultado }: Props) {
  const [detalhado, setDetalhado] = useState(false);
  const estilo = estiloDaFaixa(resultado.faixa);
  const mostraPorcentagem =
    resultado.exibe_porcentagem && resultado.veracidade !== null;

  // A triagem do backend respondeu que a entrada era conversa, não notícia: não houve
  // checagem, então não há faixa, confiança, cobertura nem dificuldade para mostrar.
  // Exibir o arcabouço de resultado aqui — com 0% de certeza e "o que consegui apurar:
  // 0%" — faria parecer que a Vera tentou checar um "bom dia" e não conseguiu.
  if (resultado.faixa === "Conversa") {
    return (
      <article className="surge flex gap-3">
        <VeraAvatar humor="satisfeita" tamanho={44} className="mt-1 shrink-0" />
        <div className="min-w-0 flex-1 rounded-lg rounded-tl-sm border-2 border-borda bg-papel-2 p-4">
          <p className="text-base">{resultado.explicacao}</p>
        </div>
      </article>
    );
  }

  const destaques = resultado.principais_sinais
    .filter((s) => s.score !== null)
    .slice(0, EVIDENCIAS_EM_DESTAQUE);
  const maiorContribuicao = Math.max(
    ...destaques.map((s) => contribuicao(s.peso, s.score)),
    1,
  );

  return (
    <article className="estufa flex gap-3">
      <VeraAvatar humor={estilo.humor} tamanho={44} className="mt-1 shrink-0" />

      <div className={`min-w-0 flex-1 rounded-lg rounded-tl-sm border-2 p-4 ${estilo.cor}`}>
        {/* A frase da Vera vem primeiro, mas o dado técnico vem logo abaixo, nunca
            no lugar dela (RN-11). */}
        <p className="font-mao text-lg leading-snug">{estilo.frase}</p>

        <div className="mt-2 flex flex-wrap items-baseline gap-x-3 gap-y-1">
          <span className="font-display text-sm font-bold uppercase tracking-wide">
            {resultado.faixa}
          </span>
          {mostraPorcentagem && (
            <span className="font-display text-3xl font-bold tabular-nums leading-none">
              {Math.round(resultado.veracidade!)}%
            </span>
          )}
        </div>

        {mostraPorcentagem && (
          <div
            className="mt-2 h-2 w-full overflow-hidden rounded-total bg-papel-3"
            role="meter"
            aria-valuenow={Math.round(resultado.veracidade!)}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label="Score de veracidade"
          >
            <div
              className={`h-full rounded-total transition-all duration-700 ${estilo.barra}`}
              style={{ width: `${resultado.veracidade}%` }}
            />
          </div>
        )}

        {/* Quando uma regra de negócio decidiu, ela explica por que o resultado
            publicado não bate com a média dos sinais. Sem isso o número não fecha.
            Só a frase da regra, sem a narração das camadas colada atrás. */}
        {resultado.motivo_regra && (
          <p className="mt-3 rounded-md border border-borda bg-papel-3 px-3 py-2 text-sm">
            {resultado.motivo_regra}
          </p>
        )}

        {destaques.length > 0 && (
          <section className="mt-3">
            <h4 className="text-xs font-semibold uppercase tracking-wide opacity-60">
              O que mais pesou
            </h4>
            <ul className="mt-1.5 space-y-1.5">
              {destaques.map((sinal) => (
                <EvidenciaEmDestaque
                  key={sinal.id}
                  sinal={sinal}
                  maior={maiorContribuicao}
                />
              ))}
            </ul>
          </section>
        )}

        {/* Checagem da alegação e cobertura do fato são coisas opostas, e a tela
            precisa dizer qual é qual: listar o desmentido do G1 sob "quem mais
            publicou isso" afirma ao usuário o contrário do que aconteceu. */}
        {(["checagem", "cobertura"] as const).map((grupo) => {
          const docs = resultado.documentos_relacionados.filter((d) =>
            grupo === "checagem" ? d.e_checagem : !d.e_checagem,
          );
          if (docs.length === 0) return null;
          return (
            <section className="mt-3" key={grupo}>
              <h4 className="text-xs font-semibold uppercase tracking-wide opacity-60">
                {grupo === "checagem"
                  ? "Quem já conferiu isso"
                  : "Quem mais publicou isso"}
              </h4>
              <ul className="mt-1.5 space-y-1 text-sm">
                {docs.map((doc, i) => (
                  <li key={doc.url ?? i} className="flex items-baseline gap-2">
                    <span
                      className="shrink-0 text-xs"
                      title={
                        doc.fonte_confiavel
                          ? "Veículo da base curada"
                          : "Fora da base curada"
                      }
                      aria-hidden
                    >
                      {doc.fonte_confiavel ? "✓" : "·"}
                    </span>
                    <span className="min-w-0">
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
                      {doc.fonte && (
                        <span className="ml-1.5 opacity-60">— {doc.fonte}</span>
                      )}
                    </span>
                  </li>
                ))}
              </ul>
            </section>
          );
        })}

        <button
          type="button"
          onClick={() => setDetalhado((v) => !v)}
          aria-expanded={detalhado}
          className="mt-3 text-xs underline decoration-dotted underline-offset-2 opacity-70 hover:opacity-100"
        >
          {detalhado
            ? "Esconder as contas"
            : "Quer ver as minhas contas? Sinal por sinal, com o peso de cada um"}
        </button>

        {detalhado && (
          <div className="mt-3 border-t border-borda pt-3">
            {/* Metadado de auditoria: fica aqui, e não na resposta, porque não é o que
                a pessoa veio saber. */}
            <dl className="mb-3 flex flex-wrap gap-x-5 gap-y-1 text-xs opacity-70">
              <div>
                <dt className="inline">O quanto eu tenho certeza: </dt>
                <dd className="inline font-medium">
                  {rotuloDeConfianca(resultado.confianca)}
                </dd>
              </div>
              <div>
                <dt className="inline">Do que eu sei olhar, apurei: </dt>
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
            <DetalheSinais
              sinais={resultado.sinais}
              fontes={resultado.fontes_citadas}
            />
            {resultado.explicacao && (
              <p className="mt-3 border-t border-borda pt-3 text-xs opacity-70">
                {resultado.explicacao}
              </p>
            )}
          </div>
        )}
      </div>
    </article>
  );
}

/**
 * Uma das maiores evidências, com barra proporcional ao quanto pesou.
 *
 * A barra existe para a comparação ser visual: ler "peso 20" e "peso 5" exige fazer a
 * conta de cabeça, e a pessoa está ali para entender, não para calcular.
 */
function EvidenciaEmDestaque({ sinal, maior }: { sinal: Sinal; maior: number }) {
  const peso = contribuicao(sinal.peso, sinal.score);
  const aFavor = (sinal.score ?? 0) >= 0.5;

  return (
    <li>
      <div className="flex items-baseline justify-between gap-2 text-sm">
        <span className="min-w-0">{falaDoSinal(sinal) ?? sinal.nome}</span>
        <span
          className="shrink-0 text-xs font-semibold"
          title={aFavor ? "Pesou a favor" : "Pesou contra"}
        >
          {aFavor ? "a favor" : "contra"}
        </span>
      </div>
      <div className="mt-1 h-1.5 w-full overflow-hidden rounded-total bg-papel-3">
        <div
          className={`h-full rounded-total ${aFavor ? "bg-confirmada" : "bg-falsa"}`}
          style={{ width: `${Math.max(8, (peso / maior) * 100)}%` }}
        />
      </div>
    </li>
  );
}
