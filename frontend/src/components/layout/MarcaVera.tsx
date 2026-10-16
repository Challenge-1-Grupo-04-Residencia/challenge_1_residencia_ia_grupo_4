/**
 * Marca da Vera: o rosto dela num emblema, e o nome em letreiro.
 *
 * Era uma lupa com um visto dentro — o desenho certo para um checador genérico,
 * e errado para este: a Vera **tem** rosto, e é o rosto que as pessoas
 * reconhecem no grupo da família. Uma lupa de traço fino também destoava do
 * resto, que é todo contorno grosso.
 *
 * O emblema continua servindo de marca-d'água sem o nome, por isso o desenho é
 * separado do texto.
 */

import Image from "next/image";

interface Props {
  /** Só o emblema, sem o nome. */
  apenasSimbolo?: boolean;
  className?: string;
}

export function SimboloVera({ tamanho = 48 }: { tamanho?: number }) {
  return (
    <span
      className="inline-flex shrink-0 items-center justify-center overflow-hidden rounded-total border-[3px] border-tinta bg-papel-2 shadow-bloco-sm"
      style={{ width: tamanho, height: tamanho }}
    >
      <Image
        src="/vera-rosto.png"
        alt=""
        width={tamanho}
        height={tamanho}
        className="h-full w-full scale-105 object-contain object-bottom"
        priority
      />
    </span>
  );
}

export function MarcaVera({ apenasSimbolo = false, className = "" }: Props) {
  return (
    <div className={`flex items-center gap-2.5 ${className}`}>
      <SimboloVera />
      {!apenasSimbolo && (
        <div className="leading-none">
          <p className="font-display text-3xl">Vera</p>
          <p className="mt-0.5 text-xs font-bold uppercase tracking-wide opacity-90">
            Verificadora de fatos
          </p>
        </div>
      )}
    </div>
  );
}
