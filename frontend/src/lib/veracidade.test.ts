/**
 * Testes da apresentação do veredito (RF-05, RN-03, RN-12).
 *
 * O que está sendo protegido aqui não é estética: é o contrato de que a tela
 * sempre diz a faixa oficial por escrito, sempre tem um pictograma para quem lê
 * com dificuldade, e nunca inventa uma sexta faixa de veracidade.
 */

import { describe, expect, it } from "vitest";

import {
  CASAS_DO_TERMOMETRO,
  ORDEM_DAS_FAIXAS,
  estiloDaFaixa,
} from "./veracidade";
import type { Faixa } from "@/types/checagem";

describe("estiloDaFaixa", () => {
  it("toda faixa tem pictograma e palavra curta", () => {
    // Cor sozinha não carrega informação: vermelho e verde é justamente o eixo
    // que quem tem daltonia perde.
    for (const faixa of ORDEM_DAS_FAIXAS) {
      const estilo = estiloDaFaixa(faixa);
      expect(estilo.icone, faixa).toBeTruthy();
      expect(estilo.palavra.length, faixa).toBeGreaterThan(0);
    }
  });

  it("a palavra curta cabe em três palavras", () => {
    for (const faixa of ORDEM_DAS_FAIXAS) {
      expect(
        estiloDaFaixa(faixa).palavra.split(" ").length,
        faixa,
      ).toBeLessThanOrEqual(3);
    }
  });

  it("a palavra curta nunca crava certeza absoluta", () => {
    // RN-12: a Vera não afirma. O carimbo pode ser curto, mas não pode dizer
    // "MENTIRA" nem "VERDADE" como fato consumado.
    const proibidas = ["MENTIRA", "FALSA", "VERDADEIRO", "CONFIRMADO", "PROVADO"];
    for (const faixa of ORDEM_DAS_FAIXAS) {
      const palavra = estiloDaFaixa(faixa).palavra;
      for (const proibida of proibidas) {
        expect(palavra.split(" "), `${faixa}: ${palavra}`).not.toContain(proibida);
      }
    }
  });

  it("faixa desconhecida cai em inconclusiva, não em falsa", () => {
    // Acusar de falsidade o que não se sabe medir é o erro que a RN-06 existe
    // para evitar, e ele também vale para a apresentação.
    expect(estiloDaFaixa("Sei lá" as Faixa)).toBe(estiloDaFaixa("Inconclusiva"));
  });
});

describe("CASAS_DO_TERMOMETRO", () => {
  it("tem exatamente as cinco faixas, na ordem da classificação", () => {
    expect(CASAS_DO_TERMOMETRO.map((c) => c.faixa)).toEqual(ORDEM_DAS_FAIXAS);
  });

  it("não inclui a conversa, que não é resultado de checagem", () => {
    expect(CASAS_DO_TERMOMETRO.map((c) => c.faixa)).not.toContain("Conversa");
  });
});
