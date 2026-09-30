/**
 * Faixa de abertura: a Vera se apresenta num balão de fala.
 *
 * É o único momento de exagero visual da tela — traço grosso, retícula de
 * pontos, letra à mão. Tudo que vem depois é discreto de propósito: se a página
 * inteira gritasse, nada se destacaria, e o que precisa se destacar é o
 * resultado de uma checagem.
 */

import { VeraIlustracao } from "@/components/vera/VeraIlustracao";

export function Hero() {
  return (
    <section className="relative overflow-hidden bg-vermelho px-4 pb-24 pt-8 text-white md:px-8 md:pb-28">
      {/* Retícula de quadrinho, e o jornal ao fundo como marca-d'água. */}
      <div className="reticula pointer-events-none absolute inset-0 text-white" aria-hidden />
      <svg
        viewBox="0 0 120 90"
        className="pointer-events-none absolute -right-4 bottom-2 h-44 w-56 opacity-15 md:h-56 md:w-72"
        aria-hidden
      >
        <rect x="8" y="12" width="104" height="70" rx="3" fill="none" stroke="currentColor" strokeWidth="3" />
        <rect x="16" y="22" width="40" height="26" fill="currentColor" opacity="0.5" />
        <path d="M64 24h40M64 32h40M64 40h30M16 56h88M16 64h88M16 72h60" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
      </svg>

      <div className="relative mx-auto flex max-w-6xl flex-col items-center gap-6 md:flex-row md:items-start md:gap-10">
        {/* Balão de fala */}
        <div className="estufa relative w-full max-w-lg">
          <div className="rounded-lg border-[3px] border-tinta bg-papel-2 p-5 text-tinta shadow-bloco md:p-6">
            <p className="font-display text-4xl font-extrabold leading-none">
              Oi, meu bem!
            </p>
            <p className="mt-2 font-display text-xl font-semibold leading-snug">
              Eu sou a Vera. Eu sei de tudo — mas só depois de conferir.
            </p>
            <p className="mt-3 text-base leading-relaxed text-tinta-2">
              Chegou aquela notícia no grupo da família e te deu uma pulga atrás
              da orelha? Cola aqui embaixo. Eu ligo pras minhas comadres, confiro
              com quem é sério e te conto o que descobri — e de onde eu tirei.
            </p>
            <span className="risco mt-3 block h-1 w-40 rounded-full bg-vermelho" aria-hidden />
          </div>

          {/* Rabicho apontando para a Vera. */}
          <span
            aria-hidden
            className="absolute -bottom-[18px] left-16 hidden h-0 w-0 border-x-[14px] border-t-[20px] border-x-transparent border-t-tinta md:block"
          />
          <span
            aria-hidden
            className="absolute -bottom-[12px] left-[70px] hidden h-0 w-0 border-x-[10px] border-t-[15px] border-x-transparent border-t-[var(--papel-2)] md:block"
          />
        </div>

        <div className="flex flex-1 items-start justify-center gap-4">
          <VeraIlustracao
            humor="desconfiada"
            tamanho={260}
            className="surge balanca shrink-0"
            style={{ "--atraso": "150ms" } as React.CSSProperties}
          />

          <p
            className="surge fonte-mao hidden max-w-[10rem] pt-6 text-3xl leading-tight lg:block"
            style={{ "--atraso": "350ms" } as React.CSSProperties}
          >
            Informação boa também é poder, visse?
            <span className="mt-1 block h-0.5 w-28 bg-white/80" aria-hidden />
          </p>
        </div>
      </div>
    </section>
  );
}
