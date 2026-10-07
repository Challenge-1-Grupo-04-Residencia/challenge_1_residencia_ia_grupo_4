# Extensão da Senhora Vera

## Uso local

1. Inicie a API na porta `8010`, conforme as instruções de [`backend/README.md`](../backend/README.md).
2. No Chrome, abra `chrome://extensions`, ative o modo do desenvolvedor e escolha **Carregar sem compactação**, apontando para esta pasta.
3. Em uma página HTTP ou HTTPS, clique no ícone da extensão e depois em **Verificar esta página**. O widget flutuante é injetado nessa ação; nenhuma análise ou coleta acontece automaticamente.

A extensão envia para `POST /api/v1/checar` somente o texto extraído (limitado a 8.000 caracteres) e a URL higienizada. A chamada do widget passa pelo service worker da extensão para não depender do CORS do site visitado. A configuração atual é local (`http://127.0.0.1:8010`); não há domínio de produção confirmado.

## Permissões e privacidade

- `activeTab` e `scripting` permitem ler e injetar o script apenas na aba ativa após a ação do usuário.
- O acesso de host limita a comunicação à API local em `127.0.0.1:8010`.
- A extensão não acessa histórico, cookies ou abas em segundo plano, não lê campos de formulário e não persiste o conteúdo analisado.
- A explicação da Vera é exibida mesmo quando a API informa que não deve mostrar uma porcentagem.
