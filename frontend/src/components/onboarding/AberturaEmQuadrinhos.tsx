"use client";

/**
 * A abertura: uma página de quadrinho com câmera que passeia pelos quadros.
 *
 * É a primeira coisa que a pessoa vê, e tem um trabalho específico: dizer, sem
 * manual, que a Vera é uma personagem e que ela **mostra o caminho** em vez de
 * cuspir um carimbo. Quem entende isso usa o produto como ele foi pensado; quem
 * não entende usa como mais um oráculo, que é o contrário do que a Vera serve
 * para fazer.
 *
 * ## Como a câmera funciona
 *
 * Os quadros ficam numa prancha de 1600×1000 em coordenadas próprias. A câmera é
 * uma transformação na prancha inteira:
 *
 *     translate(50vw, 50vh) rotate(R) scale(S) translate(-px, -py)
 *
 * lida da direita para a esquerda: leva o ponto (px, py) da prancha para a
 * origem, amplia, inclina e joga no centro da tela. `transform-origin: 0 0` é o
 * que faz essa conta fechar — com a origem no centro, cada passo precisaria
 * descontar metade da prancha.
 *
 * A escala não é fixa: ela sai do tamanho do quadro e do tamanho da janela, para
 * o mesmo passo enquadrar direito no celular de 360px e no monitor largo.
 *
 * ## Acessibilidade não é detalhe aqui
 *
 * Uma câmera que gira e dá zoom é exatamente o que derruba quem tem enxaqueca
 * vestibular. Com `prefers-reduced-motion` a abertura vira uma página parada, com
 * todos os quadros visíveis de uma vez e nenhum movimento — o conteúdo é o mesmo.
 * Sai por Esc, pelo botão de pular e sozinha no fim, e nunca aparece duas vezes.
 */

import Image from "next/image";
import { useCallback, useEffect, useRef, useState } from "react";

import { Icone, type NomeDoIcone } from "@/components/ui/Icone";
import { VeraIlustracao } from "@/components/vera/VeraIlustracao";
import { CASAS_DO_TERMOMETRO } from "@/lib/veracidade";

/** A prancha, em coordenadas próprias. Tudo aqui é desenhado nesta grade. */
const PRANCHA = { largura: 1560, altura: 1480 };

interface Quadro {
  /** Caixa do quadro na prancha. */
  x: number;
  y: number;
  largura: number;
  altura: number;
  /** Quanto tempo a câmera fica nele. */
  duracao: number;
}

/**
 * Quatro quadros do mesmo tamanho, numa grade de duas colunas.
 *
 * Eles já foram tortos, com tamanhos diferentes e inclinações para cada lado. O
 * efeito era de prancha bagunçada, não de quadrinho: o que dá o movimento aqui é
 * a câmera, que já gira e dá zoom. Com os quadros também tortos, a cena inteira
 * balança e fica difícil de ler.
 */
const QUADROS: Quadro[] = [
  { x: 40, y: 40, largura: 720, altura: 440, duracao: 2600 },
  { x: 800, y: 40, largura: 720, altura: 440, duracao: 2600 },
  { x: 40, y: 520, largura: 720, altura: 440, duracao: 2600 },
  { x: 800, y: 520, largura: 720, altura: 440, duracao: 3000 },
  { x: 40, y: 1000, largura: 1480, altura: 440, duracao: 3000 },
];

/** Sobra em volta do quadro ao enquadrar: sem ela a moldura encosta na tela. */
const RESPIRO = 0.88;

/** Altura reservada para o cartaz final, que fica por cima da prancha. */
const ALTURA_DO_CARTAZ = 140;

interface Props {
  /** Chamado quando a abertura termina ou é pulada. */
  aoTerminar: () => void;
  /** Mostra a abertura mesmo que ela já tenha sido vista (botão "ver de novo"). */
  forcar?: boolean;
}

