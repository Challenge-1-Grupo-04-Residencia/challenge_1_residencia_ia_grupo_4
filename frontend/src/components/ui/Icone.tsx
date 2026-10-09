/**
 * Os pictogramas da Vera (ver skill `vera-gamificacao`).
 *
 * O desenho vem do **Phosphor**, no peso `fill`: formas cheias, cantos
 * arredondados e silhueta grossa, que é o vocabulário de cartoon. A primeira
 * versão era um conjunto desenhado à mão aqui mesmo, em traço de 2px — ficava
 * fino, irregular entre um ícone e outro, e destoava do contorno pesado da arte
 * da personagem.
 *
 * O nome do ícone continua sendo o **significado**, não o desenho: a tela pede
 * "aFavor", não "polegar para cima". Trocar de biblioteca outra vez é mexer
 * neste arquivo e em nenhum outro.
 *
 * Emoji continua proibido: muda de cara em cada aparelho, some em Android
 * antigo, e o leitor de tela anuncia "rosto levemente franzido" no meio de um
 * veredito. O ícone é sempre `aria-hidden` — ele nunca aparece sozinho, a
 * palavra escrita vem do lado.
 */

import {
  Browser,
  CalendarBlank,
  ChatCircleDots,
  CheckCircle,
  Checks,
  Clock,
  Copy,
  Detective,
  HandPalm,
  Hourglass,
  LinkSimple,
  ListChecks,
  MagnifyingGlass,
  Megaphone,
  Newspaper,
  Question,
  Robot,
  Tag,
  TextAlignLeft,
  ThumbsDown,
  ThumbsUp,
  UserCircle,
  Warning,
  ArrowRight,
  HeartStraight,
  MinusCircle,
  type Icon,
} from "@phosphor-icons/react";
import type { ComponentProps } from "react";

/** Nome de cada pictograma. O nome diz o que ele significa, não como é desenhado. */
export type NomeDoIcone =
  // Veredito
  | "mentira"
  | "duvida"
  | "espera"
  | "quase"
  | "verdade"
  | "conversa"
  // Direção de um sinal
  | "aFavor"
  | "contra"
  | "semDado"
  // Sinais
  | "site"
  | "alerta"
  | "calendario"
  | "etiqueta"
  | "assinatura"
  | "texto"
  | "megafone"
  | "coracao"
  | "link"
  | "robo"
  | "jornal"
  | "lupa"
  | "copia"
  // Interface
  | "visto"
  | "seta"
  | "relogio"
  | "contas";

const DESENHOS: Record<NomeDoIcone, Icon> = {
  mentira: HandPalm,
  duvida: Question,
  espera: Hourglass,
  quase: Checks,
  verdade: CheckCircle,
  conversa: ChatCircleDots,

  aFavor: ThumbsUp,
  contra: ThumbsDown,
  semDado: MinusCircle,

  site: Browser,
  alerta: Warning,
  calendario: CalendarBlank,
  etiqueta: Tag,
  assinatura: UserCircle,
  texto: TextAlignLeft,
  megafone: Megaphone,
  coracao: HeartStraight,
  link: LinkSimple,
  robo: Robot,
  jornal: Newspaper,
  // A lupa de busca genérica virou o detetive: é o gesto da Vera, que investiga
  // em vez de pesquisar, e tem silhueta própria mesmo em 18px.
  lupa: Detective,
  copia: Copy,

  visto: Checks,
  seta: ArrowRight,
  relogio: Clock,
  contas: ListChecks,
};

interface Props extends Omit<ComponentProps<Icon>, "size" | "weight"> {
  nome: NomeDoIcone;
  /** Lado do quadrado, em pixels. Mínimo de 24 — ver `vera-gamificacao`. */
  tamanho?: number;
}

export function Icone({ nome, tamanho = 24, ...resto }: Props) {
  const Desenho = DESENHOS[nome];

  return (
    <Desenho
      size={tamanho}
      weight="fill"
      aria-hidden
      focusable="false"
      {...resto}
    />
  );
}

/** A lupa de busca, que é outra coisa: procurar, não investigar. */
export function IconeDeBusca({ tamanho = 20, ...resto }: Omit<Props, "nome">) {
  return <MagnifyingGlass size={tamanho} weight="bold" aria-hidden {...resto} />;
}
