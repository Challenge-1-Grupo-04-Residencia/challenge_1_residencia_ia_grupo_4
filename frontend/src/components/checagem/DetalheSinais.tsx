"use client";

/**
 * Detalhamento do veredito: sinal por sinal, com peso (RF-32, RF-33).
 *
 * Esta é a única parte da interface onde o vocabulário técnico aparece (ID do sinal,
 * peso, nome do método): o objetivo aqui é **auditar** a decisão, e para isso o leitor
 * precisa dos nomes reais. A conversa, essa fala em linguagem simples.
 *
 * ## O que mudou, e por quê
 *
 * A tela era uma lista de nomes técnicos com barras: "S-07 · Análise de sensacionalismo
 * · peso 8 · conteúdo". Quem construiu o sistema lê isso; quem recebeu uma corrente no
 * mensageiro, não — e é essa pessoa que clica em "ver as contas" para entender por que a
 * Vera disse o que disse.
 *
 * Agora cada linha começa pela **frase em português e o pictograma**, com o nome técnico
 * logo abaixo, menor. Nada foi escondido: o ID, o peso e a justificativa continuam
 * todos ali, na mesma linha, porque auditar sem eles é impossível. O que mudou é a
 * ordem de leitura — primeiro o que significa, depois como se chama.
 *
 * Os sinais **não medidos** aparecem de propósito. Esconder o que a Vera não conseguiu
 * apurar faria a checagem parecer mais completa do que foi, e é justamente a lacuna que
 * explica uma confiança baixa (RN-06).
 */

import { Icone, type NomeDoIcone } from "@/components/ui/Icone";
import { ROTULO_DIMENSAO, contribuicao } from "@/lib/veracidade";
import { falaDoSinal, resumoDoSinal, sinalAponta } from "@/lib/linguagem";
import type { Sinal } from "@/types/checagem";

interface Props {
  sinais: Sinal[];
  /** URLs consultadas, para ancorar os sinais de corroboração (RN-05). */
  fontes?: string[];
}

