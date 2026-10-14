import { UltimasChecagens } from "@/components/home/UltimasChecagens";

export const metadata = {
  title: "O que eu já conferi · Vera",
};

/**
 * Histórico das checagens (RF-43).
 *
 * A tira completa mora aqui. Ela já esteve embaixo do chat na página inicial e
 * foi tirada de lá porque a primeira tela tem de caber sem rolagem — mas o
 * conteúdo é bom, e o "Ver tudo" da barra lateral já apontava para este
 * endereço, que até então não existia e dava 404.
 */
export default function Historico() {
  return (
    <div className="mx-auto w-full max-w-5xl px-4 py-8 md:px-8">
      <h1 className="font-display text-3xl">O que eu já conferi</h1>
      <p className="mt-1 text-base text-tinta-2">
        Dá uma espiada antes de acreditar: muita mentira volta a circular do
        mesmo jeitinho.
      </p>

      <div className="mt-6">
        <UltimasChecagens />
      </div>
    </div>
  );
}
