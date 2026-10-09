"use client";

/**
 * As indicações manuscritas que aparecem na primeira vez, como anotação de
 * quadrinho à margem do quadro.
 *
 * Substituem a janela de tour para a pergunta "onde eu faço o quê?". O tour
 * parava a pessoa, escurecia a tela e pedia atenção antes de ela ter feito nada;
 * isto fica ao lado da coisa que descreve, em letra de mão com uma seta, e some
 * sozinho assim que a pessoa começa a escrever — porque aí ela já sabe.
 *
 * Aparecem uma vez por visita, e nunca cobrem nada: são irmãos do elemento, não
 * camadas por cima dele.
 */

import { useEffect, useState } from "react";

interface Props {
  /** Texto da anotação. */
  children: React.ReactNode;
  /** De que lado a seta aponta. */
  seta?: "cima" | "baixo" | "esquerda";
  /** Atraso da entrada, para escalonar com o resto da página. */
  atraso?: number;
  className?: string;
}

export function Apontamento({ children, seta = "cima", atraso = 900, className = "" }: Props) {
  const [visivel, setVisivel] = useState(false);

  useEffect(() => {
    // Some assim que a pessoa interage: a anotação já fez o trabalho dela, e
    // texto parado em volta do campo vira ruído durante a digitação.
    function sumir() {
      setVisivel(false);
    }
    const t = setTimeout(() => setVisivel(true), atraso);
    document.addEventListener("keydown", sumir, { once: true });
    document.addEventListener("pointerdown", sumir, { once: true });
    return () => {
      clearTimeout(t);
      document.removeEventListener("keydown", sumir);
      document.removeEventListener("pointerdown", sumir);
    };
  }, [atraso]);

  if (!visivel) return null;

  return (
    <span
      /* `hidden sm:flex`: no celular a anotação cai em cima das outras coisas,
         e o campo já diz o que fazer no próprio texto de apoio. */
      className={`estala fonte-mao pointer-events-none hidden items-center gap-1.5 text-lg text-tinta-2 sm:flex ${className}`}
      aria-hidden
    >
      {children}
      {seta === "baixo" ? (
        <SetaParaBaixo />
      ) : seta === "cima" ? (
        <SetaParaCima />
      ) : (
        <SetaParaEsquerda />
      )}
    </span>
  );
}

/** Seta desenhada à mão, com a curva de quem rabisca na margem. */
function SetaParaCima() {
  return (
    <svg viewBox="0 0 40 34" className="h-7 w-8 shrink-0" fill="none" aria-hidden>
      <path
        d="M34 30C30 14 22 6 10 5"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
      <path
        d="M10 5l9 1M10 5l2 9"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
    </svg>
  );
}

/**
 * Aponta para baixo, para a caixa que vem logo abaixo da anotação.
 *
 * A primeira versão descia para a **direita**, que é para fora da tela: a
 * anotação fica encostada na margem direita, e a seta mandava olhar para o lado
 * em vez de para o campo.
 */
function SetaParaBaixo() {
  return (
    <svg viewBox="0 0 34 34" className="h-7 w-7 shrink-0" fill="none" aria-hidden>
      <path
        d="M26 3C29 12 27 22 18 29"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
      <path
        d="M18 29l1-9M18 29l9 0"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
    </svg>
  );
}

function SetaParaEsquerda() {
  return (
    <svg viewBox="0 0 40 24" className="h-5 w-8 shrink-0" fill="none" aria-hidden>
      <path d="M38 12C26 12 16 12 5 12" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M5 12l8-6M5 12l8 6" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
    </svg>
  );
}
