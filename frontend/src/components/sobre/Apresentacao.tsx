"use client";


import { Icone, type NomeDoIcone } from "@/components/ui/Icone";
import { VeraAvatar } from "@/components/vera/VeraAvatar";


/**
 * Tela de apresentação do projeto (Residência em IA · Challenge 1 · Grupo 4).
 *
 * Mostra, para quem chega de fora, o produto inteiro: a persona, o pipeline em camadas
 * N0–N4, os sinais que pesam o veredito (incluindo a parte de ML e a de LLM), a stack de
 * cada frente e a equipe. O conteúdo vem da branch `docs` (funcionamento, persona,
 * classificação) e do ARQUITETURA.md.
 *
 * É só leitura (sem estado), mas Client Component porque usa `Icone` e `VeraAvatar`,
 * que dependem de contexto do React; a rota em si (`app/sobre/page.tsx`) fica como
 * Server Component só para exportar o `metadata`.
 */

// --- Dados da apresentação -----------------------------------------------------------

const CAMADAS: Array<{
  id: string;
  nome: string;
  icone: NomeDoIcone;
  pergunta: string;
  comoFaz: string;
  custo: string;
}> = [
  {
    id: "N0",
    nome: "Cache",
    icone: "relogio",
    pergunta: "Já conferi isso antes?",
    comoFaz: "Reaproveita uma checagem já feita da mesma URL ou afirmação.",
    custo: "Instantâneo",
  },
  {
    id: "N1",
    nome: "Fonte",
    icone: "site",
    pergunta: "Quem publicou?",
    comoFaz:
      "Reputação na base curada, idade do domínio (RDAP/WHOIS) e checagens de agência já existentes.",
    custo: "Muito baixo",
  },
  {
    id: "N2",
    nome: "Conteúdo",
    icone: "texto",
    pergunta: "Como foi escrito?",
    comoFaz:
      "Classificador de estilo (TF-IDF + SVM/Regressão), sensacionalismo e intensidade emocional.",
    custo: "Baixo",
  },
  {
    id: "N3",
    nome: "Corroboração",
    icone: "jornal",
    pergunta: "Quem mais publicou?",
    comoFaz:
      "Busca notícias semelhantes (Google Notícias, GDELT) e mede similaridade por embeddings.",
    custo: "Médio",
  },
  {
    id: "N4",
    nome: "IA generativa",
    icone: "robo",
    pergunta: "As fontes sustentam?",
    comoFaz:
      "Uma LLM confere alegação por alegação contra as evidências (NLI: sustenta, contradiz ou é neutro).",
    custo: "Alto",
  },
];

const DIMENSOES: Array<{
  nome: string;
  pontos: number;
  icone: NomeDoIcone;
  resumo: string;
  sinais: Array<{ id: string; nome: string; peso: number }>;
}> = [
  {
    nome: "Fonte",
    pontos: 35,
    icone: "site",
    resumo: "Quem publicou e se dá para confiar no veículo.",
    sinais: [
      { id: "S-01", nome: "Reputação do veículo na base curada", peso: 12 },
      { id: "S-02", nome: "Histórico de fakes do domínio (12 meses)", peso: 8 },
      { id: "S-03", nome: "Idade do domínio (RDAP/WHOIS)", peso: 6 },
      { id: "S-04", nome: "Transparência da página (autor, data, contato)", peso: 5 },
      { id: "S-05", nome: "Autor identificável", peso: 4 },
    ],
  },
  {
    nome: "Conteúdo",
    pontos: 25,
    icone: "texto",
    resumo: "Como o texto foi escrito — o território do aprendizado de máquina.",
    sinais: [
      { id: "S-06", nome: "Classificador estilístico (TF-IDF + SVM/RL)", peso: 10 },
      { id: "S-07", nome: "Sensacionalismo (caixa alta, clickbait, urgência)", peso: 5 },
      { id: "S-08", nome: "Intensidade emocional (NRC: medo, raiva)", peso: 5 },
      { id: "S-09", nome: "Cita fontes verificáveis", peso: 3 },
      { id: "S-10", nome: "Probabilidade de texto gerado por IA", peso: 2 },
    ],
  },
  {
    nome: "Corroboração",
    pontos: 40,
    icone: "jornal",
    resumo: "Se outros veículos publicaram o mesmo fato — onde entra a LLM.",
    sinais: [
      { id: "S-11", nome: "Veículos confiáveis que publicaram o mesmo", peso: 15 },
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
      "Python + FastAPI, arquitetura hexagonal (o núcleo não conhece a infraestrutura)",
      "Cadeia de responsabilidade: as camadas N0–N4 e a regra de parada",
      "PostgreSQL com pgvector para o cache e a busca por similaridade",
    ],
  },
  {
    titulo: "Aprendizado de máquina",
    icone: "etiqueta",
    itens: [
      "Classificador de estilo S-06: TF-IDF + SVM / Regressão Logística",
      "Intensidade emocional com o NRC Emotion Lexicon (S-08)",
      "Notebooks de EDA por camada e datasets em Parquet para treino e avaliação",
    ],
  },
  {
    titulo: "IA generativa (LLM)",
    icone: "robo",
    itens: [
      "Camada N4: LLM servida pelo Ollama (llama3), chamada só quando N0–N3 não bastam",
      "Inferência de linguagem (NLI): confere se cada evidência sustenta ou contradiz",
      "A explicação do veredito pode ser montada por templates (modo econômico) ou pela LLM",
    ],
  },
  {
    titulo: "Frontend",
    icone: "conversa",
    itens: [
      "Next.js + TypeScript + Tailwind, em formato de chat com a persona",
      "Mostra o andamento da investigação, os sinais e as fontes de cada checagem",
      "Site responsivo e instalável (PWA) e uma extensão de navegador",
    ],
  },
];

