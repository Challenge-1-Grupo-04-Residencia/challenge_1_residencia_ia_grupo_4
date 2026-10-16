import type { Metadata } from "next";

import { Apresentacao } from "@/components/sobre/Apresentacao";

export const metadata: Metadata = {
  title: "Apresentação · Vera",
  description:
    "Quem é a Vera, como ela investiga em camadas, o que ela mede e quem a construiu.",
};

/**
 * Rota da apresentação do projeto. O conteúdo vive em `Apresentacao` (Client Component,
 * porque usa componentes com contexto do React); aqui ficamos só com o `metadata`.
 */
export default function Sobre() {
  return <Apresentacao />;
}
