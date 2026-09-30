/**
 * Cliente HTTP da API da Vera.
 *
 * É o único módulo que fala com o backend. Componentes importam daqui e nunca chamam
 * `fetch` direto, para que a URL base, o tratamento de erro e o formato da resposta
 * fiquem em um lugar só.
 */

import type {
  ChecagemDoFeed,
  ChecagemRequest,
  ChecagemResponse,
  RespostaResponse,
} from "@/types/checagem";

const URL_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** Erro de comunicação com a API, já com mensagem na voz da Vera. */
export class ErroDaVera extends Error {
  constructor(
    message: string,
    readonly status?: number,
  ) {
    super(message);
    this.name = "ErroDaVera";
  }
}

/**
 * Envia um texto, link ou afirmação para checagem (RF-01).
 *
 * @throws {ErroDaVera} quando a API responde erro ou está fora do ar.
 */
export async function checar(
  entrada: ChecagemRequest,
  sinal?: AbortSignal,
): Promise<ChecagemResponse> {
  let resposta: Response;

  try {
    resposta = await fetch(`${URL_BASE}/api/v1/checar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(entrada),
      signal: sinal,
    });
  } catch (erro) {
    // Rede fora ou backend desligado: a distinção não importa para quem pergunta.
    if (erro instanceof DOMException && erro.name === "AbortError") throw erro;
    throw new ErroDaVera(
      "Minha internet caiu, acredita? Tenta de novo daqui a pouco.",
    );
  }

  if (!resposta.ok) {
    throw new ErroDaVera(
      resposta.status === 422
        ? "Preciso de um texto ou link para conferir, meu bem."
        : "Deu problema aqui do meu lado. Tenta de novo daqui a pouco.",
      resposta.status,
    );
  }

  return (await resposta.json()) as ChecagemResponse;
}

/** Verifica se a API está no ar. Usado no indicador de status do rodapé. */
export async function health(): Promise<boolean> {
  try {
    const resposta = await fetch(`${URL_BASE}/health`, { cache: "no-store" });
    return resposta.ok;
  } catch {
    return false;
  }
}

/**
 * Pergunta algo sobre um resultado já entregue (RF-04).
 *
 * Usa o `id` da checagem original: o backend responde a partir dos sinais e das
 * evidências que já recuperou, sem refazer a investigação.
 */
export async function perguntar(
  idChecagem: string,
  pergunta: string,
  sinal?: AbortSignal,
): Promise<RespostaResponse> {
  let resposta: Response;

  try {
    resposta = await fetch(`${URL_BASE}/api/v1/perguntar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id_checagem: idChecagem, pergunta }),
      signal: sinal,
    });
  } catch (erro) {
    if (erro instanceof DOMException && erro.name === "AbortError") throw erro;
    throw new ErroDaVera(
      "Minha internet caiu, acredita? Tenta de novo daqui a pouco.",
    );
  }

  if (!resposta.ok) {
    throw new ErroDaVera(
      resposta.status === 404
        ? "Essa checagem eu já não tenho mais aqui comigo. Manda de novo que eu confiro."
        : "Deu problema aqui do meu lado. Tenta de novo daqui a pouco.",
      resposta.status,
    );
  }

  return (await resposta.json()) as RespostaResponse;
}

/**
 * Últimas checagens, para o feed da página inicial (RF-43).
 *
 * Falha em silêncio devolvendo lista vazia: o feed é informação complementar, e não
 * deve impedir a pessoa de usar o chat se a rota estiver fora do ar.
 */
export async function checagensRecentes(
  limite = 8,
): Promise<ChecagemDoFeed[]> {
  try {
    const resposta = await fetch(
      `${URL_BASE}/api/v1/checagens/recentes?limite=${limite}`,
      { cache: "no-store" },
    );
    if (!resposta.ok) return [];
    return (await resposta.json()) as ChecagemDoFeed[];
  } catch {
    return [];
  }
}