const PRINCIPIOS: Array<{ icone: NomeDoIcone; titulo: string; texto: string }> = [
  {
    icone: "lupa",
    titulo: "Mostra o caminho",
    texto:
      "A Vera não responde só “fake ou não fake”. Ela mostra quais fontes olhou, que sinais achou e quanto cada um pesou — a pessoa decide com o próprio pensamento crítico.",
  },
  {
    icone: "quase",
    titulo: "Nunca crava certeza",
    texto:
      "Os rótulos são “provavelmente falsa”, “provavelmente verdadeira”, “confirmada por fontes”. Ela é desconfiada por ofício, inclusive de si mesma.",
  },
  {
    icone: "espera",
    titulo: "Não sei é não sei",
    texto:
      "Um sinal sem dado fica de fora da conta e nunca vale zero: “não consegui medir” é diferente de “medi e está ruim”. Sem corroboração, ela prefere ficar em aberto.",
  },
  {
    icone: "contas",
    titulo: "Gasta a IA só quando precisa",
    texto:
      "A LLM é a camada mais cara e só é chamada quando as anteriores não resolveram. É o que torna o produto viável — e mais rápido na maioria dos casos.",
  },
];

const EQUIPE: Array<{ nome: string; papel: string }> = [
  { nome: "Maykon Soares", papel: "Product Owner · dev" },
  { nome: "Ian Costa", papel: "Scrum Master · dev" },
  { nome: "Luísa Brambilla", papel: "Desenvolvimento" },
  { nome: "Natália Evelin", papel: "Desenvolvimento" },
  { nome: "Rebeca Bontempo", papel: "Desenvolvimento" },
];

// --- Blocos reutilizáveis ------------------------------------------------------------

function TituloDeSecao({ icone, texto }: { icone: NomeDoIcone; texto: string }) {
  return (
    <h2 className="flex items-center gap-2 font-display text-2xl">
      <Icone nome={icone} tamanho={26} className="text-vermelho" />
      {texto}
    </h2>
  );
}

// --- Página --------------------------------------------------------------------------

