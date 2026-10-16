"use client";

/**
 * Apresentação do projeto em formato de slides, dentro do próprio app.
 *
 * Mostra o produto inteiro para quem chega de fora — persona, pipeline em camadas
 * N0 a N4, os 13 sinais (com a parte de ML e a de LLM), as frentes de tecnologia, os
 * princípios, a metodologia e a equipe. Um dos slides é uma **demonstração ao vivo**:
 * roda o pipeline de verdade para simular um prompt.
 *
 * É um deck navegável (setas na tela, teclado ← →, e as bolinhas). Cada troca de slide
 * re-dispara a animação de entrada; `prefers-reduced-motion` desliga o movimento pelo
 * CSS global. O conteúdo vem da branch `docs` e do ARQUITETURA.md; feito com o sistema
 * visual (vera-estilo) e a voz da Vera (vera-voz).
 */

import Image from "next/image";
import { useCallback, useEffect, useRef, useState } from "react";

import { DemoAoVivo } from "@/components/sobre/DemoAoVivo";
import { Icone, type NomeDoIcone } from "@/components/ui/Icone";
import { VeraAvatar } from "@/components/vera/VeraAvatar";

// --- Dados da apresentação -----------------------------------------------------------

const CAMADAS: Array<{
  id: string;
  nome: string;
  icone: NomeDoIcone;
  pergunta: string;
  comoFaz: string;
}> = [
  { id: "N0", nome: "Cache", icone: "relogio", pergunta: "Já conferi isso?", comoFaz: "Reaproveita uma checagem já feita." },
  { id: "N1", nome: "Fonte", icone: "site", pergunta: "Quem publicou?", comoFaz: "Reputação, idade do domínio, checagens de agência." },
  { id: "N2", nome: "Conteúdo", icone: "texto", pergunta: "Como foi escrito?", comoFaz: "Classificador de estilo, sensacionalismo, emoção." },
  { id: "N3", nome: "Corroboração", icone: "jornal", pergunta: "Quem mais publicou?", comoFaz: "Busca notícias semelhantes e mede similaridade." },
  { id: "N4", nome: "IA generativa", icone: "robo", pergunta: "As fontes sustentam?", comoFaz: "Uma LLM confere alegação por alegação (NLI)." },
];

const DIMENSOES: Array<{
  nome: string;
  pontos: number;
  icone: NomeDoIcone;
  sinais: Array<{ id: string; nome: string; peso: number }>;
}> = [
  {
    nome: "Fonte",
    pontos: 35,
    icone: "site",
    sinais: [
      { id: "S-01", nome: "Reputação do veículo", peso: 12 },
      { id: "S-02", nome: "Histórico de fakes do domínio", peso: 8 },
      { id: "S-03", nome: "Idade do domínio (RDAP/WHOIS)", peso: 6 },
      { id: "S-04", nome: "Transparência da página", peso: 5 },
      { id: "S-05", nome: "Autor identificável", peso: 4 },
    ],
  },
  {
    nome: "Conteúdo",
    pontos: 25,
    icone: "texto",
    sinais: [
      { id: "S-06", nome: "Classificador estilístico (TF-IDF + SVM/RL)", peso: 10 },
      { id: "S-07", nome: "Sensacionalismo", peso: 5 },
      { id: "S-08", nome: "Intensidade emocional (NRC)", peso: 5 },
      { id: "S-09", nome: "Cita fontes verificáveis", peso: 3 },
      { id: "S-10", nome: "Texto gerado por IA", peso: 2 },
    ],
  },
  {
    nome: "Corroboração",
    pontos: 40,
    icone: "jornal",
    sinais: [
      { id: "S-11", nome: "Veículos confiáveis que publicaram", peso: 15 },
      { id: "S-12", nome: "NLI: evidências sustentam ou contradizem", peso: 20 },
      { id: "S-13", nome: "Originalidade (é cópia alterada?)", peso: 5 },
    ],
  },
];

