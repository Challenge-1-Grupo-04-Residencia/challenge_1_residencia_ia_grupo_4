/**
 * Contrato da API da Vera (`POST /api/v1/checar`).
 *
 * Espelha `backend/src/main.py`. Mudanças no backend precisam ser refletidas aqui —
 * é o único ponto do frontend que conhece o formato da resposta.
 */

/** As três dimensões de sinais: fonte, conteúdo e corroboração. */
export type Dimensao = "fonte" | "conteudo" | "corroboracao";

/**
 * Camada em que a checagem parou. Define a dificuldade.
 *
 * `TRIAGEM` significa que não houve checagem: a entrada era conversa, não alegação de
 * fato, e o pipeline não rodou.
 */
export type Camada = "TRIAGEM" | "N0" | "N1" | "N2" | "N3" | "N4";

export type Dificuldade = "facil" | "mediano" | "dificil";

/**
 * Rótulos da faixa de veracidade. Nunca afirmam certeza absoluta (RN-12).
 */
export type Faixa =
  /** Não houve checagem: a entrada era saudação ou conversa, não notícia. */
  | "Conversa"
  | "Provavelmente falsa"
  | "Duvidosa"
  | "Inconclusiva"
  | "Provavelmente verdadeira"
  | "Confirmada por fontes";

/**
 * Um sinal medido. `score` em `null` significa que o dado não foi obtido — o sinal
 * saiu do cálculo (RN-06) em vez de contar como zero.
 */
export interface Sinal {
  id: string;
  nome: string;
  peso: number;
  dimensao: Dimensao;
  camada: Camada;
  score: number | null;
  /**
   * `score: null` com `aferido: true` é "olhei e não havia o que anotar"; com
   * `aferido: false` é "não consegui medir". Só o segundo é lacuna.
   */
  aferido: boolean;
  justificativa: string;
}

/** Notícia semelhante encontrada na corroboração (N3). */
export interface DocumentoRelacionado {
  titulo: string;
  url: string | null;
  fonte: string;
  similaridade: number;
  /**
   * `false` quando a `similaridade` é só a posição no ranking do buscador, e não
   * comparação entre os textos. Não a apresente como "x% parecido" nesse caso.
   */
  similaridade_textual: boolean;
  fonte_confiavel: boolean;
  data_publicacao: string | null;
}

export interface ChecagemRequest {
  texto: string;
  url?: string | null;
}

export interface ChecagemResponse {
  /** Identificador desta checagem, usado nas perguntas de acompanhamento (RF-04). */
  id: string;
  /**
   * `null` quando uma regra de negócio suprime a porcentagem (opinião, sátira) ou
   * quando a entrada não era uma alegação de fato.
   */
  veracidade: number | null;
  confianca: number;
  faixa: Faixa;
  camada_parada: Camada;
  dificuldade: Dificuldade;
  explicacao: string;
  /** RN-03: falso para opinião, sátira e para entrada que não é notícia. */
  exibe_porcentagem: boolean;
  /** ID da regra que sobrepôs o score calculado, se houver (ex.: "RN-01"). */
  regra_aplicada: string | null;
  /** Fração do que as camadas existentes sabem medir que foi observada. */
  cobertura: number;
  /**
   * Fração dos 100 pontos do catálogo completo que foi observada. Menor que
   * `cobertura` enquanto houver camada não implementada.
   */
  cobertura_do_catalogo: number;
  principais_sinais: Sinal[];
  sinais: Sinal[];
  documentos_relacionados: DocumentoRelacionado[];
  fontes_citadas: string[];
}

/** Temas que a Vera reconhece numa pergunta de acompanhamento (RF-04). */
export type AssuntoDaPergunta =
  | "motivo"
  | "fontes"
  | "estilo"
  | "confianca"
  | "lacunas"
  | "geral";

export interface PerguntaRequest {
  id_checagem: string;
  pergunta: string;
}

export interface RespostaResponse {
  texto: string;
  assunto: AssuntoDaPergunta;
  /** URLs citadas na resposta, para a interface linká-las (RN-05). */
  fontes: string[];
  /** IDs dos sinais em que a resposta se apoia, para auditoria (RF-33). */
  sinais_citados: string[];
}

/** Cartão do feed de últimas checagens (RF-43). */
export interface ChecagemDoFeed {
  id: string;
  trecho: string;
  url: string | null;
  veracidade: number | null;
  faixa: Faixa;
  exibe_porcentagem: boolean;
  confianca: number;
  camada_parada: Camada;
  dificuldade: Dificuldade;
  regra_aplicada: string | null;
  /** ISO 8601, em UTC. */
  checada_em: string;
}
