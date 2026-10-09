"use client";

/**
 * O veredito, como um quadro de quadrinho (RF-02, RF-05, RF-32).
 *
 * Quatro regras moldam este componente:
 *
 * - **RN-05** — todo resultado mostra porcentagem, faixa, principais sinais e fontes.
 *   Resultado sem explicação não é exibido.
 * - **RN-11** — a frase da Vera acompanha o dado técnico e nunca o substitui.
 * - **RN-03** — opinião e sátira não recebem porcentagem.
 * - **RN-12** — a palavra curta do carimbo não substitui o rótulo da faixa:
 *   "CONVERSA FIADA" é bom de ler, mas o que o produto afirma é "provavelmente falsa".
 *
 * ## Por que é assim
 *
 * A versão anterior já tinha enxugado o cartão, e ainda assim era parede de texto: três
 * frases longas de evidência, dois parágrafos, duas listas e um `<dl>`. Quem lê devagar
 * — que é parte grande de quem recebe mentira no mensageiro — não chegava ao fim.
 *
 * Agora a tela se lê na ordem de `vera-gamificacao`: pictograma, palavra curta, rótulo
 * oficial, termômetro de cinco casas, três evidências de quatro palavras com polegar, e
 * quem publicou. A auditoria inteira — confiança, cobertura, dificuldade, sinal por
 * sinal com peso e nome técnico — continua ali, atrás de um botão, para RF-33.
 */

import { useState } from "react";

import { DetalheSinais } from "@/components/checagem/DetalheSinais";
import { Icone } from "@/components/ui/Icone";
import { VeraAvatar } from "@/components/vera/VeraAvatar";
import { resumoDoSinal } from "@/lib/linguagem";
import {
  CASAS_DO_TERMOMETRO,
  ORDEM_DAS_FAIXAS,
  ROTULO_DIFICULDADE,
  contribuicao,
  estiloDaFaixa,
  rotuloDeConfianca,
} from "@/lib/veracidade";
import type { ChecagemResponse, DocumentoRelacionado, Sinal } from "@/types/checagem";

interface Props {
  resultado: ChecagemResponse;
}

/** Quantas evidências aparecem no resumo antes do detalhamento. */
const EVIDENCIAS_EM_DESTAQUE = 3;

/** Quantas publicações cabem em cada lista antes de o resto ir para o detalhe. */
const PUBLICACOES_EM_DESTAQUE = 3;

