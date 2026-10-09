import { Suspense } from "react";

import { Conversa } from "@/components/checagem/Conversa";

export const metadata = {
  title: "Verificar notícia · Vera",
};

/**
 * Tela de checagem.
 *
 * `Conversa` lê o parâmetro `?q=`, que a busca do topo preenche, e por isso
 * precisa de `Suspense`: no App Router, `useSearchParams` suspende durante a
 * renderização estática.
 */
export default function Checar() {
  return (
    <div className="mx-auto w-full max-w-3xl px-4 py-6 md:px-8">
      <h1 className="font-display text-3xl">Me manda a notícia</h1>
      <p className="mt-1 text-base text-tinta-2">
        Cola o link ou o texto. Eu vou atrás e te mostro de onde tirei cada coisa.
      </p>

      <Suspense fallback={<p className="mt-8 text-tinta-3">Já vou te atender, meu bem…</p>}>
        <Conversa />
      </Suspense>
    </div>
  );
}
