/**
 * Faixa de abertura: a Vera se apresenta num balão de fala.
 *
 * O balão diz **uma** coisa: quem ela é e o que fazer. Ele já carregou também as
 * três promessas da checagem, a tira do que já foi conferido e a dica de
 * segurança — e virou um depósito: quatro assuntos empilhados num cartão só,
 * numa faixa vermelha que tomava metade da tela.
 *
 * Cada um foi para onde pertence: as promessas ficam junto da caixa de
 * pergunta, porque descrevem o que ela devolve; a tira do que já foi conferido
 * foi para a navegação lateral, que é onde moram os atalhos; a dica fecha o
 * chat. Aqui ficou só a apresentação, e a faixa encolheu junto.
 */

import { Icone } from "@/components/ui/Icone";
import { VeraIlustracao } from "@/components/vera/VeraIlustracao";

interface Props {
  /** Abre a abertura em quadrinhos de novo. */
  aoRever?: () => void;
  /** Classes de layout de quem a coloca na página (a altura, por exemplo). */
  className?: string;
}

export function Hero({ aoRever, className = "" }: Props) {
  return (
    <section
      className={`relative flex items-end overflow-hidden bg-vermelho px-4 pb-0 pt-3 text-white md:px-8 ${className}`}
    >
      {/* Retícula de quadrinho, e o jornal ao fundo como marca-d'água. */}
      <div className="reticula pointer-events-none absolute inset-0 text-white" aria-hidden />

      {/* `items-end` com a Vera sem margem embaixo: ela encosta na base da faixa
          vermelha, como quem está apoiada nela. Flutuando acima da borda, a arte
          parecia um adesivo colado por engano. */}
      <div className="relative mx-auto flex h-full w-full max-w-5xl items-end gap-3 md:gap-6">
        <div className="estufa relative mb-4 min-w-0 flex-1">
          <div className="rounded-lg border-[3px] border-tinta bg-papel-2 p-3 text-tinta shadow-bloco md:p-4">
            <div className="flex items-baseline justify-between gap-3">
              <p className="font-display text-3xl leading-none md:text-4xl">
                Oi, meu bem!
              </p>
              {/* Alvo de 44px, e não um link de 20: no celular este botão é a
                  **única** porta de volta para a abertura, que só roda sozinha
                  uma vez por aparelho. Como texto solto, ele era pequeno demais
                  para o dedo acertar — e quem não acertava ficava sem jeito
                  nenhum de rever a história. */}
              {aoRever && (
                <button
                  type="button"
                  onClick={aoRever}
                  aria-label="Ver a história da Vera de novo"
                  className="surge -mr-1 flex min-h-11 shrink-0 items-center gap-1.5 rounded-total border-2 border-vermelho px-3 text-sm font-bold text-vermelho hover:bg-vermelho hover:text-white"
                  style={{ "--atraso": "460ms" } as React.CSSProperties}
                >
                  <Icone nome="conversa" tamanho={18} />
                  Minha história
                </button>
              )}
            </div>

            <p className="mt-1.5 text-base leading-snug text-tinta-2">
              Eu sou a Vera. Eu sei de tudo, mas só depois de conferir. Chegou
              notícia esquisita no grupo da família? Me manda aqui embaixo.
            </p>

            <span className="risco mt-2 block h-1 w-40 rounded-full bg-vermelho" aria-hidden />
          </div>

          {/* Rabicho apontando para a Vera. */}
          <span
            aria-hidden
            className="absolute -bottom-[18px] right-10 hidden h-0 w-0 border-x-[14px] border-t-[20px] border-x-transparent border-t-tinta md:block"
          />
          <span
            aria-hidden
            className="absolute -bottom-[12px] right-[46px] hidden h-0 w-0 border-x-[10px] border-t-[15px] border-x-transparent border-t-[var(--papel-2)] md:block"
          />
        </div>

        {/* A arte ocupa a altura que sobrou da faixa, e não um tamanho fixo: a
            faixa cresce até onde o chat permite, e a Vera cresce com ela. Em
            tela baixa, ela encolhe em vez de empurrar a caixa de pergunta para
            fora da primeira dobra. */}
        <VeraIlustracao
          pose="apontando"
          tamanho={340}
          prioridade
          ajusteLivre
          className="surge hidden h-full max-h-[300px] w-auto max-w-[42%] self-end object-contain sm:block"
          style={{ "--atraso": "150ms" } as React.CSSProperties}
        />
      </div>
    </section>
  );
}
