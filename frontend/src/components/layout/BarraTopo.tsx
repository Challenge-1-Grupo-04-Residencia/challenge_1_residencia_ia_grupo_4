"use client";

/**
 * Barra de topo com a busca principal, como no protótipo.
 *
 * O campo aceita link, texto ou afirmação sem a pessoa precisar dizer qual é
 * qual (RF-01) — quem cola uma mensagem de mensageiro não sabe classificar o que
 * recebeu, e não deveria precisar.
 */

import { useRouter } from "next/navigation";
import { useState } from "react";

import { AlternarTema } from "@/components/layout/AlternarTema";
import { DICA_POR_TIPO, classificarEntrada } from "@/lib/entrada";

export function BarraTopo() {
  const [texto, setTexto] = useState("");
  const router = useRouter();
  const vazio = texto.trim().length === 0;

  function enviar() {
    if (vazio) return;
    router.push(`/checar?q=${encodeURIComponent(texto.trim())}`);
  }

  return (
    <header className="sticky top-0 z-30 flex items-center gap-3 border-b border-borda bg-papel-2 px-4 py-3 md:px-6">
      <form
        role="search"
        className="flex flex-1 items-center gap-3 rounded-md border border-borda bg-papel-2 px-4 py-2.5 focus-within:border-vermelho"
        onSubmit={(e) => {
          e.preventDefault();
          enviar();
        }}
      >
        <svg viewBox="0 0 24 24" className="size-5 shrink-0 text-tinta-3" aria-hidden>
          <circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" strokeWidth="2" />
          <path d="m20 20-3.5-3.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        </svg>

        <label htmlFor="busca" className="sr-only">
          Cole aqui o link, o texto ou a notícia que quer checar
        </label>
        <input
          id="busca"
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="Cole aqui o link, texto ou notícia…"
          /* 16px é o mínimo: abaixo disso o Safari no iPhone dá zoom ao focar. */
          className="min-w-0 flex-1 bg-transparent text-base text-tinta placeholder:text-tinta-3 focus:outline-none"
        />

        {!vazio && (
          <span className="hidden shrink-0 text-xs text-tinta-3 lg:inline">
            {DICA_POR_TIPO[classificarEntrada(texto).tipo]}
          </span>
        )}
      </form>

      <AlternarTema />

      <button
        type="button"
        className="relative rounded-md p-2 text-tinta-2 hover:bg-papel-3"
        aria-label="Notificações"
      >
        <svg viewBox="0 0 24 24" className="size-6" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M18 8a6 6 0 1 0-12 0c0 6-2 7-2 7h16s-2-1-2-7" strokeLinejoin="round" />
          <path d="M10.5 20a2 2 0 0 0 3 0" strokeLinecap="round" />
        </svg>
        <span
          className="absolute right-1.5 top-1.5 size-2.5 rounded-full bg-vermelho ring-2 ring-papel-2"
          aria-hidden
        />
      </button>

      <button
        type="button"
        className="rounded-full p-1 text-tinta-2 hover:bg-papel-3"
        aria-label="Sua conta"
      >
        <svg viewBox="0 0 24 24" className="size-8" fill="currentColor">
          <circle cx="12" cy="12" r="11" className="text-papel-3" fill="currentColor" opacity="0.25" />
          <circle cx="12" cy="9.5" r="3.5" />
          <path d="M5 20a7 7 0 0 1 14 0z" />
        </svg>
      </button>
    </header>
  );
}
