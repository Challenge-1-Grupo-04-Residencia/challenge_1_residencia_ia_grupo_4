/**
 * Página inicial.
 *
 * A ordem responde a duas pessoas diferentes: quem chega com uma dúvida
 * específica encontra a busca no topo; quem chega sem dúvida nenhuma encontra o
 * feed logo abaixo, e se informa de forma preventiva (RF-43).
 */

import { DicaDeSeguranca } from "@/components/home/DicaDeSeguranca";
import { Hero } from "@/components/home/Hero";
import { UltimasChecagens } from "@/components/home/UltimasChecagens";
import { Tour } from "@/components/onboarding/Tour";

export default function Home() {
  return (
    <>
      <Hero />

      {/* O card sobe sobre a faixa vermelha, como no protótipo. */}
      {/* `relative z-10`: sem isso a margem negativa esconde o topo do cartão
          atrás da faixa vermelha, que é pintada depois. */}
      <div className="relative z-10 mx-auto -mt-16 w-full max-w-6xl px-4 pb-10 md:-mt-20 md:px-8">
        <div className="grid gap-5 lg:grid-cols-[1.6fr_1fr]">
          <div data-tour="feed">
            <UltimasChecagens />
          </div>
          <div data-tour="dica">
            <DicaDeSeguranca />
          </div>
        </div>
      </div>
      <Tour />
    </>
  );
}