export function Apresentacao() {
  return (
    <div className="mx-auto w-full max-w-5xl px-4 py-8 md:px-8">
      {/* Abertura: quem é a Vera */}
      <header className="painel overflow-hidden">
        <div className="relative flex flex-col items-center gap-4 p-6 text-center md:flex-row md:items-center md:gap-6 md:p-8 md:text-left">
          <VeraAvatar humor="satisfeita" tamanho={120} className="shrink-0" />
          <div className="min-w-0">
            <p className="font-display text-sm uppercase tracking-wide text-vermelho">
              Residência em IA · Challenge 1 · Grupo 4
            </p>
            <h1 className="mt-1 font-display text-4xl leading-none">A Senhora Vera</h1>
            <p className="mt-3 text-lg">
              Uma senhora do Recife que sabe de tudo — mas <strong>não repassa nada sem
              conferir a fonte antes</strong>. Você manda a notícia, ela investiga em
              vários lugares e mostra o porquê.
            </p>
            <p className="fonte-mao mt-3 text-xl text-tinta-2">
              “O que é que tu quer saber que é verdade?”
            </p>
          </div>
        </div>
      </header>

      {/* Visão do produto */}
      <section className="mt-6 rounded-md border-[3px] border-tinta bg-papel-2 p-5 shadow-bloco-sm">
        <p className="text-base leading-relaxed">
          Para quem recebe notícia por rede social, mensageiro e site e não sabe se pode
          confiar, a Vera é uma <strong>checadora em formato de conversa</strong> que
          cruza o que você leu com fontes confiáveis e <strong>explica</strong> por que
          aquilo parece verdadeiro ou falso. Diferente de um classificador que só diz
          “fake / não fake”, ela mostra o caminho — para ajudar o pensamento crítico, não
          substituir.
        </p>
      </section>

      {/* Como funciona: camadas */}
      <section className="mt-10">
        <TituloDeSecao icone="lupa" texto="Como a Vera investiga" />
        <p className="mt-2 text-base text-tinta-2">
          Ela confere em <strong>camadas</strong>, da mais barata para a mais cara.
          Depois de cada uma, calcula o quanto já tem certeza; se bastou, para e responde.
          A camada em que parou vira a <strong>dificuldade</strong> da notícia.
        </p>
        <ol className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {CAMADAS.map((c) => (
            <li
              key={c.id}
              className="flex flex-col gap-2 rounded-md border-[3px] border-tinta bg-papel-2 p-3 shadow-bloco-sm"
            >
              <div className="flex items-center justify-between">
                <span className="font-display text-xl">{c.id}</span>
                <Icone nome={c.icone} tamanho={26} className="text-vermelho" />
              </div>
              <span className="font-display text-lg leading-none">{c.nome}</span>
              <span className="text-sm font-bold text-tinta-2">{c.pergunta}</span>
              <span className="text-sm">{c.comoFaz}</span>
              <span className="mt-auto inline-flex w-fit rounded-total border-2 border-borda px-2 text-xs font-bold text-tinta-3">
                {c.custo}
              </span>
            </li>
          ))}
        </ol>
      </section>

      {/* Sinais por dimensão */}
      <section className="mt-10">
        <TituloDeSecao icone="contas" texto="O que a Vera mede — os sinais" />
        <p className="mt-2 text-base text-tinta-2">
          O veredito é a média ponderada de até <strong>13 sinais</strong>, divididos em
          três dimensões que somam 100 pontos. Cada sinal vale um tanto; o que ela não
          consegue medir fica de fora da conta.
        </p>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          {DIMENSOES.map((d) => (
            <div
              key={d.nome}
              className="flex flex-col rounded-md border-[3px] border-tinta bg-papel-2 p-4 shadow-bloco-sm"
            >
              <div className="flex items-center gap-2">
                <Icone nome={d.icone} tamanho={22} className="text-vermelho" />
                <h3 className="font-display text-xl">{d.nome}</h3>
                <span className="ml-auto font-display text-lg tabular-nums text-tinta-2">
                  {d.pontos} pts
                </span>
              </div>
              <p className="mt-1 text-sm text-tinta-2">{d.resumo}</p>
              <ul className="mt-3 space-y-1.5">
                {d.sinais.map((s) => (
                  <li key={s.id} className="flex items-baseline gap-2 text-sm">
                    <span className="font-mono text-xs text-tinta-3">{s.id}</span>
                    <span className="min-w-0 flex-1">{s.nome}</span>
                    <span className="font-bold tabular-nums">{s.peso}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* Frentes de tecnologia */}
      <section className="mt-10">
        <TituloDeSecao icone="etiqueta" texto="As frentes do projeto" />
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {FRENTES.map((f) => (
            <div
              key={f.titulo}
              className="rounded-md border-[3px] border-tinta bg-papel-2 p-4 shadow-bloco-sm"
            >
              <h3 className="flex items-center gap-2 font-display text-xl">
                <Icone nome={f.icone} tamanho={22} className="text-vermelho" />
                {f.titulo}
              </h3>
              <ul className="mt-2 space-y-1.5">
                {f.itens.map((i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <Icone
                      nome="visto"
                      tamanho={16}
                      className="mt-0.5 shrink-0 text-confirmada"
                    />
                    <span>{i}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* Princípios */}
      <section className="mt-10">
        <TituloDeSecao icone="coracao" texto="O jeito da Vera" />
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          {PRINCIPIOS.map((p) => (
            <div
              key={p.titulo}
              className="flex items-start gap-3 rounded-md border-[3px] border-tinta bg-papel-2 p-4 shadow-bloco-sm"
            >
              <Icone nome={p.icone} tamanho={26} className="mt-0.5 shrink-0 text-vermelho" />
              <div>
                <h3 className="font-display text-lg leading-none">{p.titulo}</h3>
                <p className="mt-1.5 text-sm">{p.texto}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Como foi construído */}
      <section className="mt-10 reticula rounded-md border-[3px] border-tinta bg-papel-3 p-5">
        <TituloDeSecao icone="etiqueta" texto="Como foi construído" />
        <p className="mt-2 text-base">
          O projeto seguiu <strong>Challenge Based Learning</strong> com{" "}
          <strong>Scrum adaptado</strong>, no tema Fake News e Desinformação. As cinco
          camadas do pipeline foram divididas entre as cinco pessoas do grupo, cada uma
          dona de uma parte do motor.
        </p>
      </section>

      {/* Equipe */}
      <section className="mt-10">
        <TituloDeSecao icone="assinatura" texto="Quem fez" />
        <ul className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
          {EQUIPE.map((pessoa) => (
            <li
              key={pessoa.nome}
              className="flex flex-col items-center gap-2 rounded-md border-[3px] border-tinta bg-papel-2 p-4 text-center shadow-bloco-sm"
            >
              <span className="flex size-14 items-center justify-center rounded-total border-[3px] border-tinta bg-vermelho font-display text-2xl text-white">
                {pessoa.nome.charAt(0)}
              </span>
              <span className="font-bold leading-tight">{pessoa.nome}</span>
              <span className="text-xs text-tinta-2">{pessoa.papel}</span>
            </li>
          ))}
        </ul>
      </section>

      <footer className="mt-10 border-t-[3px] border-tinta pt-4 text-center text-sm text-tinta-2">
        Senhora Vera · Residência em IA · Challenge 1 (Fake News e Desinformação) · Grupo 4
      </footer>
    </div>
  );
}
