"use client";

/**
 * O feed das últimas checagens, como uma tira de quadrinhos (RF-43).
 *
 * Era uma lista vertical de cartões dentro de um cartão. Como tira — quadros
 * lado a lado, cada um com o carimbo do veredito grande e uma linha de texto —
 * ela diz a mesma coisa em menos leitura, e diz na linguagem do resto do
 * produto. Quem lê devagar consegue varrer os carimbos sem ler nenhum título.
 *
 * Serve a quem chega sem uma dúvida específica: ver o que já foi desmentido é
 * prevenção, que é mais barato do que checar depois de acreditar.
 *
 * Os dados vêm de `GET /api/v1/checagens/recentes`. O histórico do backend é em
 * memória por enquanto, então a lista zera quando o servidor reinicia — é por
 * isso que o estado vazio existe de verdade aqui, e não como enfeite.
 */

import { useEffect, useState } from "react";

import { Icone } from "@/components/ui/Icone";
import { checagensRecentes } from "@/lib/api";
import { estiloDaFaixa } from "@/lib/veracidade";
import type { ChecagemDoFeed } from "@/types/checagem";

/** "Hoje, 14:32" · "Ontem, 18:45" · "27/09, 09:10" */
function quando(iso: string): string {
  const data = new Date(iso);
  if (Number.isNaN(data.getTime())) return "";

  const hora = data.toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });

  const hoje = new Date();
  const mesmoDia = (a: Date, b: Date) =>
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate();

  const ontem = new Date(hoje);
  ontem.setDate(hoje.getDate() - 1);

  if (mesmoDia(data, hoje)) return `Hoje, ${hora}`;
  if (mesmoDia(data, ontem)) return `Ontem, ${hora}`;

  return `${data.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" })}, ${hora}`;
}

interface Props {
  /**
   * Tira enxuta, para caber dentro da faixa de abertura.
   *
   * A tela inicial não rola: a faixa e o chat ocupam a tela inteira, e o que
   * ficava embaixo teve de subir. Nesta forma cada checagem é só carimbo e uma
   * linha — o suficiente para a pessoa reconhecer um assunto e tocar.
   */
  compacto?: boolean;
  /**
   * Variante para a navegação lateral, que é vermelha.
   *
   * Lá o texto é branco e o cartão precisa de contorno claro; usar as cores de
   * papel deixaria a tira invisível sobre o vermelho.
   */
  naBarra?: boolean;
}

