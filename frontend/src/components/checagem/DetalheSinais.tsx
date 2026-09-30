"use client";

/**
 * Detalhamento de cada sinal e do seu peso (RF-33).
 *
 * Mostra também os sinais **indisponíveis**, em vez de escondê-los: saber que a Vera
 * não conseguiu medir a reputação do veículo é parte de entender por que a confiança
 * ficou baixa. Esconder o que falta faria a checagem parecer mais completa do que foi.
 */

import { ROTULO_DIMENSAO, contribuicao } from "@/lib/veracidade";
import type { Dimensao, Sinal } from "@/types/checagem";

const ORDEM: Dimensao[] = ["fonte", "conteudo", "corroboracao"];

interface Props {
  sinais: Sinal[];
}

export function DetalheSinais({ sinais }: Props) {
  if (sinais.length === 0) return null;

  return (
    <div className="space-y-5">
      {ORDEM.map((dimensao) => {
        const daDimensao = sinais.filter((s) => s.dimensao === dimensao);
        if (daDimensao.length === 0) return null;

        const pesoObservado = daDimensao
          .filter((s) => s.score !== null)
          .reduce((soma, s) => soma + s.peso, 0);
        const pesoTotal = daDimensao.reduce((soma, s) => soma + s.peso, 0);

        return (
          <section key={dimensao}>
            <header className="mb-2 flex items-baseline justify-between">
              <h4 className="text-sm font-semibold text-white/80">
                {ROTULO_DIMENSAO[dimensao]}
              </h4>
              <span className="text-xs text-white/40">
                {pesoObservado} de {pesoTotal} pontos medidos
              </span>
            </header>
            <ul className="space-y-2">
              {daDimensao.map((sinal) => (
                <LinhaDeSinal key={sinal.id} sinal={sinal} />
              ))}
            </ul>
          </section>
        );
      })}
    </div>
  );
}

function LinhaDeSinal({ sinal }: { sinal: Sinal }) {
  const indisponivel = sinal.score === null;
  // A barra cresce com o quanto o sinal puxou o resultado para um dos lados; um sinal
  // pesado mas neutro contribuiu pouco para a conclusão.
  const largura = indisponivel ? 0 : (contribuicao(sinal.peso, sinal.score) / 20) * 100;
  const positivo = (sinal.score ?? 0) >= 0.5;

  return (
    <li
      className={`rounded-lg border p-3 ${
        indisponivel
          ? "border-white/5 bg-white/[0.02] opacity-60"
          : "border-white/10 bg-white/5"
      }`}
    >
      <div className="flex items-baseline justify-between gap-3">
        <span className="text-sm text-white/90">
          <span className="font-mono text-xs text-white/40">{sinal.id}</span>{" "}
          {sinal.nome}
        </span>
        <span className="shrink-0 text-xs text-white/40">peso {sinal.peso}</span>
      </div>

      {indisponivel ? (
        <p className="mt-1 text-xs italic text-white/40">
          Sem dado — não entrou no cálculo.
          {sinal.justificativa && ` ${sinal.justificativa}`}
        </p>
      ) : (
        <>
          <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-white/10">
            <div
              className={`h-full rounded-full ${positivo ? "bg-lime-500" : "bg-red-500"}`}
              style={{ width: `${Math.min(100, largura)}%` }}
            />
          </div>
          {sinal.justificativa && (
            <p className="mt-1.5 text-xs text-white/50">{sinal.justificativa}</p>
          )}
        </>
      )}
    </li>
  );
}
