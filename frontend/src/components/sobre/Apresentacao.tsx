"use client";

/**
 * Apresentação do projeto em formato de slides, dentro do próprio app.
 *
 * É uma prancha de quadrinho: painéis com moldura grossa, balões de fala, retícula de
 * impressão barata, carimbos e a arte da Vera. Mostra o produto inteiro — persona,
 * pipeline em camadas N0–N4, dificuldade, os 13 sinais (com a parte de ML e a de LLM),
 * as faixas de veracidade, as frentes, os princípios, a metodologia (CBL + Scrum), a
 * equipe e os números. Um slide é uma demonstração ao vivo: roda o pipeline de verdade.
 *
 * Deck navegável por setas, teclado ← → e bolinhas, com modo tela cheia (que aplica um
 * zoom para o texto crescer junto com a tela). Cada troca re-dispara a animação;
 * prefers-reduced-motion desliga o movimento pelo CSS. Conteúdo do planejamento (branch
 * docs) e do que foi executado (código).
 */

import Image from "next/image";
import { useCallback, useEffect, useRef, useState } from "react";

import { DemoAoVivo } from "@/components/sobre/DemoAoVivo";
import { Balao } from "@/components/ui/Balao";
import { Icone, type NomeDoIcone } from "@/components/ui/Icone";

// --- Dados ---------------------------------------------------------------------------

const CAMADAS: Array<{
  id: string;
  nome: string;
  icone: NomeDoIcone;
  pergunta: string;
  comoFaz: string;
  custo: string;
}> = [
  { id: "N0", nome: "Cache", icone: "relogio", pergunta: "Já conferi isso?", comoFaz: "Reaproveita uma checagem já feita da mesma coisa.", custo: "instantâneo" },
  { id: "N1", nome: "Fonte", icone: "site", pergunta: "Quem publicou?", comoFaz: "Reputação, idade do domínio e checagens de agência.", custo: "muito baixo" },
  { id: "N2", nome: "Conteúdo", icone: "texto", pergunta: "Como foi escrito?", comoFaz: "Classificador de estilo, sensacionalismo e emoção.", custo: "baixo" },
  { id: "N3", nome: "Corroboração", icone: "jornal", pergunta: "Quem mais publicou?", comoFaz: "Busca notícias parecidas e mede a semelhança.", custo: "médio" },
  { id: "N4", nome: "IA generativa", icone: "robo", pergunta: "As fontes sustentam?", comoFaz: "Uma LLM confere alegação por alegação (NLI).", custo: "alto" },
];

const DIFICULDADE: Array<{ nivel: string; onde: string; cor: string; exemplo: string }> = [
  { nivel: "Fácil", onde: "N0–N1", cor: "#2E7D32", exemplo: "Já desmentida por agência, ou site que nasceu semana passada." },
  { nivel: "Mediano", onde: "N2–N3", cor: "#F9A825", exemplo: "Texto sensacionalista que nenhum veículo sério replicou." },
  { nivel: "Difícil", onde: "N4", cor: "#C62828", exemplo: "Notícia plausível, bem escrita, com meia-verdade." },
];

