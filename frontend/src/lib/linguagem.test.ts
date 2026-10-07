/** Testes da tradução dos sinais para a conversa (RF-02, issue #26). */

import { describe, expect, it } from "vitest";

import {
  explicarEmLinguagemSimples,
  falaDoSinal,
  juntarFrases,
  sinalAponta,
} from "./linguagem";
import type { Sinal } from "@/types/checagem";

function sinal(id: string, score: number | null): Sinal {
  return {
    id,
    nome: "nome técnico do sinal",
    peso: 10,
    dimensao: "conteudo",
    camada: "N2",
    score,
    // `aferido` acompanha o score: medido com valor é sempre aferido. Os casos de
    // "olhei e não achei nada" vivem nos testes do backend, que é quem decide.
    aferido: score !== null,
    justificativa: "justificativa técnica",
  };
}

describe("sinalAponta", () => {
  it("score alto aponta a favor", () => {
    expect(sinalAponta(sinal("S-06", 0.9))).toBe("favor");
  });

  it("score baixo aponta contra", () => {
    expect(sinalAponta(sinal("S-06", 0.1))).toBe("contra");
  });

  it("score nulo é indisponível", () => {
    // RN-06: sem dado não é "contra", é ausência.
    expect(sinalAponta(sinal("S-06", null))).toBe("indisponivel");
  });

  it("exatamente 0,5 conta como a favor", () => {
    expect(sinalAponta(sinal("S-06", 0.5))).toBe("favor");
  });
});

describe("falaDoSinal", () => {
  it("devolve a frase de acordo com a direção", () => {
    expect(falaDoSinal(sinal("S-03", 0.1))).toContain("nasceu ontem");
    expect(falaDoSinal(sinal("S-03", 0.9))).toContain("bastante tempo");
  });

  it("não fala de sinal sem dado", () => {
    expect(falaDoSinal(sinal("S-03", null))).toBeNull();
  });

  it("devolve null para sinal fora do catálogo", () => {
    expect(falaDoSinal(sinal("S-99", 0.9))).toBeNull();
  });

  it("nenhuma frase contém jargão de machine learning", () => {
    // O critério de aceite de #26 é explícito quanto a isto.
    const jargao = /tf-idf|svm|classificador|score|limiar|cobertura|modelo|nli/i;
    const ids = [
      "S-01", "S-02", "S-03", "S-04", "S-05", "S-06", "S-07",
      "S-08", "S-09", "S-10", "S-11", "S-12", "S-13",
    ];

    for (const id of ids) {
      for (const score of [0.1, 0.9]) {
        const fala = falaDoSinal(sinal(id, score));
        expect(fala).not.toBeNull();
        expect(fala!).not.toMatch(jargao);
      }
    }
  });
});

describe("juntarFrases", () => {
  it("uma frase fica sozinha", () => {
    expect(juntarFrases(["uma"])).toBe("uma");
  });

  it("duas frases levam 'e'", () => {
    expect(juntarFrases(["uma", "duas"])).toBe("uma e duas");
  });

  it("três frases levam vírgula e 'e'", () => {
    expect(juntarFrases(["uma", "duas", "três"])).toBe("uma, duas e três");
  });

  it("lista vazia devolve string vazia", () => {
    expect(juntarFrases([])).toBe("");
  });
});

describe("explicarEmLinguagemSimples", () => {
  it("separa o que pesou contra do que pesou a favor", () => {
    const texto = explicarEmLinguagemSimples([
      sinal("S-03", 0.1),
      sinal("S-01", 0.9),
    ]);

    expect(texto).toContain("de pé atrás");
    expect(texto).toContain("a favor");
  });

  it("só sinais contra não inventa seção a favor", () => {
    const texto = explicarEmLinguagemSimples([sinal("S-03", 0.1)]);

    expect(texto).toContain("de pé atrás");
    expect(texto).not.toContain("jogou a favor");
  });

  it("ignora sinais sem dado", () => {
    expect(explicarEmLinguagemSimples([sinal("S-03", null)])).toBe("");
  });

  it("devolve vazio sem sinais, para a interface cair na explicação da API", () => {
    expect(explicarEmLinguagemSimples([])).toBe("");
  });

  it("respeita o limite de frases por lado", () => {
    const muitos = ["S-01", "S-02", "S-03", "S-04", "S-05"].map((id) =>
      sinal(id, 0.1),
    );
    const texto = explicarEmLinguagemSimples(muitos, 2);

    // Duas frases unidas por "e" têm exatamente uma vírgula a menos.
    expect(texto.split(",").length).toBeLessThanOrEqual(2);
  });
});
