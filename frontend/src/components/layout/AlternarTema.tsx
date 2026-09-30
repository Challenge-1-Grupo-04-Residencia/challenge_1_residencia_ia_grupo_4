"use client";

/**
 * Troca entre tema claro e escuro (RNF de acessibilidade).
 *
 * A escolha vai para `data-tema` no `<html>` e para o `localStorage`. O padrão é
 * seguir o sistema: quem configurou o aparelho em modo escuro já disse o que
 * prefere, e perguntar de novo é ignorar a resposta.
 *
 * O `localStorage` pode falhar em janela anônima ou com dados bloqueados, então
 * toda leitura e escrita vai em try/catch — a página precisa funcionar mesmo
 * quando ele não existe.
 */

import { useEffect, useState } from "react";

type Tema = "claro" | "escuro" | "sistema";

const CHAVE = "vera:tema";

export function AlternarTema() {
  const [tema, setTema] = useState<Tema>("sistema");

  useEffect(() => {
    try {
      const salvo = localStorage.getItem(CHAVE) as Tema | null;
      if (salvo) setTema(salvo);
    } catch {
      // Sem localStorage seguimos no padrão do sistema.
    }
  }, []);

  useEffect(() => {
    const raiz = document.documentElement;
    if (tema === "sistema") {
      raiz.removeAttribute("data-tema");
    } else {
      raiz.setAttribute("data-tema", tema);
    }
    try {
      localStorage.setItem(CHAVE, tema);
    } catch {
      // A preferência simplesmente não persiste entre sessões.
    }
  }, [tema]);

  const escuro =
    tema === "escuro" ||
    (tema === "sistema" &&
      typeof window !== "undefined" &&
      window.matchMedia?.("(prefers-color-scheme: dark)").matches);

  return (
    <button
      type="button"
      onClick={() => setTema(escuro ? "claro" : "escuro")}
      className="rounded-md p-2 text-tinta-2 hover:bg-papel-3"
      aria-label={escuro ? "Usar tema claro" : "Usar tema escuro"}
    >
      {escuro ? (
        <svg viewBox="0 0 24 24" className="size-6" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="4.5" />
          <path d="M12 2v2.5M12 19.5V22M22 12h-2.5M4.5 12H2M18.4 5.6l-1.8 1.8M7.4 16.6l-1.8 1.8M18.4 18.4l-1.8-1.8M7.4 7.4 5.6 5.6" strokeLinecap="round" />
        </svg>
      ) : (
        <svg viewBox="0 0 24 24" className="size-6" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5" strokeLinejoin="round" />
        </svg>
      )}
    </button>
  );
}