const FRENTES: Array<{ titulo: string; icone: NomeDoIcone; itens: string[] }> = [
  {
    titulo: "Motor de veracidade",
    icone: "contas",
    itens: [
      "Python + FastAPI, arquitetura hexagonal",
      "Camadas N0 a N4 em cadeia de responsabilidade",
      "PostgreSQL + pgvector (cache e similaridade)",
    ],
  },
  {
    titulo: "Aprendizado de máquina",
    icone: "etiqueta",
    itens: [
      "Classificador de estilo S-06: TF-IDF + SVM/Regressão",
      "Intensidade emocional com o NRC Emotion Lexicon",
      "Notebooks de EDA e datasets em Parquet",
    ],
  },
  {
    titulo: "IA generativa (LLM)",
    icone: "robo",
    itens: [
      "Camada N4: LLM via Ollama (llama3)",
      "NLI: sustenta, contradiz ou é neutro",
      "Chamada só quando N0 a N3 não bastam",
    ],
  },
  {
    titulo: "Frontend",
    icone: "conversa",
    itens: [
      "Next.js + TypeScript + Tailwind, em chat",
      "Mostra andamento, sinais e fontes",
      "PWA instalável e extensão de navegador",
    ],
  },
];

const PRINCIPIOS: Array<{ icone: NomeDoIcone; titulo: string; texto: string }> = [
  { icone: "lupa", titulo: "Mostra o caminho", texto: "Não responde só “fake ou não”. Mostra as fontes, os sinais e quanto cada um pesou." },
  { icone: "quase", titulo: "Nunca crava certeza", texto: "“Provavelmente falsa”, “confirmada por fontes”. Desconfiada por ofício." },
  { icone: "espera", titulo: "Não sei é não sei", texto: "Sinal sem dado fica de fora e nunca vale zero. Sem prova, ela fica em aberto." },
  { icone: "contas", titulo: "Gasta a IA só quando precisa", texto: "A LLM é a camada mais cara e só entra quando as outras não resolvem." },
];

const EQUIPE: Array<{ nome: string; papel: string; github: string; foto: string }> = [
  { nome: "Ian Costa", papel: "Scrum Master · Developer", github: "iancostag", foto: "https://avatars.githubusercontent.com/u/146049457?v=4" },
  { nome: "Maykon Soares", papel: "Product Owner · Developer", github: "maykonjuso", foto: "https://avatars.githubusercontent.com/u/89596623?v=4" },
  { nome: "Luísa Brambilla", papel: "Developer", github: "LuisaBrambilla", foto: "https://avatars.githubusercontent.com/u/139017020?v=4" },
  { nome: "Natália Evelin", papel: "Developer", github: "NatyEvelin", foto: "https://avatars.githubusercontent.com/u/211730397?v=4" },
  { nome: "Rebeca Bontempo", papel: "Developer", github: "rebecaboncaputo", foto: "https://avatars.githubusercontent.com/u/211146495?v=4" },
];

// --- Cabeçalho de slide --------------------------------------------------------------

function CabecalhoSlide({
  icone,
  sobre,
  titulo,
}: {
  icone: NomeDoIcone;
  sobre: string;
  titulo: string;
}) {
  return (
    <div className="mb-5">
      <p className="flex items-center gap-2 font-display text-base uppercase tracking-wide text-vermelho">
        <Icone nome={icone} tamanho={23} />
        {sobre}
      </p>
      <h2 className="font-display text-4xl leading-none">{titulo}</h2>
    </div>
  );
}

// --- Slides --------------------------------------------------------------------------

