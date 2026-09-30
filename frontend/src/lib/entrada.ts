/**
 * Reconhecimento do tipo de entrada (RF-01).
 *
 * A pessoa cola um link, um texto inteiro ou digita uma afirmação, sem se preocupar em
 * dizer qual é qual. Classificar é trabalho da interface, não de quem pergunta — e o
 * tipo muda o que mandamos para a API e o que mostramos enquanto ela investiga.
 */

export type TipoDeEntrada = "link" | "texto" | "afirmacao";

/** Um link sozinho: nada além da URL, possivelmente com espaços em volta. */
const SO_UMA_URL = /^https?:\/\/\S+$/i;

/** URL em qualquer posição, para o caso de link colado junto com comentário. */
const CONTEM_URL = /https?:\/\/\S+/i;

/**
 * Acima deste número de palavras tratamos como texto de notícia, e não como uma
 * afirmação digitada. O corte vem do mínimo que a camada N2 exige para o classificador
 * de estilo ser confiável — abaixo disso ela deixa S-06 indisponível de qualquer forma.
 */
const PALAVRAS_PARA_SER_TEXTO = 25;

export interface EntradaClassificada {
  tipo: TipoDeEntrada;
  /** O texto normalizado que vai para a API. */
  texto: string;
  /** Preenchido só quando há uma URL a investigar. */
  url: string | null;
}

/** Extrai a primeira URL do texto, se houver. */
export function extrairUrl(entrada: string): string | null {
  const achado = entrada.match(CONTEM_URL);
  return achado ? achado[0] : null;
}

export function contarPalavras(entrada: string): number {
  const limpo = entrada.trim();
  return limpo ? limpo.split(/\s+/).length : 0;
}

/**
 * Classifica o que a pessoa enviou.
 *
 * Um link colado junto de um comentário conta como `link`: a URL é o que a Vera
 * consegue investigar a fundo, e ignorá-la desperdiçaria a camada de fonte.
 */
export function classificarEntrada(entrada: string): EntradaClassificada {
  const texto = entrada.trim();
  const url = extrairUrl(texto);

  if (SO_UMA_URL.test(texto)) {
    return { tipo: "link", texto, url: texto };
  }
  if (url) {
    return { tipo: "link", texto, url };
  }
  if (contarPalavras(texto) >= PALAVRAS_PARA_SER_TEXTO) {
    return { tipo: "texto", texto, url: null };
  }
  return { tipo: "afirmacao", texto, url: null };
}

/** O que a interface diz de volta, para a pessoa ver que foi entendida. */
export const DICA_POR_TIPO: Record<TipoDeEntrada, string> = {
  link: "Isso é um link — vou abrir e ler a página.",
  texto: "Isso é o texto da notícia — vou analisar como foi escrito.",
  afirmacao: "Isso é uma afirmação — vou procurar quem já falou sobre ela.",
};