const DIMENSOES: Array<{
  nome: string;
  pontos: number;
  icone: NomeDoIcone;
  marca: string;
  sinais: Array<{ id: string; nome: string; peso: number }>;
}> = [
  {
    nome: "Fonte",
    pontos: 35,
    icone: "site",
    marca: "quem falou",
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
    marca: "aprendizado de máquina",
    sinais: [
      { id: "S-06", nome: "Classificador de estilo (TF-IDF + SVM/RL)", peso: 10 },
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
    marca: "onde entra a LLM",
    sinais: [
      { id: "S-11", nome: "Veículos confiáveis que publicaram", peso: 15 },
      { id: "S-12", nome: "NLI: evidências sustentam ou contradizem", peso: 20 },
      { id: "S-13", nome: "Originalidade (é cópia alterada?)", peso: 5 },
    ],
  },
];

const FAIXAS: Array<{ nome: string; cor: string }> = [
  { nome: "Provavelmente falsa", cor: "#C62828" },
  { nome: "Duvidosa", cor: "#EF6C00" },
  { nome: "Inconclusiva", cor: "#F9A825" },
  { nome: "Provavelmente verdadeira", cor: "#7CB342" },
  { nome: "Confirmada por fontes", cor: "#2E7D32" },
];

const FRENTES: Array<{ titulo: string; icone: NomeDoIcone; itens: string[] }> = [
  { titulo: "Motor de veracidade", icone: "contas", itens: ["Python + FastAPI, arquitetura hexagonal", "Camadas N0–N4 em cadeia de responsabilidade", "PostgreSQL + pgvector (cache e similaridade)"] },
  { titulo: "Aprendizado de máquina", icone: "etiqueta", itens: ["Classificador de estilo: TF-IDF + SVM/Regressão", "Emoção com o NRC Emotion Lexicon", "Notebooks de EDA e datasets em Parquet"] },
  { titulo: "IA generativa (LLM)", icone: "robo", itens: ["Camada N4: LLM via Ollama (llama3)", "NLI: sustenta, contradiz ou é neutro", "Chamada só quando N0–N3 não bastam"] },
  { titulo: "Frontend", icone: "conversa", itens: ["Next.js + TypeScript + Tailwind, em chat", "Mostra o andamento, os sinais e as fontes", "PWA instalável e extensão de navegador"] },
];

const PRINCIPIOS: Array<{ icone: NomeDoIcone; titulo: string; texto: string }> = [
  { icone: "lupa", titulo: "Mostra o caminho", texto: "Não responde só “fake ou não”. Mostra as fontes, os sinais e quanto cada um pesou." },
  { icone: "quase", titulo: "Nunca crava certeza", texto: "“Provavelmente falsa”, “confirmada por fontes”. Desconfiada por ofício." },
  { icone: "espera", titulo: "Não sei é não sei", texto: "Sinal sem dado fica de fora e nunca vale zero. Sem prova, ela fica em aberto." },
  { icone: "contas", titulo: "Gasta a IA só quando precisa", texto: "A LLM é a camada mais cara e só entra quando as outras não resolvem." },
];

const NUMEROS: Array<{ valor: string; rotulo: string }> = [
  { valor: "5", rotulo: "camadas" },
  { valor: "13", rotulo: "sinais" },
  { valor: "3", rotulo: "dimensões" },
  { valor: "100", rotulo: "pontos" },
];

const EQUIPE: Array<{ nome: string; papel: string; github: string; foto: string }> = [
  { nome: "Ian Costa", papel: "Scrum Master · Developer", github: "iancostag", foto: "https://avatars.githubusercontent.com/u/146049457?v=4" },
  { nome: "Maykon Soares", papel: "Product Owner · Developer", github: "maykonjuso", foto: "https://avatars.githubusercontent.com/u/89596623?v=4" },
  { nome: "Luísa Brambilla", papel: "Developer", github: "LuisaBrambilla", foto: "https://avatars.githubusercontent.com/u/139017020?v=4" },
  { nome: "Natália Evelin", papel: "Developer", github: "NatyEvelin", foto: "https://avatars.githubusercontent.com/u/211730397?v=4" },
  { nome: "Rebeca Bontempo", papel: "Developer", github: "rebecaboncaputo", foto: "https://avatars.githubusercontent.com/u/211146495?v=4" },
];

// --- Peças de quadrinho --------------------------------------------------------------

/** Faixa de retícula atrás de um conteúdo de destaque (nunca atrás de texto corrido). */
function Reticula({ className = "" }: { className?: string }) {
  return <span aria-hidden className={`reticula pointer-events-none absolute inset-0 ${className}`} />;
}

/** Carimbo torto, como batido à mão. */
function Carimbo({ children, cor = "bg-vermelho" }: { children: React.ReactNode; cor?: string }) {
  return (
    <span className={`carimbo inline-flex items-center gap-1.5 rounded-md border-[3px] border-tinta ${cor} px-3 py-1 font-display text-lg text-white shadow-bloco-sm`}>
      {children}
    </span>
  );
}

/** Supertítulo: a linha vermelha em caixa alta acima do título de cada slide. */
function Super({ icone, texto }: { icone: NomeDoIcone; texto: string }) {
  return (
    <p className="flex items-center gap-2 font-display text-lg uppercase tracking-wide text-vermelho">
      <Icone nome={icone} tamanho={24} />
      {texto}
    </p>
  );
}

// --- Slides --------------------------------------------------------------------------

const SLIDES: Array<{ chave: string; no: React.ReactNode }> = [
  {
    chave: "capa",
    no: (
      <div className="relative flex flex-col items-center gap-5 overflow-hidden text-center">
        <Reticula className="text-vermelho" />
        <Image src="/vera-corpo-apontando.png" alt="Senhora Vera apontando" width={260} height={320} priority className="relative h-56 w-auto drop-shadow-[6px_6px_0_var(--tinta)] md:h-72" />
        <div className="relative">
          <Carimbo cor="bg-ocre">Residência em IA · Challenge 1 · Grupo 4</Carimbo>
        </div>
        <h1 className="relative font-display text-5xl leading-none md:text-5xl">A Senhora Vera</h1>
        <div className="relative w-full max-w-xl">
          <Balao>
            <p className="fonte-mao text-2xl">“O que é que tu quer saber que é verdade?”</p>
          </Balao>
        </div>
        <p className="relative max-w-2xl text-xl">
          Uma senhora do Recife que sabe de tudo, mas <strong>não repassa nada sem conferir a fonte antes</strong>.
        </p>
      </div>
    ),
  },
  {
    chave: "equipe",
    no: (
      <div className="flex flex-col">
        <Super icone="assinatura" texto="Quem fez" />
        <h2 className="mb-6 font-display text-4xl leading-none">O Grupo 4</h2>
        <ul className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
          {EQUIPE.map((pessoa, i) => (
            <li key={pessoa.nome} className="sobe-pop" style={{ "--atraso": `${i * 90}ms` } as React.CSSProperties}>
              <a href={`https://github.com/${pessoa.github}`} target="_blank" rel="noopener noreferrer" className="flex h-full flex-col items-center gap-2 rounded-md border-[3px] border-tinta bg-papel-2 p-4 text-center shadow-bloco transition-transform hover:-translate-y-1">
                <Image src={pessoa.foto} alt={`Foto de ${pessoa.nome} no GitHub`} width={96} height={96} className="size-24 rounded-total border-[3px] border-tinta object-cover" />
                <span className="font-display text-xl leading-none">{pessoa.nome}</span>
                <span className="text-base font-bold text-tinta-2">{pessoa.papel}</span>
                <span className="mt-auto flex items-center gap-1 text-sm text-tinta-3"><Icone nome="link" tamanho={14} />@{pessoa.github}</span>
              </a>
            </li>
          ))}
        </ul>
      </div>
    ),
  },
  {
    chave: "visao",
    no: (
      <div className="flex flex-col gap-5">
        <div>
          <Super icone="coracao" texto="A ideia" />
          <h2 className="font-display text-4xl leading-none">Checar sem decidir por você</h2>
        </div>
        <div className="grid items-center gap-5 md:grid-cols-[1fr_auto]">
          <div className="flex flex-col gap-4">
            <Balao>
              <p className="text-xl leading-snug">
                Você manda a notícia, eu cruzo com <strong>fontes confiáveis</strong> e te mostro <strong>por que</strong> ela parece verdadeira ou falsa.
              </p>
            </Balao>
            <p className="text-lg leading-relaxed text-tinta-2">
              Diferente de um classificador que só diz “fake / não fake”, a Vera mostra o caminho, para <strong>fortalecer o pensamento crítico</strong>, não substituir.
            </p>
          </div>
          <Image src="/vera-corpo.png" alt="Senhora Vera avaliando" width={220} height={300} className="hidden h-64 w-auto drop-shadow-[6px_6px_0_var(--tinta)] md:block" />
        </div>
      </div>
    ),
  },
  {
    chave: "camadas",
    no: (
      <div className="flex flex-col">
        <Super icone="lupa" texto="Como investiga" />
        <h2 className="mb-2 font-display text-4xl leading-none">Investigação em camadas</h2>
        <p className="mb-5 text-lg text-tinta-2">Da mais barata para a mais cara. Achou certeza, <strong>parou e respondeu</strong>.</p>
        <ol className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {CAMADAS.map((c, i) => (
            <li key={c.id} className="sobe-pop flex flex-col gap-2 rounded-md border-[3px] border-tinta bg-papel-2 p-4 shadow-bloco" style={{ "--atraso": `${i * 90}ms` } as React.CSSProperties}>
              <div className="flex items-center justify-between">
                <span className="font-display text-2xl">{c.id}</span>
                <Icone nome={c.icone} tamanho={30} className="text-vermelho" />
              </div>
              <span className="font-display text-xl leading-none">{c.nome}</span>
              <span className="text-lg font-bold text-tinta-2">{c.pergunta}</span>
              <span className="text-base">{c.comoFaz}</span>
              <span className="mt-auto inline-flex w-fit rounded-total border-2 border-borda px-2 text-sm font-bold text-tinta-3">{c.custo}</span>
            </li>
          ))}
        </ol>
      </div>
    ),
  },
  {
    chave: "dificuldade",
    no: (
      <div className="flex flex-col">
        <Super icone="etiqueta" texto="O quanto custa" />
        <h2 className="mb-5 font-display text-4xl leading-none">A dificuldade da notícia</h2>
        <p className="mb-5 text-lg text-tinta-2">A camada em que a Vera para define o quão difícil era a checagem.</p>
        <div className="grid gap-4 md:grid-cols-3">
          {DIFICULDADE.map((d, i) => (
            <div key={d.nivel} className="sobe-pop flex flex-col gap-2 rounded-md border-[3px] border-tinta bg-papel-2 p-5 shadow-bloco" style={{ "--atraso": `${i * 120}ms` } as React.CSSProperties}>
              <span className="inline-flex w-fit items-center gap-2 rounded-md border-[3px] border-tinta px-3 py-1 font-display text-xl text-white" style={{ background: d.cor }}>
                {d.nivel}
              </span>
              <span className="font-display text-lg text-tinta-2">parou em {d.onde}</span>
              <span className="text-lg">{d.exemplo}</span>
            </div>
          ))}
        </div>
      </div>
    ),
  },
  {
    chave: "demo",
    no: (
      <div className="flex flex-col">
        <Super icone="robo" texto="Ao vivo" />
        <h2 className="font-display text-4xl leading-none">Vê a Vera trabalhando</h2>
        <p className="mb-4 text-lg text-tinta-2">Isto não é vídeo: toca num exemplo e o pipeline roda de verdade, aqui mesmo.</p>
        <DemoAoVivo />
      </div>
    ),
  },
  {
    chave: "sinais",
    no: (
      <div className="flex flex-col">
        <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
          <div>
            <Super icone="contas" texto="O que ela mede" />
            <h2 className="font-display text-4xl leading-none">13 sinais, 100 pontos</h2>
          </div>
          <Carimbo cor="bg-confirmada">a média só do que deu pra medir</Carimbo>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {DIMENSOES.map((d, i) => (
            <div key={d.nome} className="sobe-pop flex flex-col rounded-md border-[3px] border-tinta bg-papel-2 p-4 shadow-bloco" style={{ "--atraso": `${i * 110}ms` } as React.CSSProperties}>
              <div className="flex items-center gap-2">
                <Icone nome={d.icone} tamanho={24} className="text-vermelho" />
                <h3 className="font-display text-xl">{d.nome}</h3>
                <span className="ml-auto font-display text-xl tabular-nums text-tinta-2">{d.pontos}</span>
              </div>
              <span className="mb-2 text-sm font-bold uppercase tracking-wide text-vermelho">{d.marca}</span>
              <ul className="space-y-1.5">
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
      </div>
    ),
  },
  {
    chave: "faixas",
    no: (
      <div className="flex flex-col">
        <Super icone="quase" texto="O veredito" />
        <h2 className="mb-2 font-display text-4xl leading-none">As faixas de veracidade</h2>
        <p className="mb-5 text-lg text-tinta-2">A cor comunica o resultado, e nunca sozinha: vem sempre com a palavra escrita.</p>
        <ul className="flex flex-col gap-3">
          {FAIXAS.map((f, i) => (
            <li key={f.nome} className="sobe-pop flex items-center gap-4 rounded-md border-[3px] border-tinta bg-papel-2 p-3 shadow-bloco-sm" style={{ "--atraso": `${i * 80}ms` } as React.CSSProperties}>
              <span className="size-10 shrink-0 rounded-md border-[3px] border-tinta" style={{ background: f.cor }} />
              <span className="font-display text-xl md:text-2xl">{f.nome}</span>
              <span className="ml-auto font-display text-xl tabular-nums text-tinta-3">{i * 20}–{(i + 1) * 20}</span>
            </li>
          ))}
        </ul>
      </div>
    ),
  },
  {
    chave: "frentes",
    no: (
      <div className="flex flex-col">
        <Super icone="etiqueta" texto="A engenharia" />
        <h2 className="mb-5 font-display text-4xl leading-none">As frentes do projeto</h2>
        <div className="grid gap-4 md:grid-cols-2">
          {FRENTES.map((f, i) => (
            <div key={f.titulo} className="sobe-pop rounded-md border-[3px] border-tinta bg-papel-2 p-5 shadow-bloco" style={{ "--atraso": `${i * 100}ms` } as React.CSSProperties}>
              <h3 className="flex items-center gap-2 font-display text-xl">
                <Icone nome={f.icone} tamanho={26} className="text-vermelho" />
                {f.titulo}
              </h3>
              <ul className="mt-2 space-y-1.5">
                {f.itens.map((it) => (
                  <li key={it} className="flex items-start gap-2 text-lg">
                    <Icone nome="visto" tamanho={20} className="mt-0.5 shrink-0 text-confirmada" />
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
      <div className="flex flex-col">
        <Super icone="coracao" texto="O jeito dela" />
        <h2 className="mb-5 font-display text-4xl leading-none">As regras da casa</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {PRINCIPIOS.map((p, i) => (
            <div key={p.titulo} className="sobe-pop flex items-start gap-3 rounded-md border-[3px] border-tinta bg-papel-2 p-5 shadow-bloco" style={{ "--atraso": `${i * 90}ms` } as React.CSSProperties}>
              <Icone nome={p.icone} tamanho={34} className="mt-0.5 shrink-0 text-vermelho" />
              <div>
                <h3 className="font-display text-xl leading-none">{p.titulo}</h3>
                <p className="mt-1.5 text-lg">{p.texto}</p>
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
      <div className="relative flex flex-col items-center gap-5 overflow-hidden text-center">
        <Reticula className="text-ocre" />
        <Super icone="etiqueta" texto="Como foi feito" />
        <h2 className="relative font-display text-5xl leading-none">CBL + Scrum</h2>
        <p className="relative max-w-2xl text-xl leading-relaxed">
          Challenge Based Learning com Scrum adaptado, no tema <strong>Fake News e Desinformação</strong>. As cinco camadas do pipeline foram divididas entre as cinco pessoas.
        </p>
        <div className="relative flex flex-wrap items-center justify-center gap-3">
          <Carimbo cor="bg-vermelho">1 Product Owner</Carimbo>
          <Carimbo cor="bg-ocre">1 Scrum Master</Carimbo>
          <Carimbo cor="bg-confirmada">5 Developers</Carimbo>
        </div>
        <p className="relative text-lg text-tinta-2">Estimativa por Planning Poker · backlog em épicos e histórias · requisitos RF e regras RN.</p>
      </div>
    ),
  },
  {
    chave: "numeros",
    no: (
      <div className="flex flex-col items-center gap-6 text-center">
        <Super icone="contas" texto="Em números" />
        <h2 className="font-display text-4xl leading-none">O motor da Vera</h2>
        <ul className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {NUMEROS.map((n, i) => (
            <li key={n.rotulo} className="sobe-pop flex flex-col items-center rounded-md border-[3px] border-tinta bg-papel-2 px-6 py-5 shadow-bloco" style={{ "--atraso": `${i * 90}ms` } as React.CSSProperties}>
              <span className="font-display text-5xl leading-none text-vermelho">{n.valor}</span>
              <span className="mt-1 font-display text-xl text-tinta-2">{n.rotulo}</span>
            </li>
          ))}
        </ul>
        <div className="w-full max-w-md">
          <Balao>
            <p className="fonte-mao text-2xl">“Manda a notícia aí, meu bem, que eu vou atrás.”</p>
          </Balao>
        </div>
      </div>
    ),
  },
];

// --- Deck ----------------------------------------------------------------------------

export function Apresentacao() {
  const [indice, setIndice] = useState(0);
  const [telaCheia, setTelaCheia] = useState(false);
  const deckRef = useRef<HTMLDivElement>(null);
  const total = SLIDES.length;

  const ir = useCallback(
    (destino: number) => setIndice((i) => Math.max(0, Math.min(total - 1, destino))),
    [total],
  );

  useEffect(() => {
    function aoTeclar(e: KeyboardEvent) {
      if (e.key === "ArrowRight") ir(indice + 1);
      else if (e.key === "ArrowLeft") ir(indice - 1);
    }
    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
  }, [indice, ir]);

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
      /* navegador sem suporte: segue na página */
    }
  }, []);

  const slide = SLIDES[indice];

  return (
    <div
      ref={deckRef}
      className={
        telaCheia
          ? "cursor-vera flex h-screen w-full flex-col justify-center overflow-hidden bg-papel px-4 py-4 md:px-8"
          : "cursor-vera mx-auto flex w-full max-w-5xl flex-col px-4 py-6 md:px-8"
      }
    >
      <div
        className={`painel relative flex flex-col overflow-y-auto p-6 md:p-10 ${telaCheia ? "flex-1" : "min-h-[82vh]"}`}
        // Em tela cheia, dá zoom no conteúdo inteiro: o texto e as peças crescem junto
        // com a tela grande, em vez de ficarem pequenos no meio do projetor.
        style={{ zoom: telaCheia ? 1.25 : 1 } as React.CSSProperties}
      >
        <div key={slide.chave} className="slide-entra flex min-h-full flex-col justify-center">
          {slide.no}
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between gap-3">
        <button type="button" onClick={() => ir(indice - 1)} disabled={indice === 0} aria-label="Slide anterior" className="pressiona flex size-12 shrink-0 items-center justify-center rounded-total border-[3px] border-tinta bg-papel-2 shadow-bloco-sm disabled:opacity-30">
          <Icone nome="seta" tamanho={22} className="rotate-180" />
        </button>

        <div className="flex flex-wrap items-center justify-center gap-2" role="tablist" aria-label="Slides">
          {SLIDES.map((s, i) => (
            <button key={s.chave} type="button" role="tab" aria-selected={i === indice} aria-label={`Ir para o slide ${i + 1}`} onClick={() => ir(i)} className={`size-3.5 rounded-total border-2 border-tinta transition-colors ${i === indice ? "bg-vermelho" : "bg-papel-2 hover:bg-vermelho-suave"}`} />
          ))}
        </div>

        <div className="flex items-center gap-3">
          <button type="button" onClick={alternarTelaCheia} aria-label={telaCheia ? "Sair da tela cheia" : "Tela cheia"} title={telaCheia ? "Sair da tela cheia" : "Tela cheia"} className="pressiona flex size-12 shrink-0 items-center justify-center rounded-total border-[3px] border-tinta bg-papel-2 shadow-bloco-sm">
            <svg viewBox="0 0 24 24" className="size-6" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
              {telaCheia ? <path d="M9 4v5H4M15 4v5h5M9 20v-5H4M15 20v-5h5" /> : <path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" />}
            </svg>
          </button>
          <span className="font-display text-xl tabular-nums text-tinta-2">{indice + 1}/{total}</span>
          <button type="button" onClick={() => ir(indice + 1)} disabled={indice === total - 1} aria-label="Próximo slide" className="pressiona flex size-12 shrink-0 items-center justify-center rounded-total border-[3px] border-tinta bg-vermelho text-white shadow-bloco-sm disabled:opacity-30">
            <Icone nome="seta" tamanho={22} />
          </button>
        </div>
      </div>
    </div>
  );
}