export function ResultadoChecagem({ resultado }: Props) {
  const [detalhado, setDetalhado] = useState(false);
  const estilo = estiloDaFaixa(resultado.faixa);
  const mostraPorcentagem =
    resultado.exibe_porcentagem && resultado.veracidade !== null;

  // A triagem do backend respondeu que a entrada era conversa, não notícia: não houve
  // checagem, então não há faixa, confiança, cobertura nem dificuldade para mostrar.
  // Exibir o arcabouço de resultado aqui faria parecer que a Vera tentou checar um
  // "bom dia" e não conseguiu.
  if (resultado.faixa === "Conversa") {
    return (
      <article className="surge flex gap-3">
        <VeraAvatar humor="satisfeita" tamanho={48} />
        <div className="min-w-0 flex-1 rounded-lg rounded-tl-sm border-[3px] border-tinta bg-papel-2 p-4 shadow-bloco-sm">
          <p className="text-base">{resultado.explicacao}</p>
        </div>
      </article>
    );
  }

  const evidencias = resultado.principais_sinais
    .filter((s) => s.score !== null)
    .slice(0, EVIDENCIAS_EM_DESTAQUE);
  const maiorContribuicao = Math.max(
    ...evidencias.map((s) => contribuicao(s.peso, s.score)),
    1,
  );

  const checagens = resultado.documentos_relacionados.filter((d) => d.e_checagem);
  const coberturas = resultado.documentos_relacionados.filter((d) => !d.e_checagem);
  const posicao = ORDEM_DAS_FAIXAS.indexOf(resultado.faixa);

  return (
    <article className="estufa flex gap-3" role="status" aria-live="polite">
      <VeraAvatar humor={estilo.humor} tamanho={48} moldura={estilo.cor.split(" ")[0]} />

      <div className={`painel min-w-0 flex-1 overflow-hidden p-0 ${estilo.cor}`}>
        {/* ---- O carimbo: é o que se lê primeiro, de relance -------------- */}
        <header className="relative px-4 pb-4 pt-5">
          <div
            className="reticula pointer-events-none absolute inset-0 text-tinta"
            aria-hidden
          />

          <div className="relative flex flex-wrap items-center gap-x-4 gap-y-3">
            <span
              className={`bate-carimbo flex items-center gap-2 rounded-sm border-[3px] border-tinta px-3 py-1.5 ${estilo.carimbo}`}
            >
              <Icone nome={estilo.icone} tamanho={40} className="shrink-0" />
              <span className="font-display text-2xl">{estilo.palavra}</span>
            </span>

            {mostraPorcentagem && (
              <span className="font-display text-4xl tabular-nums">
                {Math.round(resultado.veracidade!)}%
              </span>
            )}
          </div>

          {/* O rótulo oficial da faixa, sempre escrito: a palavra do carimbo é
              atalho de leitura, não é o que o produto afirma (RN-12). */}
          <p className="relative mt-2 text-sm font-bold uppercase tracking-wide">
            {resultado.faixa}
          </p>

          {mostraPorcentagem && (
            <Termometro
              posicao={posicao}
              porcentagem={Math.round(resultado.veracidade!)}
            />
          )}

          {/* A fala da Vera vem depois do dado, nunca no lugar dele (RN-11). */}
          {estilo.frase && (
            <p className="relative mt-3 fonte-mao text-lg leading-snug">
              {estilo.frase}
            </p>
          )}
        </header>

        <div className="border-t-[3px] border-tinta bg-papel-2 p-4 text-tinta">
          {/* Quando uma regra de negócio decidiu, ela explica por que o resultado
              publicado não bate com a média dos sinais. Sem isso o número não fecha. */}
          {resultado.motivo_regra && (
            <p className="mb-4 flex gap-2 rounded-md bg-papel-3 px-3 py-2 text-sm">
              <Icone nome="alerta" tamanho={20} className="mt-0.5 shrink-0" />
              <span>{resultado.motivo_regra}</span>
            </p>
          )}

          {evidencias.length > 0 && (
            <section>
              <Titulo icone="contas" texto="O que pesou" />
              <ul className="mt-2 space-y-2">
                {evidencias.map((sinal) => (
                  <Evidencia key={sinal.id} sinal={sinal} maior={maiorContribuicao} />
                ))}
              </ul>
            </section>
          )}

          {/* Checagem da alegação e cobertura do fato são coisas opostas, e a tela
              precisa dizer qual é qual: listar o desmentido do G1 sob "quem mais
              publicou isso" afirma ao usuário o contrário do que aconteceu. */}
          {checagens.length > 0 && (
            <ListaDePublicacoes
              icone="lupa"
              titulo="Já conferiram isso"
              documentos={checagens}
            />
          )}
          {coberturas.length > 0 && (
            <ListaDePublicacoes
              icone="jornal"
              titulo="Quem publicou"
              documentos={coberturas}
            />
          )}

          <button
            type="button"
            onClick={() => setDetalhado((v) => !v)}
            aria-expanded={detalhado}
            aria-label={
              detalhado
                ? "Esconder as contas da checagem"
                : "Ver as contas da checagem, sinal por sinal"
            }
            className="pressiona mt-4 flex min-h-11 w-full items-center justify-center gap-2 rounded-total border-[3px] border-tinta bg-papel-3 px-4 py-2 font-display text-lg shadow-bloco-sm"
          >
            <Icone nome="contas" tamanho={22} />
            {detalhado ? "Esconder as contas" : "Ver as minhas contas"}
          </button>

          {detalhado && (
            <div className="mt-4 border-t border-borda pt-4">
              {/* Metadado de auditoria: fica aqui, e não na resposta, porque não é o
                  que a pessoa veio saber. */}
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
      </div>
    </article>
  );
}

/** Cabeçalho de bloco: pictograma e palavra, sempre os dois. */
function Titulo({ icone, texto }: { icone: Parameters<typeof Icone>[0]["nome"]; texto: string }) {
  return (
    <h4 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wide text-tinta-2">
      <Icone nome={icone} tamanho={18} />
      {texto}
    </h4>
  );
}

/**
 * O termômetro de cinco casas.
 *
 * A porcentagem é precisa e abstrata; a régua desenhada é grosseira e imediata. As
 * duas aparecem juntas porque servem a leitores diferentes — e as cinco casas são as
 * cinco faixas de `docs/produto/classificacao.md`, nunca uma simplificação delas.
 */
function Termometro({ posicao, porcentagem }: { posicao: number; porcentagem: number }) {
  return (
    <div
      className="relative mt-3 flex gap-1.5"
      role="meter"
      aria-valuenow={porcentagem}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label="O quanto esta notícia parece verdadeira"
    >
      {CASAS_DO_TERMOMETRO.map((casa, i) => (
        <span
          key={casa.faixa}
          className={[
            "h-4 flex-1 rounded-sm border-2 border-tinta transition-opacity duration-500",
            i === posicao ? `${casa.cor} opacity-100` : "bg-papel-2 opacity-45",
          ].join(" ")}
          aria-hidden
        />
      ))}
    </div>
  );
}

/**
 * Uma evidência, em quatro palavras.
 *
 * Três coisas dizem de que lado ela pesou, porque cor sozinha não serve a quem tem
 * daltonia: o polegar (silhueta oposta), a palavra e a barra. A barra é proporcional
 * ao quanto o sinal puxou o resultado — ler "peso 20" e "peso 5" exigiria fazer a
 * conta de cabeça, e a pessoa está ali para entender, não para calcular.
 */
function Evidencia({ sinal, maior }: { sinal: Sinal; maior: number }) {
  const resumo = resumoDoSinal(sinal);
  if (!resumo) return null;

  const peso = contribuicao(sinal.peso, sinal.score);
  const aFavor = resumo.direcao === "favor";

  return (
    <li className="flex items-center gap-3 rounded-md border border-borda bg-papel-3 p-2.5">
      <span
        className={`flex size-11 shrink-0 items-center justify-center rounded-total border-2 border-tinta ${
          aFavor ? "bg-verdadeira-fundo text-confirmada" : "bg-falsa-fundo text-falsa"
        }`}
      >
        <Icone nome={resumo.icone} tamanho={24} />
      </span>

      <span className="min-w-0 flex-1">
        <span className="block text-base font-bold leading-tight">{resumo.texto}</span>
        <span className="mt-1.5 block h-1.5 w-full overflow-hidden rounded-total bg-papel-2">
          <span
            className={`block h-full rounded-total ${aFavor ? "bg-verdadeira" : "bg-falsa"}`}
            style={{ width: `${Math.max(12, (peso / maior) * 100)}%` }}
          />
        </span>
      </span>

      <span
        className={`flex shrink-0 flex-col items-center gap-0.5 ${
          aFavor ? "text-confirmada" : "text-falsa"
        }`}
      >
        <Icone nome={aFavor ? "aFavor" : "contra"} tamanho={24} />
        <span className="text-[11px] font-bold uppercase">
          {aFavor ? "a favor" : "contra"}
        </span>
      </span>
    </li>
  );
}

/** Quem publicou, com visto para o veículo da base curada. */
function ListaDePublicacoes({
  icone,
  titulo,
  documentos,
}: {
  icone: Parameters<typeof Icone>[0]["nome"];
  titulo: string;
  documentos: DocumentoRelacionado[];
}) {
  const visiveis = documentos.slice(0, PUBLICACOES_EM_DESTAQUE);
  const restantes = documentos.length - visiveis.length;

  return (
    <section className="mt-4">
      <Titulo icone={icone} texto={titulo} />
      <ul className="mt-2 space-y-1.5">
        {visiveis.map((doc, i) => (
          <li key={doc.url ?? i} className="flex items-center gap-2 text-sm">
            <span
              className={`flex size-6 shrink-0 items-center justify-center rounded-total ${
                doc.fonte_confiavel
                  ? "bg-confirmada text-white"
                  : "border border-borda text-tinta-3"
              }`}
              title={doc.fonte_confiavel ? "Veículo da base curada" : "Fora da base curada"}
            >
              <Icone nome={doc.fonte_confiavel ? "visto" : "duvida"} tamanho={14} />
            </span>
            <span className="min-w-0 flex-1 truncate">
              {doc.url ? (
                <a
                  href={doc.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-semibold underline decoration-dotted underline-offset-2 hover:decoration-solid"
                >
                  {doc.fonte || doc.titulo}
                </a>
              ) : (
                <span className="font-semibold">{doc.fonte || doc.titulo}</span>
              )}
            </span>
          </li>
        ))}
      </ul>
      {restantes > 0 && (
        <p className="mt-1 text-xs text-tinta-3">
          e mais {restantes}. Tá tudo nas minhas contas, ali embaixo.
        </p>
      )}
    </section>
  );
}
