"use client";

/**
 * Apresentação do projeto em formato de slides, dentro do próprio app.
 *
 * Prancha de quadrinho (vera-estilo): painéis, balões, retícula, carimbos e a arte da
 * Vera. Mostra persona, pipeline N0–N4, dificuldade, os 13 sinais (ML e LLM), as faixas
 * de veracidade, as frentes, os princípios, a metodologia (CBL + Scrum), a equipe e os
 * números. Um slide é demonstração ao vivo: roda o pipeline de verdade.
 *
 * Navegação com **builds**: avançar primeiro revela os blocos do slide, um a um, e só
 * depois passa de folha (← → no teclado, setas na tela, bolinhas). Em tela cheia dá
 * zoom para o texto crescer. Animações seguem o framework de design engineering (Emil
 * Kowalski): easing forte, só transform/opacity, entra de scale(0.96) com blur sutil,
 * stagger curto; prefers-reduced-motion neutraliza o movimento pelo CSS global.
 */

import Image from "next/image";
import { QRCodeSVG } from "qrcode.react";
import { useCallback, useEffect, useRef, useState } from "react";

import { DemoAoVivo } from "@/components/sobre/DemoAoVivo";
import { Balao } from "@/components/ui/Balao";
import { Icone, type NomeDoIcone } from "@/components/ui/Icone";

const EASE = "cubic-bezier(0.23, 1, 0.32, 1)"; // ease-out forte (Emil)

// --- Dados ---------------------------------------------------------------------------

