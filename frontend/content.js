if (!window.__veraContentScriptInstalled) {
  window.__veraContentScriptInstalled = true;

  // 1. Mantém suporte ao popup tradicional do Chrome
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type !== "VERA_GET_PAGE_TEXT") {
      return;
    }

    sendResponse({
      title: document.title,
      url: window.location.href,
      text: document.body?.innerText ?? ""
    });
  });

  // 2. Injeta o Botão Flutuante (estilo Grammarly) direto na página
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
          margin-bottom: 12px;
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
        .vera-text {
          font-size: 13px;
          line-height: 1.5;
          color: #404840;
          margin: 0 0 12px 0;
          white-space: pre-wrap;
        }
        .vera-footer {
          font-size: 11px;
          color: #89918a;
          text-align: right;
          margin: 0;
        }
      </style>

      <div class="vera-fab" id="vera-fab-btn" title="Checar veracidade com a Senhora Vera">
        <span class="vera-icon">V</span>
        <span>Checar com a Vera</span>
      </div>

      <div class="vera-card" id="vera-popup-card">
        <div class="vera-header">
          <h4 class="vera-title">Senhora Vera</h4>
          <button class="vera-close" id="vera-card-close" title="Fechar">✕</button>
        </div>
        <div id="vera-badge-container"></div>
        <p class="vera-text" id="vera-card-content">Carregando...</p>
        <p class="vera-footer">Vera IA · Motor de Veracidade</p>
      </div>
    `;

    const fab = shadow.getElementById("vera-fab-btn");
    const card = shadow.getElementById("vera-popup-card");
    const closeBtn = shadow.getElementById("vera-card-close");
    const badgeContainer = shadow.getElementById("vera-badge-container");
    const content = shadow.getElementById("vera-card-content");

    let isAnalyzing = false;

    fab.addEventListener("click", async () => {
      if (card.classList.contains("active")) {
        card.classList.remove("active");
        return;
      }

      card.classList.add("active");

      if (isAnalyzing) return;
      isAnalyzing = true;

      badgeContainer.innerHTML = '<span class="vera-badge badge-loading">⏳ Analisando matéria...</span>';
      content.textContent = "A Senhora Vera está avaliando o texto e a reputação desta página...";

      try {
        const pageText = document.body?.innerText ?? "";
        if (!pageText.trim()) {
          throw new Error("Não foi encontrado texto suficiente nesta página para análise.");
        }

        const response = await fetch("http://127.0.0.1:8000/api/v1/checar", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            texto: pageText,
            url: window.location.href
          })
        });

        if (!response.ok) {
          throw new Error(`Erro na API (${response.status})`);
        }

        const data = await response.json();
        const score = Math.round(data.veracidade ?? 50);

        let badgeClass = "badge-vermelho";
        let ratingText = "Vermelho (Suspeito)";

        if (score >= 70) {
          badgeClass = "badge-verde";
          ratingText = "Verde (Confiável)";
        } else if (score >= 40) {
          badgeClass = "badge-amarelo";
          ratingText = "Amarelo (Atenção)";
        }

        badgeContainer.innerHTML = `<span class="vera-badge ${badgeClass}">${ratingText} · ${score}/100</span>`;
        content.textContent = data.explicacao || "Análise concluída com sucesso.";
      } catch (err) {
        badgeContainer.innerHTML = '<span class="vera-badge badge-vermelho">Falha na análise</span>';
        if (err instanceof TypeError && err.message.includes("fetch")) {
          content.textContent = "Não foi possível conectar à API. Verifique se o servidor FastAPI está ligado no terminal (porta 8000).";
        } else {
          content.textContent = err.message || "Erro desconhecido ao processar a página.";
        }
      } finally {
        isAnalyzing = false;
      }
    });

    closeBtn.addEventListener("click", () => {
      card.classList.remove("active");
    });
  }

  // Injeta quando o DOM estiver pronto
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", injectVeraWidget);
  } else {
    injectVeraWidget();
  }
}