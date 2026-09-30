"use client";

/**
 * Entrada de dados para checagem (RF-01): link, texto ou afirmação.
 *
 * Um único campo aceita os três formatos porque quem cola uma mensagem de WhatsApp não
 * sabe dizer se aquilo é "um link" ou "uma afirmação" — a classificação é trabalho do
 * backend, não do usuário.
 */

import { useState } from "react";

interface Props {
  onPerguntar: (texto: string) => void;
  carregando: boolean;
}

/** Detecta se o que foi colado é só uma URL, para mandar no campo certo. */
function pareceUrl(valor: string): boolean {
  const limpo = valor.trim();
  return /^https?:\/\/\S+$/.test(limpo) && !limpo.includes(" ");
}

export function CaixaDePergunta({ onPerguntar, carregando }: Props) {
  const [texto, setTexto] = useState("");
  const vazio = texto.trim().length === 0;

  function enviar() {
    if (vazio || carregando) return;
    onPerguntar(texto.trim());
  }

  return (
    <div className="w-full">
      <label htmlFor="pergunta" className="sr-only">
        Cole aqui o link, o texto ou a afirmação que quer checar
      </label>
      <div className="rounded-2xl border border-white/10 bg-white/5 p-2 focus-within:border-violet-400/60">
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
          rows={3}
          disabled={carregando}
          placeholder="Cola aqui o link ou o texto, meu bem…"
          className="w-full resize-none bg-transparent px-3 py-2 text-base text-white placeholder:text-white/40 focus:outline-none disabled:opacity-50"
        />
        <div className="flex items-center justify-between gap-3 px-3 pb-1">
          <span className="text-xs text-white/40">
            {pareceUrl(texto) ? "Isso é um link — vou abrir e ler." : "Enter para enviar"}
          </span>
          <button
            type="button"
            onClick={enviar}
            disabled={vazio || carregando}
            className="rounded-full bg-violet-500 px-5 py-2 text-sm font-medium text-white transition hover:bg-violet-400 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {carregando ? "Apurando…" : "Perguntar à Vera"}
          </button>
        </div>
      </div>
    </div>
  );
}
