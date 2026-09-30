"use client";

/**
 * Apresentação guiada na primeira visita.
 *
 * A Vera se apresenta e mostra o site, destacando um trecho por vez. Existe
 * porque o produto tem uma ideia que não é óbvia: ela não dá um carimbo de
 * verdadeiro ou falso, ela mostra o caminho — quais fontes consultou e quanto
 * cada sinal pesou. Quem não entende isso usa a Vera como mais um oráculo, que
 * é o contrário do que ela serve para fazer.
 *
 * Aparece uma vez só e sai por Esc, por clique fora ou pelo botão. Nada aqui
 * bloqueia o uso do site: um tour que não se pode pular é uma parede.
 */

import { useCallback, useEffect, useRef, useState } from "react";

import { VeraAvatar } from "@/components/vera/VeraAvatar";
import type { HumorDaVera } from "@/lib/veracidade";

const CHAVE = "vera:tour-visto";

interface Passo {
  /** Elemento a destacar. `null` mostra o cartão sem recorte. */
  alvo: string | null;
  titulo: string;
  texto: string;
  humor: HumorDaVera;
}

const PASSOS: Passo[] = [
  {
    alvo: null,
    titulo: "Oi, meu bem!",
    texto:
      "Eu sou a Vera. Você me traz aquela notícia que chegou no grupo da família, e eu vou atrás de saber se é verdade. Deixa eu te mostrar a casa em meio minuto?",
    humor: "satisfeita",
  },
  {
    alvo: "[data-tour='busca']",
    titulo: "Aqui você me pergunta",
    texto:
      "Cola o link, o texto ou só a afirmação que você ouviu. Não precisa saber dizer o que é — isso é comigo.",
    humor: "investigando",
  },
  {
    alvo: "[data-tour='feed']",
    titulo: "O que eu já conferi",
    texto:
      "Aqui fica o que passou por mim. Dar uma espiada antes ajuda: muita mentira volta a circular do mesmo jeitinho.",
    humor: "pensativa",
  },
  {
    alvo: "[data-tour='dica']",
    titulo: "E o mais importante, visse?",
    texto:
      "Eu não te dou só um carimbo de verdadeiro ou falso. Eu mostro quem publicou, o que encontrei e quanto cada coisa pesou — pra você decidir com a sua própria cabeça.",
    humor: "orgulhosa",
  },
];

interface Recorte {
  top: number;
  left: number;
  width: number;
  height: number;
}

export function Tour() {
  const [aberto, setAberto] = useState(false);
  const [passo, setPasso] = useState(0);
  const [recorte, setRecorte] = useState<Recorte | null>(null);
  const botaoRef = useRef<HTMLButtonElement>(null);

  const fechar = useCallback(() => {
    setAberto(false);
    try {
      localStorage.setItem(CHAVE, "1");
    } catch {
      // Sem localStorage o tour reaparece na próxima visita. Chato, não quebrado.
    }
  }, []);

  // Abre só na primeira visita, e depois da página assentar: aparecer no meio
  // do carregamento faria o cartão pular junto com o resto.
  useEffect(() => {
    let visto = true;
    try {
      visto = localStorage.getItem(CHAVE) === "1";
    } catch {
      visto = false;
    }
    if (visto) return;

    const id = setTimeout(() => setAberto(true), 900);
    return () => clearTimeout(id);
  }, []);

  // Mede o alvo do passo atual, e remede se a janela mudar de tamanho.
  useEffect(() => {
    if (!aberto) return;

    function medir() {
      const seletor = PASSOS[passo].alvo;
      if (!seletor) {
        setRecorte(null);
        return;
      }
      const alvo = document.querySelector(seletor);
      if (!alvo) {
        setRecorte(null);
        return;
      }
      alvo.scrollIntoView({ block: "center", behavior: "smooth" });
      const r = alvo.getBoundingClientRect();
      const folga = 8;
      setRecorte({
        top: r.top - folga,
        left: r.left - folga,
        width: r.width + folga * 2,
        height: r.height + folga * 2,
      });
    }

    const id = setTimeout(medir, 260);
    window.addEventListener("resize", medir);
    return () => {
      clearTimeout(id);
      window.removeEventListener("resize", medir);
    };
  }, [aberto, passo]);

  useEffect(() => {
    if (!aberto) return;
    botaoRef.current?.focus();

    function aoTeclar(e: KeyboardEvent) {
      if (e.key === "Escape") fechar();
      if (e.key === "ArrowRight") setPasso((p) => Math.min(p + 1, PASSOS.length - 1));
      if (e.key === "ArrowLeft") setPasso((p) => Math.max(p - 1, 0));
    }
    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
  }, [aberto, fechar]);

  if (!aberto) return null;

  const atual = PASSOS[passo];
  const ultimo = passo === PASSOS.length - 1;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center p-4 md:items-center"
      role="dialog"
      aria-modal="true"
      aria-labelledby="tour-titulo"
    >
      {/* Quem escurece a tela é UM só elemento, nunca dois.
          Com alvo, o escuro vem da sombra gigante do holofote, que deixa o
          recorte limpo; o clique-fora fica transparente, senão ele cobriria de
          novo o elemento em destaque e o holofote não destacaria nada.
          Sem alvo (primeiro passo), o próprio clique-fora faz o escuro. */}
      <button
        type="button"
        aria-label="Fechar a apresentação"
        onClick={fechar}
        className={`absolute inset-0 cursor-default transition-colors ${
          recorte ? "bg-transparent" : "bg-tinta/60"
        }`}
      />
      {recorte && (
        <span
          aria-hidden
          className="pointer-events-none absolute rounded-md ring-4 ring-ocre transition-all duration-300"
          style={{
            top: recorte.top,
            left: recorte.left,
            width: recorte.width,
            height: recorte.height,
            boxShadow: "0 0 0 9999px rgb(26 20 16 / 0.65)",
          }}
        />
      )}

      <div className="estufa relative w-full max-w-md rounded-lg border-[3px] border-tinta bg-papel-2 p-5 shadow-bloco">
        <div className="flex items-start gap-3">
          <VeraAvatar humor={atual.humor} tamanho={52} className="shrink-0" />
          <div className="min-w-0">
            <h2 id="tour-titulo" className="font-display text-xl font-bold">
              {atual.titulo}
            </h2>
            <p className="mt-1.5 text-base leading-relaxed text-tinta-2">
              {atual.texto}
            </p>
          </div>
        </div>

        <div className="mt-5 flex items-center justify-between gap-3">
          <ol
            className="flex gap-1.5"
            aria-label={`Passo ${passo + 1} de ${PASSOS.length}`}
          >
            {PASSOS.map((_, i) => (
              <li
                key={i}
                className={`h-2 rounded-full transition-all ${
                  i === passo ? "w-6 bg-vermelho" : "w-2 bg-borda"
                }`}
              />
            ))}
          </ol>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={fechar}
              className="rounded-total px-3 py-2 text-sm font-semibold text-tinta-2 hover:bg-papel-3"
            >
              {ultimo ? "Fechar" : "Pular"}
            </button>
            <button
              ref={botaoRef}
              type="button"
              onClick={() => (ultimo ? fechar() : setPasso((p) => p + 1))}
              className="pressiona rounded-total border-2 border-tinta bg-vermelho px-5 py-2 font-display font-bold text-white shadow-bloco-sm"
            >
              {ultimo ? "Bora conferir!" : "Mostra aí"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
