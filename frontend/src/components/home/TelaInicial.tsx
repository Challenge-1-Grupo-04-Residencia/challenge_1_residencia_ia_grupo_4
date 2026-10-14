"use client";

/**
 * A tela inicial: abertura em quadrinhos, apresentação e conversa.
 *
 * A **abertura em quadrinhos** roda na primeira visita, por cima de tudo, e
 * conta quem é a Vera com um caso do começo ao fim. Ela substituiu o tour
 * guiado, que ficava por cima da página e, no celular, engolia todos os toques —
 * quem chegava no aparelho não conseguia clicar em nada, nem nos próprios botões
 * da tela. Duas apresentações seguidas também era uma a mais.
 *
 * Depois disso, o que muda é **o que some**. Enquanto ninguém perguntou nada, a
 * página se apresenta: a faixa com a Vera, a caixa de pergunta, o que ela
 * devolve e o que já conferiu. Assim que chega a primeira mensagem, tudo isso
 * sai de cena e a tela vira chat.
 *
 * O motivo é de leitura, não de enfeite: a resposta da Vera é um painel alto,
 * com carimbo, termômetro e evidências. Com a apresentação ainda na tela, a
 * resposta nasceria abaixo da dobra, e quem veio com uma dúvida aflitiva rolaria
 * procurando o que pediu.
 */

import Link from "next/link";
import { Suspense, useCallback, useState } from "react";

import { Conversa } from "@/components/checagem/Conversa";
import { Apontamento } from "@/components/home/Apontamentos";
import { Hero } from "@/components/home/Hero";
import { UltimasChecagens } from "@/components/home/UltimasChecagens";
import { AberturaEmQuadrinhos } from "@/components/onboarding/AberturaEmQuadrinhos";
import { Icone, type NomeDoIcone } from "@/components/ui/Icone";

/** O que a Vera devolve numa checagem. Três palavras cada, como manda a skill. */
const PROMESSAS: Array<{ icone: NomeDoIcone; texto: string }> = [
  { icone: "site", texto: "Quem publicou" },
  { icone: "jornal", texto: "Quem mais falou" },
  { icone: "contas", texto: "Quanto pesou" },
];

/** Exemplos para quem chega sem saber o que colar: um toque e a checagem roda.
 *  Navegam para `/?q=`, que a `Conversa` lê e dispara sozinha. Misturam boato
 *  conhecido e fato, para a pessoa ver a Vera acertar nos dois sentidos. */
const EXEMPLOS = [
  "O Pix vai ser taxado?",
  "A vacina da Covid tem chip?",
  "O Brasil tem segundo turno em 2026?",
];

/** A abertura não precisa avisar ninguém quando termina: ela só sai de cena. */
function naoFazNada() {}