export function UltimasChecagens({ compacto = false, naBarra = false }: Props = {}) {
  const [checagens, setChecagens] = useState<ChecagemDoFeed[] | null>(null);

  useEffect(() => {
    let ativo = true;
    checagensRecentes(6).then((lista) => {
      if (ativo) setChecagens(lista);
    });
    return () => {
      ativo = false;
    };
  }, []);

  if (compacto) {
    if (!checagens) return null;

    // Vazio dito com todas as letras, e não um buraco na tela. Na barra lateral
    // o silêncio passa; no celular, onde a tira é a única coisa abaixo da caixa
    // de pergunta, sumir deixava meia tela em branco sem explicação.
    if (checagens.length === 0) {
      return (
        <p
          className={`flex items-center gap-2 rounded-md border-2 border-dashed p-3 text-sm ${
            naBarra ? "border-white/40 text-white/85" : "border-borda text-tinta-2"
          }`}
        >
          <Icone nome="jornal" tamanho={20} className="shrink-0" />
          Ainda não conferi nada hoje. Manda a primeira aí em cima!
        </p>
      );
    }

    return (
      <section className={naBarra ? "" : "mt-3"}>
        <header className="flex items-baseline justify-between gap-3">
          <h2
            className={`flex items-center gap-1.5 text-xs font-bold uppercase tracking-wide ${
              naBarra ? "text-white/80" : "text-tinta-2"
            }`}
          >
            <Icone nome="jornal" tamanho={16} />
            Eu já conferi
          </h2>
          <a
            href="/historico"
            className={`flex items-center gap-1 text-xs font-bold hover:underline ${
              naBarra ? "text-white" : "text-vermelho"
            }`}
          >
            Ver tudo
            <Icone nome="seta" tamanho={14} />
          </a>
        </header>

        <ul className="mt-1.5 flex flex-col gap-1.5">
          {checagens.slice(0, naBarra ? 2 : 3).map((c, i) => {
            const estilo = estiloDaFaixa(c.faixa);
            return (
              <li
                key={c.id}
                className="surge"
                style={{ "--atraso": `${600 + i * 80}ms` } as React.CSSProperties}
              >
                <a
                  href={`/checagem/${c.id}`}
                  className={`block rounded-sm border-2 border-tinta px-2 py-1.5 ${
                    naBarra ? "bg-papel-2 text-tinta" : "bg-papel-3 hover:bg-papel-2"
                  }`}
                >
                  <span
                    className={`flex w-fit items-center gap-1 rounded-sm px-1.5 py-0.5 font-display text-sm leading-none ${estilo.carimbo}`}
                  >
                    <Icone nome={estilo.icone} tamanho={14} />
                    {estilo.palavra}
                  </span>
                  <span
                    className={`mt-1 block text-sm font-semibold leading-snug ${
                      naBarra ? "line-clamp-2" : "truncate"
                    }`}
                  >
                    {c.trecho}
                  </span>
                </a>
              </li>
            );
          })}
        </ul>
      </section>
    );
  }

  return (
    <section>
      <header className="flex items-baseline justify-between gap-3">
        <h2 className="flex items-center gap-2 font-display text-2xl">
          <Icone nome="jornal" tamanho={24} />O que eu já conferi
        </h2>
        <a
          href="/historico"
          className="flex items-center gap-1 text-sm font-bold text-tinta-2 hover:text-vermelho"
        >
          Ver tudo
          <Icone nome="seta" tamanho={16} />
        </a>
      </header>

      {checagens === null && (
        <p className="mt-4 text-sm text-tinta-3">Deixa eu ver o que eu já conferi…</p>
      )}

      {checagens?.length === 0 && (
        <p className="mt-4 rounded-md border-2 border-dashed border-borda p-5 text-center text-base text-tinta-2">
          Tô meio borocoxô: ninguém me trouxe nada hoje. Manda aí em cima que eu
          vou atrás.
        </p>
      )}

      {checagens && checagens.length > 0 && (
        <ul className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {checagens.map((c, i) => {
            const estilo = estiloDaFaixa(c.faixa);
            return (
              // Escalonar a entrada faz a tira "cair" em cascata, como quadro
              // sendo colado na prancha um a um.
              <li
                key={c.id}
                className="entra-baixo"
                style={{ "--atraso": `${i * 70}ms`, animationDelay: `${i * 70}ms` } as React.CSSProperties}
              >
                <a
                  href={`/checagem/${c.id}`}
                  className="painel pressiona flex h-full flex-col gap-2 p-3 hover:bg-papel-3"
                >
                  <span
                    className={`flex w-fit items-center gap-1.5 rounded-sm border-2 border-tinta px-2 py-1 font-display text-lg leading-none ${estilo.carimbo}`}
                  >
                    <Icone nome={estilo.icone} tamanho={18} />
                    {estilo.palavra}
                  </span>

                  <p className="line-clamp-3 text-base font-semibold leading-snug">
                    {c.trecho}
                  </p>

                  <p className="mt-auto flex items-center gap-1.5 text-xs text-tinta-3">
                    <Icone nome="relogio" tamanho={14} />
                    {quando(c.checada_em)}
                    {c.exibe_porcentagem && c.veracidade !== null && (
                      <span className="font-display text-base text-tinta-2">
                        {Math.round(c.veracidade)}%
                      </span>
                    )}
                  </p>
                </a>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
