/**
 * Marca da Vera: lupa com um visto dentro, e o nome.
 *
 * A lupa diz "eu vou conferir" e o visto diz "eu confirmo" — juntos são a
 * promessa do produto numa forma só. Serve também como marca-d'água no rodapé da
 * navegação, por isso o desenho é separado do texto.
 */

interface Props {
  /** Só o símbolo, sem o nome. */
  apenasSimbolo?: boolean;
  className?: string;
}

export function SimboloVera({ tamanho = 40 }: { tamanho?: number }) {
  return (
    <svg viewBox="0 0 48 48" width={tamanho} height={tamanho} aria-hidden>
      <circle
        cx="21"
        cy="21"
        r="15"
        fill="none"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        d="M14 21.5l5 5 9-10"
        fill="none"
        stroke="currentColor"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M32 32l10 10"
        stroke="currentColor"
        strokeWidth="5"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function MarcaVera({ apenasSimbolo = false, className = "" }: Props) {
  return (
    <div className={`flex items-center gap-2.5 ${className}`}>
      <SimboloVera />
      {!apenasSimbolo && (
        <div className="leading-none">
          <p className="font-display text-3xl font-extrabold">Vera</p>
          <p className="mt-1 text-sm font-semibold opacity-90">
            Verificadora
            <br />
            de Fatos
          </p>
        </div>
      )}
    </div>
  );
}