export function DetalheSinais({ sinais, fontes = [] }: Props) {
  if (sinais.length === 0) return null;

  const aFavor = sinais.filter((s) => sinalAponta(s) === "favor");
  const contra = sinais.filter((s) => sinalAponta(s) === "contra");
  const semDado = sinais.filter((s) => sinalAponta(s) === "indisponivel");

  const pesoMedido = [...aFavor, ...contra].reduce((t, s) => t + s.peso, 0);

  return (
    <div className="space-y-5">
      {/* A regra da casa, dita em uma frase antes de qualquer número. */}
      <p className="flex items-start gap-2 rounded-md border-2 border-borda bg-papel-3 p-3 text-sm">
        <Icone nome="contas" tamanho={20} className="mt-0.5 shrink-0 text-vermelho" />
        <span>
          Eu olho <strong>{sinais.length} coisas</strong> em cada notícia, e cada uma
          vale um tanto. Nesta aqui eu consegui medir{" "}
          <strong>{pesoMedido} de 100 pontos</strong>. O que eu não consegui medir fica
          de fora da conta, e nunca conta como ponto contra.
        </span>
      </p>

      <Grupo
        titulo="Pesou contra"
        icone="contra"
        sinais={contra}
        cor="text-falsa"
        barra="bg-falsa"
        vazio="Nada pesou contra."
      />
      <Grupo
        titulo="Pesou a favor"
        icone="aFavor"
        sinais={aFavor}
        cor="text-confirmada"
        barra="bg-verdadeira"
        vazio="Nada pesou a favor."
      />

      {semDado.length > 0 && (
        <section>
          <Cabecalho icone="semDado" titulo="Não consegui apurar" cor="text-tinta-3" />
          <ul className="mt-2 space-y-1.5">
            {semDado.map((sinal) => (
              <li
                key={sinal.id}
                className="rounded-md border-2 border-dashed border-borda bg-papel-3 p-3 text-sm"
              >
                <div className="flex items-baseline justify-between gap-3">
                  <span className="font-semibold text-tinta-2">{sinal.nome}</span>
                  <span className="shrink-0 text-xs text-tinta-3">
                    valeria {sinal.peso}
                  </span>
                </div>
                <p className="mt-1 text-xs text-tinta-3">
                  <span className="font-mono">{sinal.id}</span> · ficou de fora da
                  conta.
                  {sinal.justificativa && ` ${sinal.justificativa}`}
                </p>
              </li>
            ))}
          </ul>
        </section>
      )}

      {fontes.length > 0 && (
        <section>
          <Cabecalho icone="lupa" titulo="Onde eu fui olhar" cor="text-tinta-2" />
          <p className="mt-1 text-xs text-tinta-3">
            Pode conferir você mesma: é só tocar em cada uma.
          </p>
          <ul className="mt-2 space-y-1.5">
            {fontes.map((url) => (
              <li key={url}>
                <a
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-start gap-2 rounded-md border-2 border-borda bg-papel-2 p-2.5 text-sm hover:border-vermelho"
                >
                  <Icone nome="link" tamanho={18} className="mt-0.5 shrink-0 text-vermelho" />
                  <span className="min-w-0 flex-1 break-all underline decoration-dotted underline-offset-2">
                    {url}
                  </span>
                </a>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

function Cabecalho({
  icone,
  titulo,
  cor,
  direita,
}: {
  icone: NomeDoIcone;
  titulo: string;
  cor: string;
  direita?: string;
}) {
  return (
    <header className="flex items-baseline justify-between gap-3">
      <h4 className={`flex items-center gap-2 font-display text-xl ${cor}`}>
        <Icone nome={icone} tamanho={20} />
        {titulo}
      </h4>
      {direita && <span className="shrink-0 text-xs text-tinta-3">{direita}</span>}
    </header>
  );
}

interface GrupoProps {
  titulo: string;
  icone: NomeDoIcone;
  sinais: Sinal[];
  cor: string;
  barra: string;
  vazio: string;
}

function Grupo({ titulo, icone, sinais, cor, barra, vazio }: GrupoProps) {
  const peso = sinais.reduce((total, s) => total + s.peso, 0);

  return (
    <section>
      <Cabecalho
        icone={icone}
        titulo={titulo}
        cor={cor}
        direita={sinais.length > 0 ? `${peso} pontos em jogo` : undefined}
      />

      {sinais.length === 0 ? (
        <p className="mt-1 text-sm italic text-tinta-3">{vazio}</p>
      ) : (
        <ul className="mt-2 space-y-2">
          {sinais.map((sinal) => (
            <LinhaDeSinal key={sinal.id} sinal={sinal} barra={barra} />
          ))}
        </ul>
      )}
    </section>
  );
}

/**
 * Uma linha da auditoria: primeiro o que significa, depois como se chama.
 *
 * A barra cresce com o quanto o sinal puxou o resultado para um dos lados — um sinal
 * pesado mas morno contribuiu pouco para a conclusão, e mostrá-lo cheio enganaria.
 */
function LinhaDeSinal({ sinal, barra }: { sinal: Sinal; barra: string }) {
  const resumo = resumoDoSinal(sinal);
  const largura = (contribuicao(sinal.peso, sinal.score) / 20) * 100;

  return (
    <li className="rounded-md border-2 border-borda bg-papel-3 p-3">
      <div className="flex items-start gap-2.5">
        {resumo && (
          <span className="mt-0.5 shrink-0 text-tinta-2">
            <Icone nome={resumo.icone} tamanho={22} />
          </span>
        )}
        <div className="min-w-0 flex-1">
          <p className="text-base font-bold leading-snug">
            {falaDoSinal(sinal) ?? sinal.nome}
          </p>
          <p className="mt-0.5 text-xs text-tinta-3">
            <span className="font-mono">{sinal.id}</span> · {sinal.nome} · peso{" "}
            {sinal.peso} · {ROTULO_DIMENSAO[sinal.dimensao]}
          </p>
        </div>
      </div>

      <div className="mt-2 h-2 w-full overflow-hidden rounded-total border border-borda bg-papel-2">
        <div
          className={`h-full rounded-total ${barra}`}
          style={{ width: `${Math.min(100, largura)}%` }}
        />
      </div>

      {sinal.justificativa && (
        <p className="mt-1.5 text-xs text-tinta-3">{sinal.justificativa}</p>
      )}
    </li>
  );
}