const CAMADAS: Array<{ id: string; nome: string; icone: NomeDoIcone; pergunta: string; comoFaz: string; custo: string }> = [
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

const DIMENSOES: Array<{ nome: string; pontos: number; icone: NomeDoIcone; marca: string; sinais: Array<{ id: string; nome: string; peso: number }> }> = [
  { nome: "Fonte", pontos: 35, icone: "site", marca: "quem falou", sinais: [
    { id: "S-01", nome: "Reputação do veículo", peso: 12 },
    { id: "S-02", nome: "Histórico de fakes do domínio", peso: 8 },
    { id: "S-03", nome: "Idade do domínio (RDAP/WHOIS)", peso: 6 },
    { id: "S-04", nome: "Transparência da página", peso: 5 },
    { id: "S-05", nome: "Autor identificável", peso: 4 },
  ] },
  { nome: "Conteúdo", pontos: 25, icone: "texto", marca: "aprendizado de máquina", sinais: [
    { id: "S-06", nome: "Classificador de estilo (TF-IDF + SVM/RL)", peso: 10 },
    { id: "S-07", nome: "Sensacionalismo", peso: 5 },
    { id: "S-08", nome: "Intensidade emocional (NRC)", peso: 5 },
    { id: "S-09", nome: "Cita fontes verificáveis", peso: 3 },
    { id: "S-10", nome: "Texto gerado por IA", peso: 2 },
  ] },
  { nome: "Corroboração", pontos: 40, icone: "jornal", marca: "onde entra a LLM", sinais: [
    { id: "S-11", nome: "Veículos confiáveis que publicaram", peso: 15 },
    { id: "S-12", nome: "NLI: evidências sustentam ou contradizem", peso: 20 },
    { id: "S-13", nome: "Originalidade (é cópia alterada?)", peso: 5 },
  ] },
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

// --- Peças ---------------------------------------------------------------------------

/**
 * Revela um bloco quando `mostrar` fica verdadeiro (um passo do slide). Entra de
 * scale(0.96) + translateY com blur sutil (nada surge do nada), easing forte, só
 * transform/opacity/filter. prefers-reduced-motion zera a transição pelo CSS global.
 */
function Revela({
  mostrar,
  children,
  className = "",
  atraso = 0,
}: {
  mostrar: boolean;
  children: React.ReactNode;
  className?: string;
  atraso?: number;
}) {
  return (
    <div
      className={className}
      style={{
        transition: `opacity 440ms ${EASE}, transform 440ms ${EASE}, filter 440ms ${EASE}`,
        transitionDelay: `${atraso}ms`,
        opacity: mostrar ? 1 : 0,
        transform: mostrar ? "none" : "translateY(16px) scale(0.96)",
        filter: mostrar ? "none" : "blur(4px)",
        pointerEvents: mostrar ? "auto" : "none",
      }}
    >
      {children}
    </div>
  );
}

function Reticula({ className = "" }: { className?: string }) {
  return <span aria-hidden className={`reticula pointer-events-none absolute inset-0 ${className}`} />;
}

function Carimbo({ children, cor = "bg-vermelho" }: { children: React.ReactNode; cor?: string }) {
  return (
    <span className={`carimbo inline-flex items-center gap-1.5 rounded-md border-[3px] border-tinta ${cor} px-3 py-1 font-display text-xl text-white shadow-bloco-sm`}>
      {children}
    </span>
  );
}

function Super({ icone, texto }: { icone: NomeDoIcone; texto: string }) {
  return (
    <p className="flex w-fit items-center gap-2 font-display text-xl uppercase tracking-wide text-vermelho">
      <Icone nome={icone} tamanho={24} />
      <span className="relative">
        {texto}
        {/* Risco vermelho de marcador sob o rótulo: toque de cordel/quadrinho. */}
        <span aria-hidden className="absolute -bottom-1 left-0 h-1.5 w-full rounded-total bg-vermelho/40" />
      </span>
    </p>
  );
}

const CARD = "rounded-md border-[3px] border-tinta bg-papel-2 shadow-bloco";

/**
 * Slide do QR code: aponta para o endereço que a pessoa abriu (window.location.origin),
 * então o QR já leva ao IP:3000 da rede sem configurar nada. A URL é lida no cliente
 * (useEffect) para não divergir entre servidor e navegador.
 */
function SlideQRCode() {
  const [url, setUrl] = useState("");
  useEffect(() => setUrl(window.location.origin), []);
  return (
    <div className="flex flex-col items-center gap-5 text-center">
      <Super icone="link" texto="No seu celular" />
      <h2 className="font-display text-5xl leading-none">Abre aí e confere comigo</h2>
      <p className="max-w-xl text-2xl">Aponta a câmera no código que a Vera abre no seu telefone.</p>
      <div className="estufa rounded-md border-[3px] border-tinta bg-white p-4 shadow-bloco">
        {url ? (
          <QRCodeSVG value={url} size={240} level="M" marginSize={0} />
        ) : (
          <div className="size-60" aria-hidden />
        )}
      </div>
      {url && <Carimbo cor="bg-vermelho">{url.replace(/^https?:\/\//, "")}</Carimbo>}
    </div>
  );
}

// --- Slides --------------------------------------------------------------------------

type Slide = { chave: string; passos: number; render: (p: number) => React.ReactNode };

const SLIDES_DEF: Slide[] = [
  {
    chave: "capa",
    passos: 0,
    render: () => (
      <div className="relative flex flex-col items-center gap-5 overflow-hidden text-center">
        <Reticula className="text-vermelho" />
        <Image src="/vera-corpo-apontando.png" alt="Senhora Vera apontando" width={260} height={320} priority className="estufa relative h-56 w-auto drop-shadow-[6px_6px_0_var(--tinta)] md:h-72" />
        <div className="surge relative" style={{ "--atraso": "120ms" } as React.CSSProperties}>
          <Carimbo cor="bg-ocre">Residência em IA · Challenge 1 · Grupo 4</Carimbo>
        </div>
        <h1 className="surge relative font-display text-5xl leading-none md:text-6xl" style={{ "--atraso": "200ms" } as React.CSSProperties}>A Senhora Vera</h1>
        <div className="surge relative w-full max-w-xl" style={{ "--atraso": "320ms" } as React.CSSProperties}>
          <Balao><p className="fonte-mao text-3xl">“O que é que tu quer saber que é verdade?”</p></Balao>
        </div>
        <p className="surge relative max-w-2xl text-2xl" style={{ "--atraso": "440ms" } as React.CSSProperties}>
          Uma senhora do Recife que sabe de tudo, mas <strong>não repassa nada sem conferir a fonte antes</strong>.
        </p>
      </div>
    ),
  },
  {
    chave: "equipe",
    passos: 0,
    render: () => (
      <div className="flex flex-col justify-center">
        <Super icone="assinatura" texto="Quem fez" />
        <h2 className="mb-6 font-display text-5xl leading-none">O Grupo 4</h2>
        <ul className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
          {EQUIPE.map((pessoa, i) => (
            <li key={pessoa.nome} className="sobe-pop" style={{ "--atraso": `${i * 70}ms` } as React.CSSProperties}>
              <a href={`https://github.com/${pessoa.github}`} target="_blank" rel="noopener noreferrer" className={`flex h-full flex-col items-center gap-2 p-4 text-center transition-transform duration-200 hover:-translate-y-1 ${CARD}`}>
                <Image src={pessoa.foto} alt={`Foto de ${pessoa.nome} no GitHub`} width={96} height={96} className="size-24 rounded-total border-[3px] border-tinta object-cover" />
                <span className="font-display text-2xl leading-none">{pessoa.nome}</span>
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
    passos: 1,
    render: (p) => (
      <div className="flex flex-col justify-center gap-5">
        <div>
          <Super icone="coracao" texto="A ideia" />
          <h2 className="font-display text-5xl leading-none">Checar sem decidir por você</h2>
        </div>
        <div className="grid items-center gap-5 md:grid-cols-[1fr_auto]">
          <div className="flex flex-col gap-4">
            <Balao><p className="text-2xl leading-snug">Você manda a notícia, eu cruzo com <strong>fontes confiáveis</strong> e te mostro <strong>por que</strong> ela parece verdadeira ou falsa.</p></Balao>
            <Revela mostrar={p >= 1}>
              <p className="text-xl leading-relaxed text-tinta-2">Diferente de um classificador que só diz “fake / não fake”, a Vera mostra o caminho, para <strong>fortalecer o pensamento crítico</strong>, não substituir.</p>
            </Revela>
          </div>
          <Image src="/vera-corpo.png" alt="Senhora Vera avaliando" width={220} height={300} className="hidden h-64 w-auto drop-shadow-[6px_6px_0_var(--tinta)] md:block" />
        </div>
      </div>
    ),
  },
  {
    chave: "camadas",
    passos: 4,
    render: (p) => (
      <div className="flex flex-col justify-center">
        <Super icone="lupa" texto="Como investiga" />
        <h2 className="mb-2 font-display text-5xl leading-none">Investigação em camadas</h2>
        <p className="mb-5 text-xl text-tinta-2">Da mais barata para a mais cara. Achou certeza, <strong>parou e respondeu</strong>.</p>
        <ol className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {CAMADAS.map((c, i) => (
            <Revela key={c.id} mostrar={p >= i} className={`flex flex-col gap-2 p-4 ${CARD}`}>
              <div className="flex items-center justify-between">
                <span className="font-display text-3xl">{c.id}</span>
                <Icone nome={c.icone} tamanho={30} className="text-vermelho" />
              </div>
              <span className="font-display text-2xl leading-none">{c.nome}</span>
              <span className="text-lg font-bold text-tinta-2">{c.pergunta}</span>
              <span className="text-base">{c.comoFaz}</span>
              <span className="mt-auto inline-flex w-fit rounded-total border-2 border-borda px-2 text-sm font-bold text-tinta-3">{c.custo}</span>
            </Revela>
          ))}
        </ol>
      </div>
    ),
  },
  {
    chave: "dificuldade",
    passos: 2,
    render: (p) => (
      <div className="flex flex-col justify-center">
        <Super icone="etiqueta" texto="O quanto custa" />
        <h2 className="mb-5 font-display text-5xl leading-none">A dificuldade da notícia</h2>
        <div className="grid gap-4 md:grid-cols-3">
          {DIFICULDADE.map((d, i) => (
            <Revela key={d.nivel} mostrar={p >= i} className={`flex flex-col gap-2 p-5 ${CARD}`}>
              <span className="inline-flex w-fit items-center gap-2 rounded-md border-[3px] border-tinta px-3 py-1 font-display text-2xl text-white" style={{ background: d.cor }}>{d.nivel}</span>
              <span className="font-display text-xl text-tinta-2">parou em {d.onde}</span>
              <span className="text-lg">{d.exemplo}</span>
            </Revela>
          ))}
        </div>
      </div>
    ),
  },
  {
    chave: "demo",
    passos: 0,
    render: () => (
      <div className="flex flex-col">
        <Super icone="robo" texto="Ao vivo" />
        <h2 className="font-display text-5xl leading-none">Vê a Vera trabalhando</h2>
        <p className="mb-4 text-xl text-tinta-2">Isto não é vídeo: toca num exemplo e o pipeline roda de verdade, aqui mesmo.</p>
        <DemoAoVivo />
      </div>
    ),
  },
  {
    chave: "sinais",
    passos: 2,
    render: (p) => (
      <div className="flex flex-col justify-center">
        <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
          <div>
            <Super icone="contas" texto="O que ela mede" />
            <h2 className="font-display text-5xl leading-none">13 sinais, 100 pontos</h2>
          </div>
          <Carimbo cor="bg-confirmada">a média só do que deu pra medir</Carimbo>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {DIMENSOES.map((d, i) => (
            <Revela key={d.nome} mostrar={p >= i} className={`flex flex-col p-4 ${CARD}`}>
              <div className="flex items-center gap-2">
                <Icone nome={d.icone} tamanho={24} className="text-vermelho" />
                <h3 className="font-display text-2xl">{d.nome}</h3>
                <span className="ml-auto font-display text-2xl tabular-nums text-tinta-2">{d.pontos}</span>
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
            </Revela>
          ))}
        </div>
      </div>
    ),
  },
  {
    chave: "faixas",
    passos: 4,
    render: (p) => (
      <div className="flex flex-col justify-center">
        <Super icone="quase" texto="O veredito" />
        <h2 className="mb-2 font-display text-5xl leading-none">As faixas de veracidade</h2>
        <p className="mb-5 text-xl text-tinta-2">A cor comunica o resultado, e nunca sozinha: vem sempre com a palavra escrita.</p>
        <ul className="flex flex-col gap-3">
          {FAIXAS.map((f, i) => (
            <Revela key={f.nome} mostrar={p >= i} className={`flex items-center gap-4 p-3 ${CARD}`}>
              <span className="size-10 shrink-0 rounded-md border-[3px] border-tinta" style={{ background: f.cor }} />
              <span className="font-display text-2xl md:text-3xl">{f.nome}</span>
              <span className="ml-auto font-display text-2xl tabular-nums text-tinta-3">{i * 20}–{(i + 1) * 20}</span>
            </Revela>
          ))}
        </ul>
      </div>
    ),
  },
  {
    chave: "frentes",
    passos: 3,
    render: (p) => (
      <div className="flex flex-col justify-center">
        <Super icone="etiqueta" texto="A engenharia" />
        <h2 className="mb-5 font-display text-5xl leading-none">As frentes do projeto</h2>
        <div className="grid gap-4 md:grid-cols-2">
          {FRENTES.map((f, i) => (
            <Revela key={f.titulo} mostrar={p >= i} className={`p-5 ${CARD}`}>
              <h3 className="flex items-center gap-2 font-display text-2xl"><Icone nome={f.icone} tamanho={26} className="text-vermelho" />{f.titulo}</h3>
              <ul className="mt-2 space-y-1.5">
                {f.itens.map((it) => (
                  <li key={it} className="flex items-start gap-2 text-lg"><Icone nome="visto" tamanho={20} className="mt-0.5 shrink-0 text-confirmada" /><span>{it}</span></li>
                ))}
              </ul>
            </Revela>
          ))}
        </div>
      </div>
    ),
  },
  {
    chave: "principios",
    passos: 3,
    render: (p) => (
      <div className="flex flex-col justify-center">
        <Super icone="coracao" texto="O jeito dela" />
        <h2 className="mb-5 font-display text-5xl leading-none">As regras da casa</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {PRINCIPIOS.map((pr, i) => (
            <Revela key={pr.titulo} mostrar={p >= i} className={`flex items-start gap-3 p-5 ${CARD}`}>
              <Icone nome={pr.icone} tamanho={34} className="mt-0.5 shrink-0 text-vermelho" />
              <div>
                <h3 className="font-display text-2xl leading-none">{pr.titulo}</h3>
                <p className="mt-1.5 text-lg">{pr.texto}</p>
              </div>
            </Revela>
          ))}
        </div>
      </div>
    ),
  },
  {
    chave: "metodologia",
    passos: 2,
    render: (p) => (
      <div className="relative flex flex-col items-center gap-5 overflow-hidden text-center">
        <Reticula className="text-ocre" />
        <Super icone="etiqueta" texto="Como foi feito" />
        <h2 className="relative font-display text-6xl leading-none">CBL + Scrum</h2>
        <p className="relative max-w-2xl text-2xl leading-relaxed">Challenge Based Learning com Scrum adaptado, no tema <strong>Fake News e Desinformação</strong>. As cinco camadas do pipeline foram divididas entre as cinco pessoas.</p>
        <Revela mostrar={p >= 1} className="relative flex flex-wrap items-center justify-center gap-3">
          <Carimbo cor="bg-vermelho">1 Product Owner</Carimbo>
          <Carimbo cor="bg-ocre">1 Scrum Master</Carimbo>
          <Carimbo cor="bg-confirmada">5 Developers</Carimbo>
        </Revela>
        <Revela mostrar={p >= 2} className="relative">
          <p className="text-lg text-tinta-2">Estimativa por Planning Poker · backlog em épicos e histórias · requisitos RF e regras RN.</p>
        </Revela>
      </div>
    ),
  },
  {
    chave: "numeros",
    passos: 4,
    render: (p) => (
      <div className="flex flex-col items-center gap-6 text-center">
        <Super icone="contas" texto="Em números" />
        <h2 className="font-display text-5xl leading-none">O motor da Vera</h2>
        <ul className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {NUMEROS.map((n, i) => (
            <Revela key={n.rotulo} mostrar={p >= i} className={`flex flex-col items-center px-6 py-5 ${CARD}`}>
              <span className="font-display text-6xl leading-none text-vermelho">{n.valor}</span>
              <span className="mt-1 font-display text-2xl text-tinta-2">{n.rotulo}</span>
            </Revela>
          ))}
        </ul>
        <Revela mostrar={p >= 3} className="w-full max-w-md">
          <Balao><p className="fonte-mao text-3xl">“Manda a notícia aí, meu bem, que eu vou atrás.”</p></Balao>
        </Revela>
      </div>
    ),
  },
  {
    chave: "qrcode",
    passos: 0,
    render: () => <SlideQRCode />,
  },
];

/**
 * Ordem de exibição (fluxo da apresentação):
 * capa (fisga) → QR (todo mundo abre no celular) → equipe → a ideia → como investiga
 * (camadas, dificuldade) → demo ao vivo → o que mede (sinais, faixas) → engenharia →
 * princípios → como foi feito → números (fecho).
 */
const ORDEM = [
  "capa",
  "qrcode",
  "equipe",
  "visao",
  "camadas",
  "dificuldade",
  "demo",
  "sinais",
  "faixas",
  "frentes",
  "principios",
  "metodologia",
  "numeros",
] as const;

const SLIDES: Slide[] = ORDEM.map((c) => SLIDES_DEF.find((s) => s.chave === c)!);

// --- Deck ----------------------------------------------------------------------------

export function Apresentacao() {
  const [indice, setIndice] = useState(0);
  const [passo, setPasso] = useState(0);
  const [telaCheia, setTelaCheia] = useState(false);
  const deckRef = useRef<HTMLDivElement>(null);
  const total = SLIDES.length;
  const slide = SLIDES[indice];

  const avancar = useCallback(() => {
    setPasso((p) => {
      if (p < slide.passos) return p + 1;
      if (indice < total - 1) {
        setIndice(indice + 1);
        return 0;
      }
      return p;
    });
  }, [indice, slide.passos, total]);

  const voltar = useCallback(() => {
    setPasso((p) => {
      if (p > 0) return p - 1;
      if (indice > 0) {
        const anterior = indice - 1;
        setIndice(anterior);
        return SLIDES[anterior].passos; // volta já com o slide anterior "montado"
      }
      return p;
    });
  }, [indice]);

  const irPara = useCallback((i: number) => {
    setIndice(i);
    setPasso(0);
  }, []);

  useEffect(() => {
    function aoTeclar(e: KeyboardEvent) {
      if (e.key === "ArrowRight" || e.key === " ") {
        e.preventDefault();
        avancar();
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        voltar();
      }
    }
    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
  }, [avancar, voltar]);

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

  const noInicio = indice === 0 && passo === 0;
  const noFim = indice === total - 1 && passo === slide.passos;

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
        style={{ zoom: telaCheia ? 1.25 : 1 } as React.CSSProperties}
      >
        {/* Retícula de impressão nos cantos (margem, nunca atrás do texto): dá a cada
            slide a textura de página de quadrinho, de leve. */}
        <span aria-hidden className="reticula pointer-events-none absolute left-0 top-0 h-28 w-28" />
        <span aria-hidden className="reticula pointer-events-none absolute bottom-0 right-0 h-28 w-28" />

        {/* key só no índice: trocar de slide re-dispara a entrada; mudar de passo não
            remonta (os blocos revelam por transição, sem reiniciar o slide). */}
        <div key={slide.chave} className="slide-entra relative flex min-h-full flex-col justify-center">
          {slide.render(passo)}
        </div>

        {/* Progresso dos passos do slide atual (só quando há builds). */}
        {slide.passos > 0 && (
          <div className="pointer-events-none absolute right-4 top-4 flex gap-1.5" aria-hidden>
            {Array.from({ length: slide.passos + 1 }).map((_, i) => (
              <span key={i} className="size-2 rounded-total border border-tinta" style={{ background: i <= passo ? "var(--vermelho)" : "var(--papel-3)" }} />
            ))}
          </div>
        )}
      </div>

      {/* Em tela cheia os controles sao escondidos: navega-se por teclado (setas /
          espaco) e sai-se com Esc. Fora dela, a barra completa aparece. */}
      <div className={`mt-4 items-center justify-between gap-3 ${telaCheia ? "hidden" : "flex"}`}>
        <button type="button" onClick={voltar} disabled={noInicio} aria-label="Voltar" className="pressiona flex size-12 shrink-0 items-center justify-center rounded-total border-[3px] border-tinta bg-papel-2 shadow-bloco-sm transition-transform active:scale-95 disabled:opacity-30">
          <Icone nome="seta" tamanho={22} className="rotate-180" />
        </button>

        <div className="flex flex-wrap items-center justify-center gap-2" role="tablist" aria-label="Slides">
          {SLIDES.map((s, i) => (
            <button key={s.chave} type="button" role="tab" aria-selected={i === indice} aria-label={`Ir para o slide ${i + 1}`} onClick={() => irPara(i)} className={`size-3.5 rounded-total border-2 border-tinta transition-colors ${i === indice ? "bg-vermelho" : "bg-papel-2 hover:bg-vermelho-suave"}`} />
          ))}
        </div>

        <div className="flex items-center gap-3">
          <button type="button" onClick={alternarTelaCheia} aria-label={telaCheia ? "Sair da tela cheia" : "Tela cheia"} title={telaCheia ? "Sair da tela cheia" : "Tela cheia"} className="pressiona flex size-12 shrink-0 items-center justify-center rounded-total border-[3px] border-tinta bg-papel-2 shadow-bloco-sm transition-transform active:scale-95">
            <svg viewBox="0 0 24 24" className="size-6" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
              {telaCheia ? <path d="M9 4v5H4M15 4v5h5M9 20v-5H4M15 20v-5h5" /> : <path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" />}
            </svg>
          </button>
          <span className="font-display text-2xl tabular-nums text-tinta-2">{indice + 1}/{total}</span>
          <button type="button" onClick={avancar} disabled={noFim} aria-label="Avançar" className="pressiona flex size-12 shrink-0 items-center justify-center rounded-total border-[3px] border-tinta bg-vermelho text-white shadow-bloco-sm transition-transform active:scale-95 disabled:opacity-30">
            <Icone nome="seta" tamanho={22} />
          </button>
        </div>
      </div>
    </div>
  );
}
