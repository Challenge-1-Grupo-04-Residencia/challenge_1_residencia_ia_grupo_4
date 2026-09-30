/**
 * Contrato da API da Vera (`POST /api/v1/checar`).
 *
 * Espelha `backend/src/main.py`. Mudanças no backend precisam ser refletidas aqui —
 * é o único ponto do frontend que conhece o formato da resposta.
 */

/** As três dimensões de sinais: fonte, conteúdo e corroboração. */
export type Dimensao = "fonte" | "conteudo" | "corroboracao";

/** Camada em que a checagem parou. Define a dificuldade. */
export type Camada = "N0" | "N1" | "N2" | "N3" | "N4";

export type Dificuldade = "facil" | "mediano" | "dificil";

/**
 * Rótulos da faixa de veracidade. Nunca afirmam certeza absoluta (RN-12).
 */
export type Faixa =
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
  justificativa: string;
}

/** Notícia semelhante encontrada na corroboração (N3). */
export interface DocumentoRelacionado {
  titulo: string;
  url: string | null;
  fonte: string;
  similaridade: number;
  fonte_confiavel: boolean;
  data_publicacao: string | null;
}

export interface ChecagemRequest {
  texto: string;
  url?: string | null;
}

export interface ChecagemResponse {
  /** `null` quando uma regra de negócio suprime a porcentagem (opinião, sátira). */
  veracidade: number | null;
  confianca: number;
  faixa: Faixa;
  camada_parada: Camada;
  dificuldade: Dificuldade;
  explicacao: string;
  /** RN-03: falso para opinião e sátira, que não recebem porcentagem. */
  exibe_porcentagem: boolean;
  /** ID da regra que sobrepôs o score calculado, se houver (ex.: "RN-01"). */
  regra_aplicada: string | null;
  /** Fração do peso total dos sinais que foi observada. */
  cobertura: number;
  principais_sinais: Sinal[];
  sinais: Sinal[];
  documentos_relacionados: DocumentoRelacionado[];
  fontes_citadas: string[];
}
