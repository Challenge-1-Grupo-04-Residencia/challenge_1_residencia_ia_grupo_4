/** Testes do reconhecimento de tipo de entrada (RF-01, issue #25). */

import { describe, expect, it } from "vitest";

import { classificarEntrada, contarPalavras, extrairUrl } from "./entrada";

describe("extrairUrl", () => {
  it("acha a URL quando ela está sozinha", () => {
    expect(extrairUrl("https://g1.globo.com/noticia")).toBe(
      "https://g1.globo.com/noticia",
    );
  });

  it("acha a URL no meio de um comentário", () => {
    expect(extrairUrl("olha isso https://g1.globo.com/x é verdade?")).toBe(
      "https://g1.globo.com/x",
    );
  });

  it("devolve null quando não há URL", () => {
    expect(extrairUrl("o ministro pediu demissão")).toBeNull();
  });
});

describe("classificarEntrada", () => {
  it("reconhece um link sozinho", () => {
    const r = classificarEntrada("https://g1.globo.com/noticia");

    expect(r.tipo).toBe("link");
    expect(r.url).toBe("https://g1.globo.com/noticia");
  });

  it("trata link com comentário como link", () => {
    // A URL é o que a Vera consegue investigar a fundo; ignorá-la desperdiçaria
    // a camada de fonte.
    const r = classificarEntrada("recebi isso, é verdade? https://site.com/x");

    expect(r.tipo).toBe("link");
    expect(r.url).toBe("https://site.com/x");
  });

  it("reconhece texto longo de notícia", () => {
    const texto = Array.from({ length: 30 }, (_, i) => `palavra${i}`).join(" ");

    expect(classificarEntrada(texto).tipo).toBe("texto");
    expect(classificarEntrada(texto).url).toBeNull();
  });

  it("reconhece afirmação curta", () => {
    expect(classificarEntrada("a vacina causa autismo").tipo).toBe("afirmacao");
  });

  it("apara espaços em volta", () => {
    expect(classificarEntrada("  https://site.com/x  ").texto).toBe(
      "https://site.com/x",
    );
  });

  it("não quebra com entrada vazia", () => {
    const r = classificarEntrada("   ");

    expect(r.tipo).toBe("afirmacao");
    expect(r.url).toBeNull();
  });
});

describe("contarPalavras", () => {
  it("conta palavras separadas por espaço", () => {
    expect(contarPalavras("uma duas três")).toBe(3);
  });

  it("ignora espaços repetidos e quebras de linha", () => {
    expect(contarPalavras("uma   duas\n\ntrês")).toBe(3);
  });

  it("devolve zero para string vazia", () => {
    expect(contarPalavras("   ")).toBe(0);
  });
});