export function AberturaEmQuadrinhos({ aoTerminar, forcar = false }: Props) {
  const [aberta, setAberta] = useState(false);
  const [passo, setPasso] = useState(0);
  const [semMovimento, setSemMovimento] = useState(false);
  const [janela, setJanela] = useState({ largura: 1280, altura: 800 });
  const relogio = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Decide na montagem, e não na renderização do servidor: `matchMedia` não
  // existe lá, e tentar adivinhar daria um salto de tela.
  //
  // A abertura roda **toda vez** que a página inicial é aberta. Já rodou só na
  // primeira visita, guardada no `localStorage`, e isso criou um problema de uso
  // difícil de adivinhar: quem já tinha visto nunca mais via, e a única volta
  // era um botão dentro do balão — se a pessoa não o acertasse, não havia jeito.
  // Para uma apresentação, ainda por cima, a abertura é o ponto. Quem não quer
  // vê-la fecha em um toque, e o toque fecha em qualquer lugar da tela.
  useEffect(() => {
    setSemMovimento(window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    setAberta(true);
  }, [forcar]);

  useEffect(() => {
    function medir() {
      setJanela({ largura: window.innerWidth, altura: window.innerHeight });
    }
    medir();
    window.addEventListener("resize", medir);
    return () => window.removeEventListener("resize", medir);
  }, []);

  const encerrar = useCallback(() => {
    setAberta(false);
    aoTerminar();
  }, [aoTerminar]);

  // O passo avança sozinho. O último não avança: ele é o cartaz final, e quem
  // decide quando sair dali é a pessoa.
  useEffect(() => {
    if (!aberta || semMovimento) return;
    if (passo >= QUADROS.length) return;

    relogio.current = setTimeout(
      () => setPasso((p) => p + 1),
      QUADROS[passo].duracao,
    );
    return () => {
      if (relogio.current) clearTimeout(relogio.current);
    };
  }, [aberta, passo, semMovimento]);

  useEffect(() => {
    if (!aberta) return;
    function tecla(e: KeyboardEvent) {
      if (e.key === "Escape") encerrar();
      if (e.key === "Enter" || e.key === " ") {
        setPasso((p) => Math.min(p + 1, QUADROS.length));
      }
    }
    document.addEventListener("keydown", tecla);
    // A página atrás não rola enquanto a abertura está na frente.
    const antes = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", tecla);
      document.body.style.overflow = antes;
    };
  }, [aberta, encerrar]);

  if (!aberta) return null;

  const fim = passo >= QUADROS.length;

  /** A transformação da câmera para o passo atual. */
  function camera(): string {
    if (semMovimento) {
      const escala =
        Math.min(
          janela.largura / PRANCHA.largura,
          janela.altura / PRANCHA.altura,
        ) * 0.9;
      return `translate(50vw, 50vh) scale(${escala}) translate(${-PRANCHA.largura / 2}px, ${-PRANCHA.altura / 2}px)`;
    }

    if (fim) {
      // O cartaz final ocupa a faixa de baixo da tela, então a prancha não tem
      // a altura inteira: ela tem o que sobra acima dele. Enquadrando pela
      // altura cheia, os dois quadros de baixo saíam cortados.
      const alturaUtil = janela.altura - ALTURA_DO_CARTAZ;
      const escala =
        Math.min(
          janela.largura / PRANCHA.largura,
          alturaUtil / PRANCHA.altura,
        ) * 0.94;
      return `translate(50vw, ${alturaUtil / 2}px) scale(${escala}) translate(${-PRANCHA.largura / 2}px, ${-PRANCHA.altura / 2}px)`;
    }

    const quadro = QUADROS[passo];
    const escala =
      Math.min(janela.largura / quadro.largura, janela.altura / quadro.altura) *
      RESPIRO;
    const centroX = quadro.x + quadro.largura / 2;
    const centroY = quadro.y + quadro.altura / 2;

    return `translate(50vw, 50vh) scale(${escala}) translate(${-centroX}px, ${-centroY}px)`;
  }

  return (
    <div
      className="fixed inset-0 z-50 overflow-hidden bg-papel"
      role="dialog"
      aria-modal="true"
      aria-label="A história da Senhora Vera"
      /* Toque em qualquer lugar avança, e no último quadro fecha.
         Antes, a única saída era um botão pequeno no canto de cima — e, no
         celular, quem não o acertava ficava preso: a abertura cobre a tela
         inteira, então "não dá para clicar em nada" era literalmente isso. */
      onClick={() => {
        if (fim) encerrar();
        else setPasso((p) => p + 1);
      }}
    >
      {/* Linhas de velocidade atrás de tudo: é o fundo de ação do quadrinho. O
          tamanho e a posição vêm da classe, que desenha um quadrado maior que a
          tela para que girar não deixe canto vazio. */}
      <div className="raios pointer-events-none" aria-hidden />

      {/* Duas camadas de movimento: a de fora enquadra (passo a passo), a de
          dentro deriva de leve o tempo todo. Juntas, a cena respira em vez de
          congelar entre um quadro e outro. */}
      <div
        className="absolute left-0 top-0"
        style={{
          width: PRANCHA.largura,
          height: PRANCHA.altura,
          transformOrigin: "0 0",
          transform: camera(),
          transition: semMovimento
            ? "none"
            : "transform 1200ms cubic-bezier(0.65, 0, 0.2, 1)",
        }}
      >
        {/* A deriva vai numa camada **de dentro**: `animation` e `style` disputam
            a mesma propriedade `transform`, e a animação ganha. No mesmo
            elemento, ela apagaria o enquadramento da câmera. */}
        <div
          className={semMovimento ? "" : "deriva"}
          style={{ width: "100%", height: "100%", transformOrigin: "50% 50%" }}
        >
            <QuadroDaProsa quadro={QUADROS[0]} visivel={semMovimento || passo >= 0} />
          <QuadroDaDesconfianca quadro={QUADROS[1]} visivel={semMovimento || passo >= 1} />
          <QuadroDaApuracao quadro={QUADROS[2]} visivel={semMovimento || passo >= 2} />
          <QuadroDaImagemFabricada quadro={QUADROS[3]} visivel={semMovimento || passo >= 3} />
          <QuadroDoCaminho quadro={QUADROS[4]} visivel={semMovimento || passo >= 4} />
        </div>
      </div>

      {/* O cartaz final fica fora da prancha: ele é da tela, não do desenho. */}
      {(fim || semMovimento) && (
        <div className="estufa absolute inset-x-0 bottom-0 flex flex-col items-center gap-1.5 bg-papel px-4 pb-4 pt-3 shadow-[0_-8px_24px_var(--papel)]">
          <p className="fonte-mao text-center text-xl text-tinta-2">
            Quem decide é você. Eu só mostro o caminho.
          </p>
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              encerrar();
            }}
            className="pressiona flex min-h-11 items-center gap-2 rounded-total border-[3px] border-tinta bg-vermelho px-7 py-3 font-display text-2xl text-white shadow-bloco"
          >
            Bora conferir!
            <Icone nome="seta" tamanho={22} />
          </button>
        </div>
      )}

      {/* O botão de pular fica **sempre** visível, inclusive no quadro final:
          ele é a saída garantida, e saída que some não é saída. */}
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          encerrar();
        }}
        className="pressiona absolute right-3 top-3 z-10 flex min-h-11 items-center gap-2 rounded-total border-[3px] border-tinta bg-papel-2 px-4 py-2 text-sm font-bold text-tinta shadow-bloco-sm"
      >
        Pular a história
      </button>

      {/* Quantos quadros faltam, no mesmo formato do placar da investigação. */}
      {!semMovimento && !fim && (
        <p
          className="fonte-mao absolute bottom-10 left-1/2 -translate-x-1/2 whitespace-nowrap text-base text-tinta-3"
          aria-hidden
        >
          toque para adiantar
        </p>
      )}

      {!semMovimento && (
        <div className="absolute bottom-4 left-1/2 flex -translate-x-1/2 gap-1.5" aria-hidden>
          {QUADROS.map((_, i) => (
            <span
              key={i}
              className={`size-3 rounded-sm border-2 border-tinta ${
                i <= passo ? "bg-vermelho" : "bg-papel-2"
              }`}
            />
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * Moldura de quadro: traço grosso, sombra dura e entrada com direção própria.
 *
 * A direção alternada não é enfeite. Com todos os quadros entrando do mesmo
 * jeito, a prancha vira uma lista aparecendo de cima para baixo; entrando cada
 * um de um lado, a página parece sendo desenhada. Quem já viu o quadro continua
 * vendo: nada desaparece quando a câmera segue adiante.
 */
function Moldura({
  quadro,
  visivel,
  entrada,
  className = "",
  children,
}: {
  quadro: Quadro;
  visivel: boolean;
  entrada: "esquerda" | "direita" | "baixo";
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <section
      className={`absolute overflow-hidden rounded-sm border-[6px] border-tinta bg-papel-2 shadow-[10px_10px_0_var(--tinta)] ${
        visivel ? `entra-${entrada}` : "opacity-0"
      } ${className}`}
      style={{
        left: quadro.x,
        top: quadro.y,
        width: quadro.largura,
        height: quadro.altura,
      }}
    >
      {children}
    </section>
  );
}

/**
 * Onomatopeia: a palavra desenhada que o quadrinho usa como som.
 *
 * Tem contorno preto porque precisa ser lida sobre qualquer fundo, e entra
 * estalando — é o acento rítmico da cena, o que faz a prancha parecer barulhenta
 * em vez de silenciosa.
 */
function Onomatopeia({
  texto,
  className = "",
  atraso = 300,
}: {
  texto: string;
  className?: string;
  atraso?: number;
}) {
  return (
    <span
      aria-hidden
      className={`estala letreiro pointer-events-none absolute font-display text-6xl text-ocre ${className}`}
      style={{ "--atraso": `${atraso}ms` } as React.CSSProperties}
    >
      {texto}
    </span>
  );
}

/** Balão de fala do quadro, com rabicho. */
function Fala({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <p
      className={`relative rounded-lg border-[5px] border-tinta bg-papel-2 px-5 py-3 font-display text-3xl leading-tight text-tinta ${className}`}
    >
      {children}
      <span
        aria-hidden
        className="absolute -bottom-[26px] left-10 h-0 w-0 border-x-[16px] border-t-[28px] border-x-transparent border-t-tinta"
      />
      <span
        aria-hidden
        className="absolute -bottom-[16px] left-[46px] h-0 w-0 border-x-[11px] border-t-[20px] border-x-transparent border-t-[var(--papel-2)]"
      />
    </p>
  );
}

/**
 * O molde de todo quadro: título, texto e, quando há, a arte na coluna da
 * direita.
 *
 * Existe para que os quatro tenham a **mesma** tipografia e o mesmo respiro.
 * Quando cada quadro escolhia o próprio tamanho de letra, a prancha parecia
 * quatro trabalhos diferentes colados juntos — e o texto encavalava na arte,
 * porque nada reservava o espaço dela.
 */
function QuadroPadrao({
  quadro,
  visivel,
  titulo,
  children,
  arte,
  fundo = "",
  entrada,
  extra,
}: {
  quadro: Quadro;
  visivel: boolean;
  titulo: string;
  children: React.ReactNode;
  arte?: React.ReactNode;
  fundo?: string;
  entrada: "esquerda" | "direita" | "baixo";
  extra?: React.ReactNode;
}) {
  return (
    <Moldura quadro={quadro} visivel={visivel} entrada={entrada} className={fundo}>
      {extra}
      <div className="reticula absolute inset-0 text-tinta" aria-hidden />
      <div className="relative flex h-full items-stretch">
        <div className="flex min-w-0 flex-1 flex-col justify-center gap-4 p-9">
          <h2 className="font-display text-5xl leading-none text-vermelho">{titulo}</h2>
          {children}
        </div>
        {/* A arte tem coluna própria: assim ela nunca passa por cima do texto,
            e o texto nunca invade a Vera. */}
        {arte && (
          <div className="relative flex w-[44%] shrink-0 items-end justify-center">
            {arte}
          </div>
        )}
      </div>
    </Moldura>
  );
}

/**
 * Quadro 1: a alegação chegando, numa tela de TV.
 *
 * A notícia é **fictícia de propósito**, e a emissora também. A história ganha
 * muito em ser concreta — "taxar o Pix em 15%" é o boato que de fato circulou
 * nos grupos de família, e é o exemplo que o produto usa na bateria de testes.
 * O que não pode é a abertura exibir uma manchete fabricada com o nome e a marca
 * de uma emissora de verdade, ou com a fala inventada de uma pessoa real: um
 * recorte dessa tela circulando é indistinguível da mentira que a Vera existe
 * para desmentir.
 */
function QuadroDaProsa({ quadro, visivel }: { quadro: Quadro; visivel: boolean }) {
  return (
    <Moldura quadro={quadro} visivel={visivel} entrada="esquerda" className="bg-ocre-suave">
      <div className="reticula absolute inset-0 text-tinta" aria-hidden />
      <Onomatopeia texto="TRIM!" className="right-6 top-4" atraso={450} />

      <div className="relative flex h-full items-center gap-6 p-8">
        <div className="min-w-0 flex-1">
          <h2 className="font-display text-5xl leading-none text-vermelho">
            Chegou mais uma!
          </h2>
          <p className="mt-3 text-[26px] leading-snug text-tinta-2">
            Caiu no grupo da família. E agora, é verdade ou é conversa fiada?
          </p>
        </div>

        {/* A telinha: faixa de plantão, manchete e rodapé, como toda notícia
            urgente que chega sem fonte. */}
        <div
          className="treme w-[46%] shrink-0 overflow-hidden rounded-md border-[5px] border-tinta bg-tinta shadow-[6px_6px_0_var(--tinta)]"
          style={{ "--atraso": "500ms" } as React.CSSProperties}
          aria-hidden
        >
          <div className="flex items-center gap-2 bg-vermelho px-3 py-1.5">
            <span className="size-3 rounded-total bg-papel-2" />
            <span className="font-display text-xl leading-none text-white">
              Ao vivo
            </span>
          </div>
          <p className="px-3 py-4 font-display text-3xl leading-tight text-papel-2">
            Governo vai taxar o Pix em 15%
          </p>
          <p className="bg-papel-3 px-3 py-1 text-sm font-bold text-tinta">
            Encaminhe para todos os grupos!
          </p>
        </div>
      </div>
    </Moldura>
  );
}

/**
 * Quadro 2: a Vera na calçada, desconfiando da alegação.
 *
 * Este é um dos dois quadros de cena cheia, e é de propósito: a arte vem com
 * rua, casa, planta e cadeira de plástico vermelha, que é o cenário onde essa
 * conversa acontece de verdade. Recortar a Vera dali jogaria fora justamente o
 * que diz de onde ela é.
 */
function QuadroDaDesconfianca({ quadro, visivel }: { quadro: Quadro; visivel: boolean }) {
  return (
    <Cena
      quadro={quadro}
      visivel={visivel}
      entrada="direita"
      src="/vera-cena-calcada.png"
      alt="Senhora Vera sentada numa cadeira de plástico na calçada, apontando e rindo de canto"
      posicao="object-[48%_20%]"
      onomatopeia="OXE!"
    >
      <Fala className="max-w-[440px]">Taxar o Pix? Isso tá com cara de pantim…</Fala>
    </Cena>
  );
}

/**
 * Quadro 3: a Vera sai para apurar.
 *
 * Aqui ela é recorte sobre papel, e não cena cheia: o quadro tem lista, e lista
 * precisa de fundo claro para ser lida. Dois quadros de cena seguidos também
 * deixavam a prancha pesada — alternar recorte e cena é o que dá ritmo.
 */
function QuadroDaApuracao({ quadro, visivel }: { quadro: Quadro; visivel: boolean }) {
  return (
    <QuadroPadrao
      quadro={quadro}
      visivel={visivel}
      titulo="Aí eu vou atrás!"
      entrada="baixo"
      arte={
        <VeraIlustracao
          pose="apontando"
          tamanho={320}
          ajusteLivre
          className="h-full w-auto max-w-full self-end object-contain"
        />
      }
    >
      <ul className="flex flex-col gap-2">
        {[
          { icone: "site", texto: "Quem publicou" },
          { icone: "jornal", texto: "Quem mais falou" },
          { icone: "lupa", texto: "O que as fontes dizem" },
        ].map((item) => (
          <li
            key={item.texto}
            className="flex w-fit items-center gap-2 rounded-md border-[4px] border-tinta bg-papel-3 px-3 py-1.5 text-[22px] font-bold"
          >
            <Icone nome={item.icone as NomeDoIcone} tamanho={26} />
            {item.texto}
          </li>
        ))}
      </ul>
    </QuadroPadrao>
  );
}

/**
 * Quadro 4: a imagem que chegou junto com a notícia, e que é fabricada.
 *
 * A peça é uma **simulação feita pela equipe** — não é um recorte de jornal, não
 * saiu no ar e ninguém disse aquilo. É esse o ponto do quadro: imagem de TV com
 * cara de plantão é uma das formas mais eficientes de mentira, porque a pessoa
 * confia no formato antes de ler o conteúdo.
 *
 * Duas decisões de segurança, e elas não são negociáveis:
 *
 * - **a marca da emissora real foi apagada do arquivo** (ver
 *   `frontend/scripts/`, e o arquivo em `public/noticia-simulada.png`). Simular
 *   uma emissora de verdade é se passar por ela, e isso é exatamente o que a
 *   Vera combate;
 * - **o carimbo "imagem fabricada" fica dentro do quadro**, grande e por cima.
 *   Assim, um recorte desta tela circulando leva o desmentido junto; sem ele,
 *   estaríamos produzindo mais uma peça de desinformação para explicar
 *   desinformação.
 */
function QuadroDaImagemFabricada({ quadro, visivel }: { quadro: Quadro; visivel: boolean }) {
  return (
    <Moldura quadro={quadro} visivel={visivel} entrada="direita">
      <Image
        src="/noticia-simulada.png"
        alt="Simulação de um telejornal, feita pela equipe da Vera para servir de exemplo de notícia fabricada"
        fill
        sizes="760px"
        className="object-cover object-[50%_28%]"
      />

      <div className="absolute inset-0 bg-tinta/35" aria-hidden />

      <span
        className="bate-carimbo absolute left-1/2 top-1/2 flex -translate-x-1/2 -translate-y-1/2 -rotate-[8deg] items-center gap-3 border-[6px] border-falsa bg-tinta/85 px-5 py-2 font-display text-5xl text-falsa"
        style={{ "--atraso": "700ms" } as React.CSSProperties}
        aria-hidden
      >
        <Icone nome="mentira" tamanho={44} />
        Imagem fabricada
      </span>

      <div className="absolute inset-x-6 bottom-6">
        <Fala className="max-w-[460px]">
          Essa imagem aí foi inventada. Ninguém sério publicou nada disso.
        </Fala>
      </div>
    </Moldura>
  );
}

/** Quadro 5: o veredito, do jeito que a Vera entrega. */
function QuadroDoCaminho({ quadro, visivel }: { quadro: Quadro; visivel: boolean }) {
  return (
    <Moldura quadro={quadro} visivel={visivel} entrada="esquerda" className="bg-papel-3">
      <div className="reticula absolute inset-0 text-tinta" aria-hidden />

      {/* Em duas colunas: o quadro é largo, e a coluna única deixava metade dele
          vazia. À esquerda o carimbo e a régua, à direita a explicação. */}
      <div className="relative flex h-full items-center gap-10 px-10">
        <div className="flex flex-col gap-3">
        <span
          className="bate-carimbo carimbo flex w-fit items-center gap-2 rounded-sm border-[5px] border-tinta bg-falsa px-4 py-1.5 font-display text-4xl text-white"
          style={{ "--atraso": "500ms" } as React.CSSProperties}
        >
          <Icone nome="mentira" tamanho={38} />
          Conversa fiada
        </span>

        <p className="text-sm font-bold uppercase tracking-wide text-tinta-2">
          Provavelmente falsa · 18%
        </p>

        {/* O termômetro da tela de resultado, igualzinho: a abertura mostra o
            que a pessoa vai ver depois, não uma ilustração do que seria. */}
        <div className="flex gap-2" aria-hidden>
          {CASAS_DO_TERMOMETRO.map((casa, i) => (
            <span
              key={casa.faixa}
              className={`h-5 flex-1 rounded-sm border-[3px] border-tinta ${
                i === 0 ? casa.cor : "bg-papel-2 opacity-45"
              }`}
            />
          ))}
        </div>

        </div>

        <p className="flex-1 text-[28px] leading-snug text-tinta-2">
          Nenhum jornal sério publicou isso, meu bem. E eu te mostro onde eu fui
          olhar.
        </p>
      </div>
    </Moldura>
  );
}

/**
 * Quadro de cena cheia: a arte sangra na moldura e o texto vem por cima.
 *
 * Um véu escuro sobe do pé do quadro só onde o texto fica, para o balão ter
 * contraste sem apagar o cenário.
 */
function Cena({
  quadro,
  visivel,
  entrada,
  src,
  alt,
  posicao,
  onomatopeia,
  children,
}: {
  quadro: Quadro;
  visivel: boolean;
  entrada: "esquerda" | "direita" | "baixo";
  src: string;
  alt: string;
  posicao: string;
  onomatopeia?: string;
  children: React.ReactNode;
}) {
  return (
    <Moldura quadro={quadro} visivel={visivel} entrada={entrada}>
      <Image src={src} alt={alt} fill sizes="760px" priority className={`object-cover ${posicao}`} />

      <div
        className="absolute inset-x-0 bottom-0 h-2/3 bg-gradient-to-t from-tinta/85 via-tinta/45 to-transparent"
        aria-hidden
      />

      {onomatopeia && <Onomatopeia texto={onomatopeia} className="left-6 top-5" atraso={400} />}

      <div className="absolute inset-x-6 bottom-6">{children}</div>
    </Moldura>
  );
}
