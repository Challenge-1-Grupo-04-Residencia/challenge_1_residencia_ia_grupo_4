/**
 * Senhora Vera - Popup Script (Manifest V3)
 *
 * PRIVACIDADE E SEGURANÇA (LGPD / Menor Privilégio):
 * 1. Ação Explícita: A checagem só é disparada mediante o clique do usuário em "Verificar esta página".
 * 2. Minimização de Dados: Coleta exclusivamente o texto jornalístico da matéria e a URL higienizada.
 * 3. A permissão 'activeTab' limita o acesso à aba atual após a ação do usuário.
 * 4. Proteção contra XSS: Todo o texto renderizado na tela utiliza 'textContent', impedindo injeção de HTML.
 * 5. Logs Seguros: Não imprime texto de matérias ou dados pessoais no console.
 */

// Configuração centralizada de endpoints e segurança
const VERA_CONFIG = {
  API_URL: "http://127.0.0.1:8010/api/v1/checar",
  REQUEST_TIMEOUT_MS: 120000,
};

const reputation = document.getElementById("reputation");
const ratingLabel = document.getElementById("rating-label");
const domainLabel = document.getElementById("domain");
const analyzeButton = document.getElementById("analyze-button");
const message = document.getElementById("message");
const result = document.getElementById("result");

let activeTab = null;

function showMessage(text) {
  message.textContent = text || "";
  message.hidden = !text;
}

function setRating(score) {
  let rating;
  let badgeColor;
  let badgeText;

  if (score >= 70) {
    rating = "verde";
    badgeColor = "#20834a"; // Confiável
    badgeText = "OK";
  } else if (score >= 40) {
    rating = "amarelo";
    badgeColor = "#d39b00"; // Atenção
    badgeText = "ATN";
  } else {
    rating = "vermelho";
    badgeColor = "#c53b36"; // Suspeito
    badgeText = "PER";
  }

  // 1. Atualiza o indicador dentro da janelinha do popup
  reputation.dataset.rating = rating;
  ratingLabel.textContent = `${rating[0].toUpperCase()}${rating.slice(1)} · ${Math.round(score)}/100`;

  // 2. Atualiza a cor e o selo no próprio ícone do navegador Chrome (RF-37)
  if (chrome.action?.setBadgeBackgroundColor && chrome.action?.setBadgeText) {
    chrome.action.setBadgeBackgroundColor({ color: badgeColor });
    chrome.action.setBadgeText({ text: badgeText });
  }
}

function clearRating() {
  reputation.dataset.rating = "";
  ratingLabel.textContent = "Sem porcentagem";

  if (chrome.action?.setBadgeText) {
    chrome.action.setBadgeText({ text: "" });
  }
}

async function analyzePage() {
  if (!activeTab?.id) {
    showMessage("Não foi possível identificar a aba ativa no momento.");
    return;
  }

  analyzeButton.disabled = true;
  analyzeButton.textContent = "Verificando matéria…";
  showMessage("");
  result.classList.remove("visible");

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), VERA_CONFIG.REQUEST_TIMEOUT_MS);

  try {
    // Solicita o texto extraído e higienizado da matéria
    const page = await chrome.tabs.sendMessage(activeTab.id, { type: "VERA_GET_PAGE_TEXT" });
    if (!page?.text || page.text.trim().length < 50) {
      throw new Error("CONTEUDO_INSUFICIENTE");
    }

    const response = await fetch(VERA_CONFIG.API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        texto: page.text,
        url: page.url
      }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`STATUS_${response.status}`);
    }

    const analysis = await response.json();
    if (
      !analysis ||
      typeof analysis.explicacao !== "string" ||
      typeof analysis.exibe_porcentagem !== "boolean" ||
      (analysis.veracidade !== null && typeof analysis.veracidade !== "number")
    ) {
      throw new Error("RESPOSTA_INVALIDA");
    }

    if (analysis.exibe_porcentagem && typeof analysis.veracidade === "number") {
      setRating(analysis.veracidade);
    } else {
      clearRating();
    }

    // Proteção XSS: inserção segura do texto de explicação
    result.textContent = analysis.explicacao || "Análise concluída com sucesso.";
    result.classList.add("visible");
  } catch (error) {
    clearTimeout(timeoutId);

    if (error.message === "CONTEUDO_INSUFICIENTE") {
      showMessage("Não foi encontrado conteúdo jornalístico suficiente nesta página para checagem.");
    } else if (error.name === "AbortError") {
      showMessage("O tempo de resposta da checagem expirou. Verifique sua conexão e tente novamente.");
    } else if (error instanceof TypeError && error.message.includes("fetch")) {
      showMessage("Não foi possível conectar à Senhora Vera. Verifique se o servidor está rodando no terminal (porta 8010).");
    } else if (error.message === "STATUS_503") {
      showMessage("A Senhora Vera não conseguiu concluir a checagem agora. Tente novamente daqui a pouco.");
    } else if (error.message === "RESPOSTA_INVALIDA") {
      showMessage("A resposta recebida não pôde ser exibida. Tente novamente daqui a pouco.");
    } else {
      showMessage("Não foi possível concluir a verificação da página no momento. Tente novamente.");
    }
  } finally {
    analyzeButton.disabled = false;
    analyzeButton.textContent = "Verificar esta página";
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    activeTab = tabs[0];

    if (!activeTab?.url) {
      domainLabel.textContent = "Página indisponível";
      analyzeButton.disabled = true;
      showMessage("Esta página não permite análise pela extensão.");
      return;
    }

    const urlObj = new URL(activeTab.url);
    if (!["http:", "https:"].includes(urlObj.protocol)) {
      domainLabel.textContent = "Página interna do navegador";
      analyzeButton.disabled = true;
      showMessage("Páginas especiais do navegador não podem ser analisadas.");
      return;
    }

    domainLabel.textContent = urlObj.hostname || "Página atual";
    analyzeButton.addEventListener("click", analyzePage);
  } catch {
    domainLabel.textContent = "Página indisponível";
    analyzeButton.disabled = true;
    showMessage("Não foi possível carregar as informações da página atual.");
  }
});