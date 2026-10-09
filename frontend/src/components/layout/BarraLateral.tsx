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

import { AlternarTema } from "@/components/layout/AlternarTema";
import { MarcaVera } from "@/components/layout/MarcaVera";
import { UltimasChecagens } from "@/components/home/UltimasChecagens";

interface Item {
  href: string;
  rotulo: string;
  /** Como o item se chama na barra do celular, onde não cabe o nome inteiro. */
  curto: string;
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
    curto: "Início",
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
    curto: "Checar",
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
    curto: "Histórico",
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
    curto: "Salvos",
    icone: (
      <svg viewBox="0 0 24 24" className="size-6" {...traco}>
        <path d="M6 4h12v17l-6-4.5L6 21z" />
      </svg>
    ),
  },
  {
    href: "/configuracoes",
    rotulo: "Configurações",
    curto: "Ajustes",
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
        /* `overflow-y-auto`: com a tira de checagens aqui dentro, em tela baixa a
           coluna passa da altura da janela. Cortar esconderia a frase do rodapé; rolar
           por dentro mantém tudo alcançável sem mexer na página. */
        className="relative sticky top-0 hidden h-dvh w-[264px] shrink-0 flex-col overflow-y-auto border-r-[3px] border-tinta bg-vermelho text-white md:flex"
      >
        {/* A coluna era um retângulo vermelho chapado, que é o único lugar do
            produto sem nada de quadrinho. Agora tem a retícula de impressão
            atrás e o traço preto separando-a da página, como moldura de quadro. */}
        <div className="reticula pointer-events-none absolute inset-0 text-white" aria-hidden />
        <div className="relative flex items-start justify-between gap-2 px-6 pt-6">
          <MarcaVera />
          {/* O alternador de tema veio da barra de topo, que saiu. Ele precisa
              existir em algum lugar fixo: quem escolheu o tema claro no escuro
              do sistema não tem outro jeito de voltar. */}
          <AlternarTema />
        </div>

        <ul className="relative mt-6 flex flex-col gap-1 px-3">
          {ITENS.map((item, i) => (
            // Entram um a um, da esquerda, como quadro sendo colado na prancha.
            <li
              key={item.href}
              className="entra-esquerda"
              style={{ animationDelay: `${120 + i * 70}ms` }}
            >
              <ItemDeMenu item={item} ativo={caminho === item.href} />
            </li>
          ))}
        </ul>

        {/* A tira do que já foi conferido (RF-43) veio do balão da abertura, que
            estava virando depósito. Aqui ela é o que sempre foi: um atalho. O
            `hidden lg:block` existe porque em tela baixa ela espremeria a frase
            do rodapé, e a navegação vem antes do feed. */}
        {/* A tira entra só em tela alta. A régua é a altura, não a largura: num
            notebook de 768px de altura ela empurraria a frase do rodapé para
            fora, e a navegação vem antes do feed. */}
        <div className="relative mt-6 hidden px-4 [@media(min-height:820px)]:block">
          <UltimasChecagens compacto naBarra />
        </div>

        {/* A frase da casa, num balão: é fala da Vera, e fala da Vera mora em
            balão. Solta sobre o vermelho, ela parecia um rodapé esquecido. */}
        <div className="relative mt-auto px-4 pb-10">
          {/* Em letreiro, e não na letra de mão: a Patrick Hand é fina demais
              para um balão pequeno sobre vermelho, e a frase é um grito de
              parede, não um bilhete. */}
          <p className="relative rounded-lg border-[3px] border-tinta bg-papel-2 px-4 py-2.5 font-display text-2xl leading-none text-tinta shadow-bloco-sm">
            Aqui ninguém repassa sem conferir!
            <span
              aria-hidden
              className="absolute -bottom-[15px] left-7 h-0 w-0 border-x-[11px] border-t-[16px] border-x-transparent border-t-tinta"
            />
            <span
              aria-hidden
              className="absolute -bottom-[10px] left-[30px] h-0 w-0 border-x-[8px] border-t-[12px] border-x-transparent border-t-[var(--papel-2)]"
            />
          </p>
        </div>
      </nav>

      {/* Barra inferior, no celular */}
      <nav
        aria-label="Navegação principal"
        className="fixed inset-x-0 bottom-0 z-40 flex justify-around border-t-[3px] border-tinta bg-vermelho px-1 py-1.5 text-white md:hidden"
      >
        {ITENS.map((item) => {
          const ativo = caminho === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              aria-current={ativo ? "page" : undefined}
              className={`flex min-h-11 flex-1 flex-col items-center justify-center gap-0.5 rounded-md px-1 py-1 text-[10px] ${
                ativo ? "bg-white/25 font-bold" : "text-white/85"
              }`}
            >
              {item.icone}
              {/* Rótulo curto: "Configurações" não cabe num sexto de 360px, e
                  cortado no meio não ajuda ninguém. */}
              <span className="leading-none">{item.curto}</span>
            </Link>
          );
        })}
        {/* No celular não existe a coluna lateral, então o alternador de tema
            mora aqui: sem ele, quem trocou de tema não tem como voltar. */}
        <AlternarTema className="self-center" />
      </nav>
    </>
  );
}

function ItemDeMenu({ item, ativo }: { item: Item; ativo: boolean }) {
  return (
    <Link
      href={item.href}
      aria-current={ativo ? "page" : undefined}
      /* O item ativo ganha traço preto e sombra de bloco, como todo elemento
         que "fala" no produto; os outros ficam discretos de propósito, senão
         nenhum se destaca. */
      className={`flex items-center gap-3 rounded-md px-4 py-3 text-base transition-colors ${
        ativo
          ? "border-[3px] border-tinta bg-papel-2 font-display text-xl text-tinta shadow-bloco-sm"
          : "border-[3px] border-transparent font-semibold text-white/90 hover:bg-white/10"
      }`}
    >
      {item.icone}
      {item.rotulo}
    </Link>
  );
}
