const API_URL = "http://127.0.0.1:8000/api/v1/checar";

const reputation = document.getElementById("reputation");
const ratingLabel = document.getElementById("rating-label");
const domainLabel = document.getElementById("domain");
const analyzeButton = document.getElementById("analyze-button");
const message = document.getElementById("message");
const result = document.getElementById("result");

let activeTab;

function showMessage(text) {
  message.textContent = text;
  message.hidden = !text;
}

function setRating(score) {
  let rating;
  let badgeColor;
  let badgeText;

  if (score >= 70) {
    rating = "verde";
    badgeColor = "#20834a"; // Verde
    badgeText = "OK";
  } else if (score >= 40) {
    rating = "amarelo";
    badgeColor = "#d39b00"; // Amarelo
    badgeText = "ATN";
  } else {
    rating = "vermelho";
    badgeColor = "#c53b36"; // Vermelho
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

async function analyzePage() {
  if (!activeTab?.id) {
    showMessage("Não foi possível identificar a aba atual.");
    return;
  }

  analyzeButton.disabled = true;
  analyzeButton.textContent = "Analisando…";
  showMessage("");
  result.classList.remove("visible");

  try {
    await chrome.scripting.executeScript({
      target: { tabId: activeTab.id },
      files: ["content.js"]
    });

    const page = await chrome.tabs.sendMessage(activeTab.id, { type: "VERA_GET_PAGE_TEXT" });
    if (!page?.text?.trim()) {
      throw new Error("Não foi encontrado texto para analisar nesta página.");
    }

    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto: page.text, url: page.url })
    });

    if (!response.ok) {
      throw new Error(`A API respondeu com erro (${response.status}).`);
    }

    const analysis = await response.json();
    if (typeof analysis.veracidade !== "number") {
      throw new Error("A resposta da API não contém uma pontuação válida.");
    }

    setRating(analysis.veracidade);
    result.textContent = analysis.explicacao || "Análise concluída.";
    result.classList.add("visible");
  } catch (error) {
    if (error instanceof TypeError && error.message.includes("fetch")) {
      showMessage("Não foi possível conectar à API. Verifique se o servidor está rodando no terminal (porta 8000).");
    } else {
      showMessage(error instanceof Error ? error.message : "Falha ao analisar a página.");
    }
  } finally {
    analyzeButton.disabled = false;
    analyzeButton.textContent = "Analisar texto completo";
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });

  try {
    const hostname = new URL(activeTab.url).hostname;
    domainLabel.textContent = hostname || "Página atual";
  } catch {
    domainLabel.textContent = "Página indisponível";
    analyzeButton.disabled = true;
    showMessage("Esta página não permite análise pela extensão.");
  }

  analyzeButton.addEventListener("click", analyzePage);
});