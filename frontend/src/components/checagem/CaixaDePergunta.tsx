"use client";

/**
 * Entrada de dados para checagem (RF-01) e perguntas de acompanhamento (RF-04).
 *
 * Um único campo aceita link, texto e afirmação porque quem cola uma mensagem de
 * mensageiro não sabe dizer se aquilo é "um link" ou "uma afirmação" — classificar é
 * trabalho nosso, não de quem pergunta.
 *
 * Depois do primeiro veredito o mesmo campo passa a servir para perguntar sobre o
 * resultado, e o texto de apoio muda para deixar isso claro.
 */

import { useState } from "react";

import { Icone } from "@/components/ui/Icone";
import { DICA_POR_TIPO, classificarEntrada } from "@/lib/entrada";

interface Props {
  onPerguntar: (texto: string) => void;
  carregando: boolean;
  /** Depois do primeiro veredito, o campo vira caixa de acompanhamento. */
  modoAcompanhamento?: boolean;
}

export function CaixaDePergunta({
  onPerguntar,
  carregando,
  modoAcompanhamento = false,
}: Props) {
  const [texto, setTexto] = useState("");
  const vazio = texto.trim().length === 0;

  function enviar() {
    if (vazio || carregando) return;
    onPerguntar(texto.trim());
    setTexto("");
  }

  const dica = modoAcompanhamento
    ? "Pergunta por que, ou quais fontes eu vi."
    : vazio
      ? "É só apertar Enter, visse?"
      : DICA_POR_TIPO[classificarEntrada(texto).tipo];

  return (
    <div className="w-full">
      <label htmlFor="pergunta" className="sr-only">
        {modoAcompanhamento
          ? "Pergunte algo sobre o resultado"
          : "Cole aqui o link, o texto ou a afirmação que quer checar"}
      </label>
      <div className="campo-composto rounded-lg border-[3px] border-tinta bg-papel-2 p-2 shadow-bloco-sm">
        <textarea
          id="pergunta"
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          onKeyDown={(e) => {
            // Enter envia; Shift+Enter quebra linha, como em qualquer chat.
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              enviar();
            }
          }}
          /* Duas linhas, não três: a caixa precisa caber na primeira tela junto
             com a faixa de abertura, e ela cresce sozinha quando o texto passa
             disso. */
          rows={2}
          disabled={carregando}
          placeholder={
            modoAcompanhamento
              ? "Quer saber mais alguma coisa, meu bem?"
              : "Cola aqui o link ou o texto que você recebeu…"
          }
          className="w-full resize-none bg-transparent px-3 py-2 text-base text-tinta placeholder:text-tinta-3 focus:outline-none disabled:opacity-50"
        />
        <div className="flex items-center justify-between gap-3 px-3 pb-1">
          <span className="text-xs text-tinta-3">{dica}</span>
          <button
            type="button"
            onClick={enviar}
            disabled={vazio || carregando}
            className="pressiona flex min-h-11 shrink-0 items-center gap-2 rounded-total border-[3px] border-tinta bg-vermelho px-5 py-2 font-display text-lg text-white shadow-bloco-sm hover:bg-vermelho-forte disabled:cursor-not-allowed disabled:opacity-40"
          >
            <Icone nome={carregando ? "relogio" : "lupa"} tamanho={20} />
            {carregando ? "Apurando…" : modoAcompanhamento ? "Perguntar" : "Pergunta"}
          </button>
        </div>
      </div>
    </div>
  );
}
