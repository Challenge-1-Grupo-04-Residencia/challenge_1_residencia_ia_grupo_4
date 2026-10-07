/**
 * Cliente HTTP da API da Vera.
 *
 * É o único módulo que fala com o backend. Componentes importam daqui e nunca chamam
 * `fetch` direto, para que a URL base, o tratamento de erro e o formato da resposta
 * fiquem em um lugar só.
 */

import type {
  Camada,
  ChecagemDoFeed,
  ChecagemRequest,
  ChecagemResponse,
  RespostaResponse,
  Sinal,
  TriagemResponse,
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

/**
 * Pergunta à API o que fazer com a mensagem: conversar, acompanhar ou checar (RF-01).
 *
 * A decisão vive no backend de propósito. Aqui ela era tomada pelo número de palavras,
 * e com isso toda alegação com menos de 25 palavras ia para o acompanhamento depois da
 * primeira checagem — e voltava como "essa sua pergunta eu ainda não sei responder".
 *
 * @throws {ErroDaVera} quando a API responde erro ou está fora do ar.
 */
export async function triar(
  texto: string,
  temChecagemAnterior: boolean,
  sinal?: AbortSignal,
): Promise<TriagemResponse> {
  let resposta: Response;

  try {
    resposta = await fetch(`${URL_BASE}/api/v1/triagem`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        texto,
        tem_checagem_anterior: temChecagemAnterior,
      }),
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
      "Deu problema aqui do meu lado. Tenta de novo daqui a pouco.",
      resposta.status,
    );
  }

  return (await resposta.json()) as TriagemResponse;
}

/** Um passo da investigação, como o backend o anuncia (RF-03). */
export interface EtapaDoAndamento {
  tipo: "iniciou" | "concluiu" | "pulou";
  camada: Camada;
  mensagem: string;
  sinais: Sinal[];
}

/**
 * Checa um texto acompanhando o andamento de verdade, etapa por etapa (RF-03).
 *
 * Usa `fetch` e não `EventSource` porque o andamento vem de um `POST`: o
 * `EventSource` só faz `GET`. O corpo chega em pedaços e é cortado nos `\n\n`
 * que separam os eventos do protocolo SSE.
 *
 * A interface mostrava o progresso por temporizador — 400 ms, 1,8 s, 1,2 s, 6 s,
 * 12 s — sem relação com o que a Vera estava fazendo. Com a camada de busca
 * levando de 1 a 25 s e a de inferência dependendo de um modelo externo, o que a
 * pessoa via era ficção.
 *
 * @throws {ErroDaVera} quando a API responde erro ou está fora do ar.
 */
export async function checarComAndamento(
  entrada: ChecagemRequest,
  aoAndar: (etapa: EtapaDoAndamento) => void,
  sinal?: AbortSignal,
): Promise<ChecagemResponse> {
  let resposta: Response;

  try {
    resposta = await fetch(`${URL_BASE}/api/v1/checar/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(entrada),
      signal: sinal,
    });
  } catch (erro) {
    if (erro instanceof DOMException && erro.name === "AbortError") throw erro;
    throw new ErroDaVera(
      "Minha internet caiu, acredita? Tenta de novo daqui a pouco.",
    );
  }

  if (!resposta.ok || !resposta.body) {
    throw new ErroDaVera(
      resposta.status === 422
        ? "Preciso de um texto ou link para conferir, meu bem."
        : "Deu problema aqui do meu lado. Tenta de novo daqui a pouco.",
      resposta.status,
    );
  }

  const leitor = resposta.body.getReader();
  const decodificador = new TextDecoder();
  let restante = "";
  let veredito: ChecagemResponse | null = null;

  while (true) {
    const { done, value } = await leitor.read();
    if (done) break;
    restante += decodificador.decode(value, { stream: true });

    // Os eventos são separados por linha em branco; o último pedaço pode estar
    // cortado no meio e fica no buffer para a próxima volta.
    const blocos = restante.split("\n\n");
    restante = blocos.pop() ?? "";

    for (const bloco of blocos) {
      const tipo = bloco.match(/^event: (.+)$/m)?.[1];
      const dados = bloco.match(/^data: (.+)$/m)?.[1];
      if (!tipo || !dados) continue;

      if (tipo === "etapa") {
        aoAndar(JSON.parse(dados) as EtapaDoAndamento);
      } else if (tipo === "veredito") {
        veredito = JSON.parse(dados) as ChecagemResponse;
      } else if (tipo === "falhou") {
        throw new ErroDaVera(
          (JSON.parse(dados) as { mensagem: string }).mensagem,
        );
      }
    }
  }

  if (!veredito) {
    throw new ErroDaVera(
      "A conversa caiu no meio da investigação. Tenta de novo?",
    );
  }
  return veredito;
}
