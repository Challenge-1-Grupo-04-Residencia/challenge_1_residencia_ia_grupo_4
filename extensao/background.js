const API_URL = "http://127.0.0.1:8010/api/v1/checar";
const LIMITE_TEXTO = 8000;
const TEMPO_LIMITE_MS = 120000;
const PARAMETROS_SENSIVEIS = new Set([
  "token",
  "auth",
  "session",
  "sessionid",
  "access_token",
  "authorization",
  "api_key",
  "key",
  "password",
  "pwd",
  "user_id",
  "email",
]);

function sanitizarUrl(valor) {
  try {
    const url = new URL(valor);
    if (url.protocol !== "http:" && url.protocol !== "https:") return null;

    url.hash = "";
    url.username = "";
    url.password = "";
    for (const parametro of new Set(url.searchParams.keys())) {
      const nome = parametro.toLowerCase();
      if (PARAMETROS_SENSIVEIS.has(nome) || nome.startsWith("utm_")) {
        url.searchParams.delete(parametro);
      }
    }
    return url.toString();
  } catch {
    return null;
  }
}

chrome.runtime.onMessage.addListener((mensagem, remetente, responder) => {
  if (mensagem?.type !== "VERA_ANALISAR_PAGINA") return false;

  const urlDaPagina = sanitizarUrl(remetente.url || remetente.tab?.url || "");
  const texto = mensagem.texto;
  if (
    !remetente.tab ||
    remetente.frameId !== 0 ||
    !urlDaPagina ||
    typeof texto !== "string" ||
    texto.trim().length < 50 ||
    texto.length > LIMITE_TEXTO
  ) {
    responder({ ok: false, erro: "REQUISICAO_INVALIDA" });
    return false;
  }

  fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texto, url: urlDaPagina }),
    signal: AbortSignal.timeout(TEMPO_LIMITE_MS),
  })
    .then(async (resposta) => {
      if (!resposta.ok) {
        responder({ ok: false, status: resposta.status });
        return;
      }

      try {
        responder({ ok: true, dados: await resposta.json() });
      } catch {
        responder({ ok: false, erro: "RESPOSTA_INVALIDA" });
      }
    })
    .catch((erro) => {
      responder({
        ok: false,
        erro:
          erro.name === "TimeoutError" || erro.name === "AbortError"
            ? "TEMPO_ESGOTADO"
            : "ERRO_REDE",
      });
    });

  return true;
});
