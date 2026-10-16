# Extensão da Senhora Vera

## Uso local

1. Inicie a API na porta `8010`, conforme as instruções de [`backend/README.md`](../backend/README.md).
2. No Chrome, abra `chrome://extensions`, ative o modo do desenvolvedor e escolha **Carregar sem compactação**, apontando para esta pasta.
3. Em páginas HTTP ou HTTPS, o widget flutuante aparece automaticamente. Para analisar, clique no widget ou abra o popup da extensão e escolha **Verificar esta página**.

O carregamento da página injeta o script necessário para desenhar o widget, mas não lê título, texto ou URL, não chama a API e não persiste dados. Somente depois de um clique deliberado a extensão procura um contêiner semântico de artigo ou um seletor editorial conhecido e extrai o conteúdo principal visível, limitado a 8.000 caracteres. Não usa `main` genérico nem o `body` como fallback: se não reconhecer um contêiner de notícia, não envia conteúdo. A API `POST /api/v1/checar` recebe o texto e a URL higienizada. A chamada do widget passa pelo service worker da extensão para não depender do CORS do site visitado. A configuração atual é local (`http://127.0.0.1:8010`); não há domínio de produção confirmado.

## Permissões e privacidade

- `activeTab` dá ao popup acesso à aba atual depois da ação do usuário.
- Os padrões `http://*/*` e `https://*/*` em `content_scripts.matches` são necessários para mostrar o widget automaticamente em qualquer página web. O Chrome pode apresentar isso como acesso a todos os sites; o script não analisa conteúdo sem clique.
- O acesso de host limita a comunicação à API local em `127.0.0.1:8010`.
- A extensão não acessa histórico, cookies ou abas em segundo plano, não lê campos de formulário e não persiste o conteúdo analisado.
- A explicação da Vera é exibida mesmo quando a API informa que não deve mostrar uma porcentagem.
