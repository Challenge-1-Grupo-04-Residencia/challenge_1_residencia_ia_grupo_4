"use client";

/**
 * Navegação lateral, como no protótipo.
 *
 * Em telas estreitas ela vira uma barra inferior fixa: o celular é o caso
 * principal do produto — é por mensageiro que a desinformação circula —, e uma
 * gaveta escondida atrás de um botão sanduíche esconderia justamente a navegação
 * de quem mais precisa dela.
 */

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import { MarcaVera } from "@/components/layout/MarcaVera";

interface Item {
  href: string;
  rotulo: string;
  icone: ReactNode;
}

const traco = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

const ITENS: Item[] = [
  {
    href: "/",
    rotulo: "Início",
    icone: (
      <svg viewBox="0 0 24 24" className="size-6" {...traco}>
        <path d="M3 10.5 12 3l9 7.5" />
        <path d="M5 9.5V20h14V9.5" />
      </svg>
    ),
  },
  {
    href: "/checar",
    rotulo: "Verificar notícia",
    icone: (
      <svg viewBox="0 0 24 24" className="size-6" {...traco}>
        <circle cx="11" cy="11" r="7" />
        <path d="m20 20-3.5-3.5" />
      </svg>
    ),
  },
  {
    href: "/historico",
    rotulo: "Histórico",
    icone: (
      <svg viewBox="0 0 24 24" className="size-6" {...traco}>
        <circle cx="12" cy="12" r="9" />
        <path d="M12 7v5l3.5 2" />
      </svg>
    ),
  },
  {
    href: "/favoritos",
    rotulo: "Favoritos",
    icone: (
      <svg viewBox="0 0 24 24" className="size-6" {...traco}>
        <path d="M6 4h12v17l-6-4.5L6 21z" />
      </svg>
    ),
  },
  {
    href: "/configuracoes",
    rotulo: "Configurações",
    icone: (
      <svg viewBox="0 0 24 24" className="size-6" {...traco}>
        <circle cx="12" cy="12" r="3.2" />
        <path d="M12 3v2.2M12 18.8V21M21 12h-2.2M5.2 12H3M18.4 5.6l-1.6 1.6M7.2 16.8l-1.6 1.6M18.4 18.4l-1.6-1.6M7.2 7.2 5.6 5.6" />
      </svg>
    ),
  },
];

export function BarraLateral() {
  const caminho = usePathname();

  return (
    <>
      {/* Coluna, do tablet para cima */}
      <nav
        aria-label="Navegação principal"
        className="sticky top-0 hidden h-dvh w-[264px] shrink-0 flex-col bg-vermelho text-white md:flex"
      >
        <div className="px-6 pt-6">
          <MarcaVera />
        </div>

        <ul className="mt-8 flex flex-col gap-1 px-3">
          {ITENS.map((item) => (
            <li key={item.href}>
              <ItemDeMenu item={item} ativo={caminho === item.href} />
            </li>
          ))}
        </ul>

        <p className="fonte-mao mt-auto px-6 pb-8 text-2xl leading-tight text-white/90">
          Juntos contra
          <br />a desinformação!
        </p>
      </nav>

      {/* Barra inferior, no celular */}
      <nav
        aria-label="Navegação principal"
        className="fixed inset-x-0 bottom-0 z-40 flex justify-around border-t border-white/15 bg-vermelho px-1 py-1.5 text-white md:hidden"
      >
        {ITENS.map((item) => {
          const ativo = caminho === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              aria-current={ativo ? "page" : undefined}
              className={`flex min-w-16 flex-col items-center gap-0.5 rounded-md px-2 py-1.5 text-[11px] ${
                ativo ? "bg-white/20 font-bold" : "text-white/85"
              }`}
            >
              {item.icone}
              <span className="leading-none">{item.rotulo.split(" ")[0]}</span>
            </Link>
          );
        })}
      </nav>
    </>
  );
}

function ItemDeMenu({ item, ativo }: { item: Item; ativo: boolean }) {
  return (
    <Link
      href={item.href}
      aria-current={ativo ? "page" : undefined}
      className={`flex items-center gap-3 rounded-md px-4 py-3 text-base transition-colors ${
        ativo
          ? "bg-white/20 font-bold"
          : "font-semibold text-white/90 hover:bg-white/10"
      }`}
    >
      {item.icone}
      {item.rotulo}
    </Link>
  );
}
