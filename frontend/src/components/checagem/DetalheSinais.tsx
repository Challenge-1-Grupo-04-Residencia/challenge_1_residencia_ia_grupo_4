"use client";

/**
 * Detalhamento do veredito: sinal por sinal, com peso (RF-32, RF-33).
 *
 * Separado em **a favor**, **contra** e **não medido**, como pede o critério de aceite —
 * agrupar por dimensão técnica obrigaria o leitor a calcular de cabeça de que lado cada
 * coisa pesou.
 *
 * Esta é a única parte da interface onde o vocabulário técnico aparece (ID do sinal,
 * peso, nome do método): o objetivo aqui é **auditar** a decisão, e para isso o leitor
 * precisa dos nomes reais. A conversa, essa fala em linguagem simples.
 *
 * Os sinais **não medidos** aparecem de propósito. Esconder o que a Vera não conseguiu
 * apurar faria a checagem parecer mais completa do que foi, e é justamente a lacuna que
 * explica uma confiança baixa.
 */

import { ROTULO_DIMENSAO, contribuicao } from "@/lib/veracidade";
import { sinalAponta } from "@/lib/linguagem";
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
      <p className="text-xs text-white/50">
        A nota é a média dos sinais que eu consegui medir, cada um com o seu peso.{" "}
        <strong className="font-medium text-white/70">
          {pesoMedido} de 100 pontos
        </strong>{" "}
        foram medidos nesta checagem.
      </p>

      <Grupo
        titulo="Pesou contra"
        sinais={contra}
        cor="text-red-300"
        barra="bg-red-500"
        vazio="Nada pesou contra."
      />
      <Grupo
        titulo="Pesou a favor"
        sinais={aFavor}
        cor="text-lime-300"
        barra="bg-lime-500"
        vazio="Nada pesou a favor."
      />

      {semDado.length > 0 && (
        <section>
          <h4 className="mb-2 text-sm font-semibold text-white/50">
            Não consegui medir
          </h4>
          <ul className="space-y-1.5">
            {semDado.map((sinal) => (
              <li
                key={sinal.id}
                className="rounded-lg border border-white/5 bg-white/2 p-3 text-sm"
              >
                <div className="flex items-baseline justify-between gap-3">
                  <span className="text-white/60">
                    <span className="font-mono text-xs text-white/30">{sinal.id}</span>{" "}
                    {sinal.nome}
                  </span>
                  <span className="shrink-0 text-xs text-white/30">
                    valeria {sinal.peso}
                  </span>
                </div>
                <p className="mt-1 text-xs italic text-white/40">
                  Ficou de fora da conta — não conta como ponto contra a notícia.
                  {sinal.justificativa && ` ${sinal.justificativa}`}
                </p>
              </li>
            ))}
          </ul>
        </section>
      )}

      {fontes.length > 0 && (
        <section>
          <h4 className="mb-2 text-sm font-semibold text-white/50">
            Fontes que eu consultei
          </h4>
          <ul className="space-y-1 text-sm">
            {fontes.map((url) => (
              <li key={url}>
                <a
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="break-all text-violet-300 underline decoration-dotted underline-offset-2 hover:decoration-solid"
                >
                  {url}
                </a>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

interface GrupoProps {
  titulo: string;
  sinais: Sinal[];
  cor: string;
  barra: string;
  vazio: string;
}

function Grupo({ titulo, sinais, cor, barra, vazio }: GrupoProps) {
  const peso = sinais.reduce((total, s) => total + s.peso, 0);

  return (
    <section>
      <header className="mb-2 flex items-baseline justify-between">
        <h4 className={`text-sm font-semibold ${cor}`}>{titulo}</h4>
        {sinais.length > 0 && (
          <span className="text-xs text-white/40">{peso} pontos em jogo</span>
        )}
      </header>

      {sinais.length === 0 ? (
        <p className="text-xs italic text-white/30">{vazio}</p>
      ) : (
        <ul className="space-y-2">
          {sinais.map((sinal) => (
            <LinhaDeSinal key={sinal.id} sinal={sinal} barra={barra} />
          ))}
        </ul>
      )}
    </section>
  );
}

function LinhaDeSinal({ sinal, barra }: { sinal: Sinal; barra: string }) {
  // A barra cresce com o quanto o sinal puxou o resultado para um dos lados: um sinal
  // pesado mas morno contribuiu pouco para a conclusão, e mostrá-lo cheio enganaria.
  const largura = (contribuicao(sinal.peso, sinal.score) / 20) * 100;

  return (
    <li className="rounded-lg border border-white/10 bg-white/5 p-3">
      <div className="flex items-baseline justify-between gap-3">
        <span className="text-sm text-white/90">
          <span className="font-mono text-xs text-white/40">{sinal.id}</span>{" "}
          {sinal.nome}
        </span>
        <span className="shrink-0 text-xs text-white/40">
          peso {sinal.peso} · {ROTULO_DIMENSAO[sinal.dimensao]}
        </span>
      </div>

      <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-white/10">
        <div
          className={`h-full rounded-full ${barra}`}
          style={{ width: `${Math.min(100, largura)}%` }}
        />
      </div>

      {sinal.justificativa && (
        <p className="mt-1.5 text-xs text-white/50">{sinal.justificativa}</p>
      )}
    </li>
  );
}
