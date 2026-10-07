/**
 * Senhora Vera - Content Script (Manifest V3)
 *
 * PRIVACIDADE E SEGURANÇA (LGPD / Princípio do Menor Privilégio):
 * 1. Ação Explícita: Nenhuma coleta contínua ou automática é feita. A extração
 *    somente ocorre mediante clique deliberado do usuário ("Verificar esta página").
 * 2. Minimização de Dados: Coleta exclusivamente o texto jornalístico da matéria e a URL.
 *    Descarta rigorosamente campos de formulários, senhas, menus, rodapés, anúncios e cookies.
 * 3. Proteção contra Conteúdo Não Confiável (XSS): Todo o texto e retornos da API são tratados
 *    como dados não confiáveis, usando nós de texto (textContent) e Shadow DOM isolado.
 * 4. Logs Seguros: Não registra no console textos integrais da página nem dados sensíveis.
 */

if (!window.__veraContentScriptInstalled) {
  window.__veraContentScriptInstalled = true;

  // Configuração centralizada da extensão
  const VERA_CONFIG = {
    MAX_TEXT_LENGTH: 8000,
  };

  /**
   * Remove parâmetros sensíveis (tokens, sessões, senhas) e fragmentos da URL.
   */
  function sanitizarUrl(urlStr) {
    try {
      const parsed = new URL(urlStr);
      parsed.hash = "";
      parsed.username = "";
      parsed.password = "";
      const paramsSensíveis = new Set([
        "token", "auth", "session", "sessionid", "access_token",
        "authorization", "api_key", "key", "password", "pwd",
        "user_id", "email"
      ]);
      for (const param of new Set(parsed.searchParams.keys())) {
        const nome = param.toLowerCase();
        if (paramsSensíveis.has(nome) || nome.startsWith("utm_")) {
          parsed.searchParams.delete(param);
        }
      }
      return parsed.toString();
    } catch {
      return urlStr;
    }
  }

  /**
   * Extrai e minimiza o conteúdo textual relevante da notícia para análise.
   * Não altera o texto jornalístico, apenas elimina ruídos e elementos de interface.
   */
  function extrairConteudoNoticia() {
    // 1. Prioriza recipientes semânticos padrão de artigos e notícias
    const seletoresConteudo = [
      "article",
      '[itemprop="articleBody"]',
      "main",
      '[role="main"]',
      ".materia-conteudo",
      ".noticia-corpo",
      ".post-content",
      ".entry-content",
      ".article-content",
      ".news-content",
      ".conteudo-materia",
      "#conteudo-noticia"
    ];

    let container = null;
    for (const seletor of seletoresConteudo) {
      const elemento = document.querySelector(seletor);
      if (elemento && (elemento.innerText || elemento.textContent || "").trim().length > 100) {
        container = elemento;
        break;
      }
    }

    // Se nenhum container específico de notícia for detectado, usa o body como fallback
    if (!container) {
      container = document.body;
    }

    if (!container) {
      return "";
    }

    // 2. Clona o nó para higienização sem alterar a visualização original da página
    const clone = container.cloneNode(true);

    // 3. Remove rigorosamente elementos irrelevantes, de navegação e de dados sensíveis
    const seletoresRemover = [
      // Navegação, menus, rodapés e cabeçalhos
      "header", "nav", "footer", "aside", "menu", "dialog",
      // Scripts, estilos e mídia interativa
      "script", "style", "noscript", "svg", "canvas", "iframe",
      // Formulários e dados do usuário (LGPD: proteção contra captura de senhas e inputs)
      "form", "input", "textarea", "select", "button",
      '[type="password"]', '[type="hidden"]', "[contenteditable]", '[role="textbox"]',
      // Publicidade, cookies, comentários e compartilhamento
      '[role="banner"]', '[role="navigation"]', '[role="complementary"]', '[role="contentinfo"]',
      '[class*="ad-"]', '[class*="advertisement"]', '[id*="advertisement"]',
      '[class*="banner"]', '[id*="banner"]',
      '[class*="comment"]', '[id*="comment"]',
      '[class*="cookie"]', '[id*="cookie"]',
      '[class*="compartilhar"]', '[class*="share"]', '[class*="social"]',
      '[class*="newsletter"]', '[id*="newsletter"]',
      // Raiz do próprio widget flutuante da Senhora Vera
      "#vera-floating-root"
    ];

    seletoresRemover.forEach((seletor) => {
      clone.querySelectorAll(seletor).forEach((el) => el.remove());
    });

    // 4. Coleta o texto estruturado priorizando títulos e parágrafos
    let textoExtraido = "";
    const blocosTexto = clone.querySelectorAll("h1, h2, h3, p, blockquote");

    if (blocosTexto.length > 0) {
      const paragrafos = [];
      blocosTexto.forEach((bloco) => {
        const trecho = (bloco.textContent || "").trim();
        if (trecho.length > 0) {
          paragrafos.push(trecho);
        }
      });
      textoExtraido = paragrafos.join("\n\n");
    }

    // Fallback se não houver parágrafos explícitos
    if (!textoExtraido || textoExtraido.trim().length < 50) {
      textoExtraido = (clone.textContent || "").replace(/\s+/g, " ").trim();
    }

    // Normalização limpa de quebras de linha e espaçamentos repetidos
    textoExtraido = textoExtraido
      .replace(/[ \t]+/g, " ")
      .replace(/\n\s*\n\s*\n+/g, "\n\n")
      .trim();

    // 5. Minimização de volume: limita o tamanho para preservar desempenho e evitar vazamentos
    if (textoExtraido.length > VERA_CONFIG.MAX_TEXT_LENGTH) {
      const corte = textoExtraido.substring(0, VERA_CONFIG.MAX_TEXT_LENGTH);
      const ultimoPonto = Math.max(corte.lastIndexOf(". "), corte.lastIndexOf("\n"));
      if (ultimoPonto > VERA_CONFIG.MAX_TEXT_LENGTH * 0.7) {
        textoExtraido = corte.substring(0, ultimoPonto + 1);
      } else {
        textoExtraido = corte + "…";
      }
    }

    return textoExtraido;
  }

  // 1. Listener de comunicação com o popup tradicional da extensão
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type !== "VERA_GET_PAGE_TEXT") {
      return;
    }

    const textoMinimizado = extrairConteudoNoticia();
    sendResponse({
      title: document.title || "",
      url: sanitizarUrl(window.location.href),
      text: textoMinimizado
    });
  });

  // 2. Injeta o Widget Flutuante sob demanda com proteção Shadow DOM (RF-36, RF-37)
  function injectVeraWidget() {
    if (document.getElementById("vera-floating-root")) return;

    const root = document.createElement("div");
    root.id = "vera-floating-root";
    document.body.appendChild(root);

    const shadow = root.attachShadow({ mode: "open" });

    shadow.innerHTML = `
      <style>
        .vera-fab {
          position: fixed;
          bottom: 24px;
          right: 24px;
          z-index: 2147483647;
          display: flex;
          align-items: center;
          gap: 8px;
          background: #245e40;
          color: #ffffff;
          padding: 10px 18px;
          border-radius: 50px;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          box-shadow: 0 4px 18px rgba(0, 0, 0, 0.22);
          transition: transform 0.2s ease, background 0.2s ease;
          border: 2px solid #ffffff;
          user-select: none;
        }
        .vera-fab:hover {
          background: #194b32;
          transform: translateY(-2px) scale(1.03);
        }
        .vera-fab:active {
          transform: translateY(0) scale(0.98);
        }
        .vera-icon {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: #ffffff;
          color: #245e40;
          font-size: 11px;
          font-weight: 800;
        }
        .vera-card {
          display: none;
          position: fixed;
          bottom: 80px;
          right: 24px;
          width: 320px;
          max-height: 480px;
          overflow-y: auto;
          background: #ffffff;
          color: #202820;
          border-radius: 12px;
          box-shadow: 0 10px 35px rgba(0, 0, 0, 0.25);
          padding: 18px;
          z-index: 2147483647;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          border: 1px solid #dce2da;
          animation: veraFadeIn 0.2s ease;
        }
        .vera-card.active {
          display: block;
        }
        @keyframes veraFadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .vera-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 10px;
          border-bottom: 1px solid #edf0ec;
          padding-bottom: 8px;
        }
        .vera-title {
          font-size: 15px;
          font-weight: 700;
          margin: 0;
          color: #202820;
        }
        .vera-close {
          border: none;
          background: none;
          cursor: pointer;
          color: #89918a;
          font-size: 18px;
          padding: 0 4px;
          line-height: 1;
        }
        .vera-close:hover {
          color: #202820;
        }
        .vera-badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 6px 12px;
          border-radius: 6px;
          font-weight: 700;
          font-size: 13px;
          margin-bottom: 12px;
        }
        .badge-verde { background: #e6f5ec; color: #20834a; }
        .badge-amarelo { background: #fdf6e2; color: #b78100; }
        .badge-vermelho { background: #fdeeee; color: #c53b36; }
        .badge-loading { background: #f0f2ef; color: #59635b; }
        .badge-neutro { background: #edf0ec; color: #59635b; }
        .vera-text {
          font-size: 13px;
          line-height: 1.5;
          color: #404840;
          margin: 0 0 12px 0;
          white-space: pre-wrap;
        }
        .vera-privacy-box {
          font-size: 11px;
          line-height: 1.4;
          color: #59635b;
          background: #f7f9f7;
          border: 1px solid #e1e7e1;
          border-radius: 6px;
          padding: 8px 10px;
          margin-bottom: 12px;
        }
        .vera-footer {
          font-size: 11px;
          color: #89918a;
          text-align: right;
          margin: 0;
        }
      </style>

      <div class="vera-fab" id="vera-fab-btn" title="Verificar esta página com a Senhora Vera" role="button" tabindex="0">
        <span class="vera-icon" aria-hidden="true">V</span>
        <span>Verificar esta página</span>
      </div>

      <div class="vera-card" id="vera-popup-card" role="dialog" aria-modal="true" aria-label="Análise de Veracidade da Senhora Vera">
        <div class="vera-header">
          <h4 class="vera-title">Senhora Vera</h4>
          <button class="vera-close" id="vera-card-close" title="Fechar painel" aria-label="Fechar painel">✕</button>
        </div>
        <div class="vera-privacy-box">
          🔒 <strong>Privacidade:</strong> A checagem só ocorre mediante seu clique. Apenas o texto da matéria e a URL são enviados. Não coletamos senhas, formulários ou histórico.
        </div>
        <div id="vera-badge-container"></div>
        <p class="vera-text" id="vera-card-content">Pronto para checar a matéria.</p>
        <p class="vera-footer">Vera IA · Motor de Veracidade</p>
      </div>
    `;

    const fab = shadow.getElementById("vera-fab-btn");
    const card = shadow.getElementById("vera-popup-card");
    const closeBtn = shadow.getElementById("vera-card-close");
    const badgeContainer = shadow.getElementById("vera-badge-container");
    const content = shadow.getElementById("vera-card-content");

    let isAnalyzing = false;

    // Função segura para renderizar badges sem injeção de HTML
    function definirBadge(classe, texto) {
      badgeContainer.replaceChildren();
      const badge = document.createElement("span");
      badge.className = `vera-badge ${classe}`;
      badge.textContent = texto;
      badgeContainer.appendChild(badge);
    }

    fab.addEventListener("click", async () => {
      if (card.classList.contains("active")) {
        card.classList.remove("active");
        return;
      }

      card.classList.add("active");

      if (isAnalyzing) return;
      isAnalyzing = true;

      definirBadge("badge-loading", "⏳ Analisando matéria...");
      content.textContent = "A Senhora Vera está avaliando o texto da página...";

      try {
        const textoMinimizado = extrairConteudoNoticia();
        if (!textoMinimizado || textoMinimizado.length < 50) {
          throw new Error("CONTEUDO_INSUFICIENTE");
        }

        const resposta = await chrome.runtime.sendMessage({
          type: "VERA_ANALISAR_PAGINA",
          texto: textoMinimizado
        });
        if (!resposta?.ok) {
          if (resposta?.status) {
            throw new Error(`STATUS_${resposta.status}`);
          }
          throw new Error(resposta?.erro || "RESPOSTA_INVALIDA");
        }

        const data = resposta.dados;
        if (
          !data ||
          typeof data.explicacao !== "string" ||
          typeof data.exibe_porcentagem !== "boolean" ||
          (data.veracidade !== null && typeof data.veracidade !== "number")
        ) {
          throw new Error("RESPOSTA_INVALIDA");
        }

        if (data.exibe_porcentagem && typeof data.veracidade === "number") {
          const score = Math.round(data.veracidade);
          let badgeClass = "badge-vermelho";
          let ratingText = "Vermelho (Suspeito)";

          if (score >= 70) {
            badgeClass = "badge-verde";
            ratingText = "Verde (Confiável)";
          } else if (score >= 40) {
            badgeClass = "badge-amarelo";
            ratingText = "Amarelo (Atenção)";
          }

          definirBadge(badgeClass, `${ratingText} · ${score}/100`);
        } else {
          definirBadge("badge-neutro", "Sem porcentagem");
        }

        // Proteção contra XSS: sempre atribuir via textContent
        content.textContent = data.explicacao || "Análise concluída com sucesso.";
      } catch (err) {
        definirBadge("badge-neutro", "Aviso");

        if (err.message === "CONTEUDO_INSUFICIENTE") {
          content.textContent = "Não foi encontrado texto jornalístico suficiente nesta página para checagem.";
        } else if (err.message === "TEMPO_ESGOTADO") {
          content.textContent = "A checagem demorou mais que o esperado. Tente novamente daqui a pouco.";
        } else if (err.message === "ERRO_REDE") {
          content.textContent = "Não foi possível conectar à Senhora Vera. Verifique se o servidor está ativo (porta 8010).";
        } else if (err.message === "STATUS_503") {
          content.textContent = "A Senhora Vera não conseguiu concluir a checagem agora. Tente novamente daqui a pouco.";
        } else if (err.message === "RESPOSTA_INVALIDA") {
          content.textContent = "A resposta recebida não pôde ser exibida. Tente novamente daqui a pouco.";
        } else {
          content.textContent = "Não foi possível concluir a verificação da página no momento. Tente novamente.";
        }
      } finally {
        isAnalyzing = false;
      }
    });

    closeBtn.addEventListener("click", () => {
      card.classList.remove("active");
    });
  }

  // Injeta quando a estrutura do documento estiver pronta
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", injectVeraWidget);
  } else {
    injectVeraWidget();
  }
}