export function TelaInicial() {
  const [conversando, setConversando] = useState(false);
  // Muda a chave do componente para remontá-lo quando a pessoa pede para rever.
  const [revisao, setRevisao] = useState(0);

  const comecou = useCallback(() => setConversando(true), []);
  const rever = useCallback(() => setRevisao((n) => n + 1), []);

  return (
    <>
      <AberturaEmQuadrinhos
        key={revisao}
        aoTerminar={naoFazNada}
        forcar={revisao > 0}
      />

      {/* A primeira dobra é exatamente isto: a faixa de abertura e o chat.
          `calc(100dvh - 5rem)` no celular porque a barra de navegação fixa de
          baixo já consome 5rem de `padding` no layout, e pedir a altura cheia
          aqui criava exatamente essa sobra de rolagem. */}
      <div
        className={
          conversando ? "" : "flex min-h-[calc(100dvh-5rem)] flex-col md:min-h-dvh"
        }
      >
        {/* A faixa **não** estica, e também não é recortada por um teto de
            altura: ela tem exatamente a altura do que diz, e o que sobra da tela
            fica com o chat. Esticando, o vermelho tomava metade da tela sem
            acrescentar informação; com `max-h`, o título saía cortado. */}
        {!conversando && <Hero aoRever={rever} />}

        {/* A cascata de entrada é a mesma ideia da prancha de quadrinho: os
            elementos são colados um a um, na ordem em que se leem. O chat entra
            por último porque é onde a pessoa vai agir.

            No celular o conteúdo começa logo abaixo da faixa; centralizar
            deixava um vão enorme entre a apresentação e a caixa de pergunta. */}
        <div
          className={`mx-auto w-full max-w-3xl px-4 pb-0 md:px-8 ${
            conversando
              ? "pt-4"
              : "estufa flex flex-1 flex-col justify-start pt-4 sm:justify-center sm:pt-0"
          }`}
          style={conversando ? undefined : ({ "--atraso": "520ms" } as React.CSSProperties)}
        >
          {conversando && (
            <div className="flex items-center justify-between gap-3 pb-2">
              <h1 className="font-display text-2xl">Conversa com a Vera</h1>
              <button
                type="button"
                onClick={() => window.location.assign("/")}
                className="flex min-h-11 items-center gap-1.5 rounded-total px-3 text-sm font-semibold text-tinta-2 hover:text-vermelho"
              >
                <Icone nome="seta" tamanho={18} className="rotate-180" />
                Começar de novo
              </button>
            </div>
          )}

          {/* A anotação é um rabisco colado no canto de cima da caixa. Dentro do
              fluxo ela empurrava a tela para além da primeira dobra; embaixo,
              caía em cima da linha das promessas; e à direita, cobria a arte da
              Vera. Aqui não cobre nada e aponta para onde se escreve. */}
          <div className="relative">
            {!conversando && (
              <Apontamento
                className="absolute -top-6 left-6 whitespace-nowrap"
                seta="baixo"
                atraso={1000}
              >
                Cola aqui o que te mandaram!
              </Apontamento>
            )}

            {/* `useSearchParams` suspende na renderização estática do App Router. */}
            <Suspense fallback={<p className="text-tinta-3">Já vou te atender, meu bem…</p>}>
              <Conversa saudacao={conversando} aoComecar={comecou} />
            </Suspense>
          </div>

          {/* O que a Vera devolve, logo abaixo de onde se pergunta: é aqui que a
              promessa faz sentido, e não no balão de apresentação, onde ela
              disputava espaço com outros três assuntos. */}
          {!conversando && (
            <div
              className="surge mt-3 flex flex-wrap items-center justify-center gap-x-3 gap-y-1 text-center"
              style={{ "--atraso": "640ms" } as React.CSSProperties}
            >
              {PROMESSAS.map((promessa) => (
                <span
                  key={promessa.texto}
                  className="flex items-center gap-1.5 text-xs font-bold text-tinta-2 sm:text-sm"
                >
                  <Icone nome={promessa.icone} tamanho={18} className="text-vermelho" />
                  {promessa.texto}
                </span>
              ))}
            </div>
          )}

          {/* Exemplos clicáveis: enchem o espaço abaixo da caixa com o que a
              pessoa veio fazer, e ensinam o que dá para colar. Um toque leva a
              `/?q=`, e a Conversa dispara a checagem. */}
          {!conversando && (
            <div
              className="surge mt-6"
              style={{ "--atraso": "720ms" } as React.CSSProperties}
            >
              <p className="text-center text-sm font-semibold text-tinta-2">
                Ou experimenta um destes, meu bem:
              </p>
              <div className="mt-2 flex flex-wrap justify-center gap-2">
                {EXEMPLOS.map((exemplo) => (
                  <Link
                    key={exemplo}
                    href={`/?q=${encodeURIComponent(exemplo)}`}
                    className="flex min-h-11 items-center gap-1.5 rounded-total border-[3px] border-tinta bg-papel-2 px-4 text-sm font-semibold text-tinta shadow-bloco-sm transition-colors hover:bg-vermelho-suave"
                  >
                    <Icone nome="lupa" tamanho={16} className="text-vermelho" />
                    {exemplo}
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* A tira do que já foi conferido aparece aqui **no celular**: lá não
              existe a coluna lateral, e sem ela a tela ficava com um vazio
              grande embaixo da caixa — além de esconder do celular um conteúdo
              que o desktop mostra. */}
          {!conversando && (
            <div
              className="surge mt-6 md:hidden"
              style={{ "--atraso": "800ms" } as React.CSSProperties}
            >
              <UltimasChecagens compacto />
            </div>
          )}
        </div>
      </div>
    </>
  );
}
