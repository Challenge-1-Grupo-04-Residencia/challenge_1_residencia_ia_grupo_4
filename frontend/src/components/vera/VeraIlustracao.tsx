/**
 * O retrato da Vera de meio corpo, para abertura e estados de espera.
 *
 * Duas poses, e cada uma diz uma coisa (ver skill `vera-estilo`):
 *
 * - **apontando** — dedo em riste, de quem está explicando. É a pose de quem
 *   ensina, e serve à abertura, ao estado vazio e à dica de segurança.
 * - **queixo** — mão no queixo, avaliando. É a pose de quem está conferindo, e
 *   serve à investigação em curso e ao resultado.
 *
 * A pose não é apavorada de propósito: quem checa fato não se assusta com a
 * notícia, examina. Uma Vera de olhos arregalados passaria a mensagem contrária
 * à do produto.
 */

import Image from "next/image";

import type { HumorDaVera } from "@/lib/veracidade";

export type PoseDaVera = "apontando" | "queixo";

interface Props {
  pose?: PoseDaVera;
  humor?: HumorDaVera;
  /** Largura em pixels; a altura sai da proporção da arte. */
  tamanho?: number;
  className?: string;
  /** Para passar `--atraso` na orquestração de entrada. */
  style?: React.CSSProperties;
  prioridade?: boolean;
  /**
   * Deixa o tamanho por conta do CSS da classe.
   *
   * Sem isso, o componente fixa a largura no estilo embutido; se a classe mexer
   * só na altura, o Next avisa que a imagem teve uma dimensão alterada sem a
   * outra, e a proporção realmente fica por conta da sorte.
   */
  ajusteLivre?: boolean;
}

const ARTE: Record<PoseDaVera, { src: string; largura: number; altura: number }> = {
  apontando: { src: "/vera-corpo-apontando.png", largura: 1190, altura: 1200 },
  queixo: { src: "/vera-corpo.png", largura: 1113, altura: 1014 },
};

const DESCRICAO: Record<PoseDaVera, string> = {
  apontando: "Senhora Vera com o dedo em riste, explicando",
  queixo: "Senhora Vera com a mão no queixo, avaliando a história",
};

export function VeraIlustracao({
  pose = "apontando",
  tamanho = 300,
  className = "",
  style,
  prioridade = false,
  ajusteLivre = false,
}: Props) {
  const arte = ARTE[pose];

  return (
    <Image
      src={arte.src}
      alt={DESCRICAO[pose]}
      width={arte.largura}
      height={arte.altura}
      sizes={`${tamanho}px`}
      priority={prioridade}
      className={className}
      style={ajusteLivre ? style : { width: tamanho, height: "auto", ...style }}
    />
  );
}