const SLIDES: Array<{ chave: string; no: React.ReactNode }> = [
  {
    chave: "capa",
    no: (
      <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
        <VeraAvatar humor="satisfeita" tamanho={165} />
        <p className="font-display text-base uppercase tracking-wide text-vermelho">
          Residência em IA · Challenge 1 · Grupo 4
        </p>
        <h1 className="font-display text-6xl leading-none">A Senhora Vera</h1>
        <p className="max-w-xl text-xl">
          Uma senhora do Recife que sabe de tudo, mas <strong>não repassa nada sem
          conferir a fonte antes</strong>.
        </p>
        <p className="fonte-mao text-3xl text-tinta-2">
          “O que é que tu quer saber que é verdade?”
        </p>
      </div>
    ),
  },
  {
    chave: "visao",
    no: (
      <div className="flex h-full flex-col justify-center">
        <CabecalhoSlide icone="coracao" sobre="A ideia" titulo="Checar sem decidir por você" />
        <p className="text-xl leading-relaxed">
          Para quem recebe notícia por rede social e não sabe se pode confiar, a Vera é
          uma <strong>checadora em formato de conversa</strong> que cruza o que você leu
          com fontes confiáveis e <strong>explica</strong> por que aquilo parece
          verdadeiro ou falso.
        </p>
        <p className="mt-4 text-xl leading-relaxed">
          Diferente de um classificador que só diz “fake / não fake”, ela mostra o
          caminho, para <strong>fortalecer o pensamento crítico</strong>, não substituir.
        </p>
      </div>
    ),
  },
  {
    chave: "camadas",
    no: (
      <div className="flex h-full flex-col justify-center">
        <CabecalhoSlide icone="lupa" sobre="Como investiga" titulo="Uma investigação em camadas" />
        <p className="mb-4 text-lg text-tinta-2">
          Da mais barata para a mais cara. Depois de cada camada, se já tem certeza, ela
          para e responde.
        </p>
        <ol className="grid gap-2 sm:grid-cols-2 lg:grid-cols-5">
          {CAMADAS.map((c, i) => (
            <li
              key={c.id}
              className="surge flex flex-col gap-1.5 rounded-md border-[3px] border-tinta bg-papel-2 p-3 shadow-bloco-sm"
              style={{ "--atraso": `${i * 90}ms` } as React.CSSProperties}
            >
              <div className="flex items-center justify-between">
                <span className="font-display text-2xl">{c.id}</span>
                <Icone nome={c.icone} tamanho={30} className="text-vermelho" />
              </div>
              <span className="font-display text-xl leading-none">{c.nome}</span>
              <span className="text-base font-bold text-tinta-2">{c.pergunta}</span>
              <span className="text-base">{c.comoFaz}</span>
            </li>
          ))}
        </ol>
      </div>
    ),
  },
  {
    chave: "demo",
    no: (
      <div className="flex h-full flex-col">
        <CabecalhoSlide icone="robo" sobre="Ao vivo" titulo="Vê a Vera trabalhando" />
        <p className="mb-3 text-lg text-tinta-2">
          Isto não é vídeo: toca num exemplo e o pipeline roda de verdade, aqui mesmo.
        </p>
        <DemoAoVivo />
      </div>
    ),
  },
  {
    chave: "sinais",
    no: (
      <div className="flex h-full flex-col justify-center">
        <CabecalhoSlide icone="contas" sobre="O que ela mede" titulo="13 sinais, 100 pontos" />
        <div className="grid gap-3 md:grid-cols-3">
          {DIMENSOES.map((d, i) => (
            <div
              key={d.nome}
              className="surge flex flex-col rounded-md border-[3px] border-tinta bg-papel-2 p-4 shadow-bloco-sm"
              style={{ "--atraso": `${i * 120}ms` } as React.CSSProperties}
            >
              <div className="flex items-center gap-2">
                <Icone nome={d.icone} tamanho={25} className="text-vermelho" />
                <h3 className="font-display text-2xl">{d.nome}</h3>
                <span className="ml-auto font-display text-xl tabular-nums text-tinta-2">
                  {d.pontos}
                </span>
              </div>
              <ul className="mt-2 space-y-1">
                {d.sinais.map((s) => (
                  <li key={s.id} className="flex items-baseline gap-2 text-base">
                    <span className="font-mono text-sm text-tinta-3">{s.id}</span>
                    <span className="min-w-0 flex-1">{s.nome}</span>
                    <span className="font-bold tabular-nums">{s.peso}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <p className="mt-3 text-base text-tinta-2">
          O veredito é a média ponderada só dos sinais que ela conseguiu medir.
        </p>
      </div>
    ),
  },
  {
    chave: "frentes",
    no: (
      <div className="flex h-full flex-col justify-center">
        <CabecalhoSlide icone="etiqueta" sobre="A engenharia" titulo="As frentes do projeto" />
        <div className="grid gap-3 md:grid-cols-2">
          {FRENTES.map((f, i) => (
            <div
              key={f.titulo}
              className="surge rounded-md border-[3px] border-tinta bg-papel-2 p-4 shadow-bloco-sm"
              style={{ "--atraso": `${i * 100}ms` } as React.CSSProperties}
            >
              <h3 className="flex items-center gap-2 font-display text-2xl">
                <Icone nome={f.icone} tamanho={25} className="text-vermelho" />
                {f.titulo}
              </h3>
              <ul className="mt-2 space-y-1">
                {f.itens.map((it) => (
                  <li key={it} className="flex items-start gap-2 text-base">
                    <Icone nome="visto" tamanho={19} className="mt-0.5 shrink-0 text-confirmada" />
                    <span>{it}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    ),
  },
  {
    chave: "principios",
    no: (
      <div className="flex h-full flex-col justify-center">
        <CabecalhoSlide icone="coracao" sobre="O jeito dela" titulo="Quatro regras da casa" />
        <div className="grid gap-3 sm:grid-cols-2">
          {PRINCIPIOS.map((p, i) => (
            <div
              key={p.titulo}
              className="surge flex items-start gap-3 rounded-md border-[3px] border-tinta bg-papel-2 p-4 shadow-bloco-sm"
              style={{ "--atraso": `${i * 90}ms` } as React.CSSProperties}
            >
              <Icone nome={p.icone} tamanho={33} className="mt-0.5 shrink-0 text-vermelho" />
              <div>
                <h3 className="font-display text-xl leading-none">{p.titulo}</h3>
                <p className="mt-1.5 text-base">{p.texto}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    ),
  },
  {
    chave: "metodologia",
    no: (
      <div className="flex h-full flex-col items-center justify-center text-center">
        <CabecalhoSlide icone="etiqueta" sobre="Como foi feito" titulo="CBL + Scrum" />
        <p className="max-w-xl text-xl leading-relaxed">
          O projeto seguiu <strong>Challenge Based Learning</strong> com{" "}
          <strong>Scrum adaptado</strong>, no tema Fake News e Desinformação. As cinco
          camadas do pipeline foram divididas entre as cinco pessoas do grupo.
        </p>
      </div>
    ),
  },
  {
    chave: "equipe",
    no: (
      <div className="flex h-full flex-col justify-center">
        <CabecalhoSlide icone="assinatura" sobre="Quem fez" titulo="O Grupo 4" />
        <ul className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
          {EQUIPE.map((pessoa, i) => (
            <li
              key={pessoa.nome}
              className="surge"
              style={{ "--atraso": `${i * 90}ms` } as React.CSSProperties}
            >
              <a
                href={`https://github.com/${pessoa.github}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex h-full flex-col items-center gap-2 rounded-md border-[3px] border-tinta bg-papel-2 p-4 text-center shadow-bloco-sm transition-colors hover:bg-vermelho-suave"
              >
                <Image
                  src={pessoa.foto}
                  alt={`Foto de ${pessoa.nome} no GitHub`}
                  width={80}
                  height={80}
                  className="size-20 rounded-total border-[3px] border-tinta object-cover"
                />
                <span className="font-bold leading-tight">{pessoa.nome}</span>
                <span className="text-sm text-tinta-2">{pessoa.papel}</span>
                <span className="mt-auto flex items-center gap-1 text-sm text-tinta-3">
                  <Icone nome="link" tamanho={15} />@{pessoa.github}
                </span>
              </a>
            </li>
          ))}
        </ul>
      </div>
    ),
  },
];

// --- Deck ----------------------------------------------------------------------------

/** Ordem de exibição: a apresentação da equipe entra logo depois da capa (2º slide). */
const ORDEM = [
  "capa",
  "equipe",
  "visao",
  "camadas",
  "demo",
  "sinais",
  "frentes",
  "principios",
  "metodologia",
] as const;

const SLIDES_EM_ORDEM = ORDEM.map(
  (chave) => SLIDES.find((s) => s.chave === chave)!,
);

export function Apresentacao() {
  const [indice, setIndice] = useState(0);
  const [telaCheia, setTelaCheia] = useState(false);
  const deckRef = useRef<HTMLDivElement>(null);
  const total = SLIDES_EM_ORDEM.length;

  const ir = useCallback(
    (destino: number) => setIndice((i) => Math.max(0, Math.min(total - 1, destino))),
    [total],
  );

  // Teclado: ← → navegam, como num projetor.
  useEffect(() => {
    function aoTeclar(e: KeyboardEvent) {
      if (e.key === "ArrowRight") ir(indice + 1);
      else if (e.key === "ArrowLeft") ir(indice - 1);
    }
    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
  }, [indice, ir]);

  // Acompanha o estado real de tela cheia: o usuário pode sair com Esc, e o botão
  // precisa refletir isso. `fullscreenElement` é nulo quando não há nada em tela cheia.
  useEffect(() => {
    function aoMudar() {
      setTelaCheia(document.fullscreenElement === deckRef.current);
    }
    document.addEventListener("fullscreenchange", aoMudar);
    return () => document.removeEventListener("fullscreenchange", aoMudar);
  }, []);

  const alternarTelaCheia = useCallback(() => {
    const el = deckRef.current;
    if (!el) return;
    try {
      if (document.fullscreenElement) void document.exitFullscreen();
      else void el.requestFullscreen();
    } catch {
      // Navegador sem suporte ou gesto negado: a apresentação segue na página.
    }
  }, []);

  const slide = SLIDES_EM_ORDEM[indice];

  return (
    <div
      ref={deckRef}
      className={
        telaCheia
          ? "flex h-screen w-full flex-col justify-center overflow-hidden bg-papel px-4 py-4 md:px-8"
          : "mx-auto flex w-full max-w-5xl flex-col px-4 py-6 md:px-8"
      }
    >
      {/* Palco: moldura de quadrinho. Em tela cheia preenche a altura disponível. */}
      <div
        className={`painel relative flex flex-col overflow-y-auto p-6 md:p-10 ${
          telaCheia ? "flex-1" : "min-h-[68vh] md:min-h-[70vh]"
        }`}
      >
        {/* A key re-dispara a animação de entrada a cada troca de slide. */}
        <div key={slide.chave} className="surge flex flex-1 flex-col">
          {slide.no}
        </div>
      </div>

      {/* Controles: ‹ · bolinhas · › e o contador. */}
      <div className="mt-4 flex items-center justify-between gap-3">
        <button
          type="button"
          onClick={() => ir(indice - 1)}
          disabled={indice === 0}
          aria-label="Slide anterior"
          className="pressiona flex size-11 shrink-0 items-center justify-center rounded-total border-[3px] border-tinta bg-papel-2 shadow-bloco-sm disabled:opacity-30"
        >
          <Icone nome="seta" tamanho={25} className="rotate-180" />
        </button>

        <div className="flex flex-wrap items-center justify-center gap-2" role="tablist" aria-label="Slides">
          {SLIDES_EM_ORDEM.map((s, i) => (
            <button
              key={s.chave}
              type="button"
              role="tab"
              aria-selected={i === indice}
              aria-label={`Ir para o slide ${i + 1}`}
              onClick={() => ir(i)}
              className={`size-3 rounded-total border-2 border-tinta transition-colors ${
                i === indice ? "bg-vermelho" : "bg-papel-2 hover:bg-vermelho-suave"
              }`}
            />
          ))}
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={alternarTelaCheia}
            aria-label={telaCheia ? "Sair da tela cheia" : "Tela cheia"}
            title={telaCheia ? "Sair da tela cheia" : "Tela cheia"}
            className="pressiona flex size-11 shrink-0 items-center justify-center rounded-total border-[3px] border-tinta bg-papel-2 shadow-bloco-sm"
          >
            <svg viewBox="0 0 24 24" className="size-5" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
              {telaCheia ? (
                <path d="M9 4v5H4M15 4v5h5M9 20v-5H4M15 20v-5h5" />
              ) : (
                <path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" />
              )}
            </svg>
          </button>
          <span className="font-display text-xl tabular-nums text-tinta-2">
            {indice + 1}/{total}
          </span>
          <button
            type="button"
            onClick={() => ir(indice + 1)}
            disabled={indice === total - 1}
            aria-label="Próximo slide"
            className="pressiona flex size-11 shrink-0 items-center justify-center rounded-total border-[3px] border-tinta bg-vermelho text-white shadow-bloco-sm disabled:opacity-30"
          >
            <Icone nome="seta" tamanho={25} />
          </button>
        </div>
      </div>
    </div>
  );
}
