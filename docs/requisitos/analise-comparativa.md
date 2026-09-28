# Análise Comparativa (Benchmarking)

??? abstract "Histórico de revisão"

    | Data | Versão | Descrição | Autor |
    | :---: | :---: | --- | --- |
    | 21/09 | 1.0 | Criação da página de Análise Comparativa | Ian Costa |

Esta seção detalha a **Análise Comparativa (Benchmarking)**, uma técnica de elicitação e análise de requisitos utilizada para avaliar como o mercado resolve atualmente o problema da desinformação e identificar as oportunidades e diferenciais da **Senhora Vera**.

## 1. Critérios de Comparação

Os critérios abaixo foram extraídos dos requisitos funcionais (RF) e não funcionais do projeto:

- **Abordagem / Mecanismo:** A ferramenta utiliza apenas uma LLM passiva (onde o usuário faz uma pergunta e a IA tenta adivinhar com base no seu treinamento) ou utiliza uma abordagem híbrida de **ML Clássico + LLM**, como a arquitetura em camadas (N0-N4) da Vera, visando escalonar custos e otimizar a resolução?
- **Transparência / Explicabilidade:** O usuário recebe uma justificativa clara do porquê daquela checagem, visualizando o detalhamento dos sinais analisados (ex: idade do domínio, apelo emocional) ou recebe apenas um selo binário "Fake/Verdadeiro"? (Conforme RF-29 e RF-30).
- **Persona e Tom de Voz:** A ferramenta tem uma postura estritamente formal/institucional (padrão jornalístico frio) ou adota uma **identidade empática**, próxima ao usuário, reduzindo o atrito e acolhendo quem foi desinformado (a identidade da Vera)?
- **Multicanalidade:** A solução exige que o usuário interrompa sua jornada para entrar em um site específico ou se integra no **fluxo natural do usuário** (ex: Web, Extensão de navegador que atua sobre o que já está na tela e PWA para celular)? (Conforme RF-33 a RF-38).
- **Fonte vs. Conteúdo (Análise Conjunta):** A ferramenta analisa de forma separada a reputação do domínio (ex: histórico de fakes, WHOIS) ou foca apenas no texto? A Vera busca analisar o **conjunto da obra**: Fonte + Conteúdo (sensacionalismo, emoção, plágio, etc).

## 2. Seleção de Concorrentes

A análise foi conduzida avaliando três grandes grupos de soluções existentes:

1. **Agências Tradicionais de Fact-checking:** Aos Fatos (Fátima), Lupa, Fato ou Fake. (Focadas no Brasil e checagem manual/semi-automatizada via WhatsApp).
2. **Soluções Globais de Credibilidade:** NewsGuard (extensão que avalia domínios) e Notas da Comunidade do X/Twitter (crowdsourcing).
3. **IAs Generativas "Puras":** ChatGPT, Gemini, Claude (uso direto pelo usuário para checar uma notícia).

## 3. Matriz de Benchmarking

| Concorrente / Ferramenta | Abordagem / Mecanismo | Transparência / Explicabilidade | Persona e Tom de Voz | Multicanalidade | Fonte vs. Conteúdo |
| --- | --- | --- | --- | --- | --- |
| **Agências Tradicionais (Bots de WhatsApp)** | Manual (curadoria humana) ou busca no cache da agência. Lenta. | Moderada (enviam o link da matéria explicativa). | Formal/Jornalístico. Na maioria dos bots (ex: Fátima), o tom é apenas utilitário. | Forte no WhatsApp/Telegram. Baixa no navegador. | Avalia o **Fato** específico checado, não o conjunto. |
| **NewsGuard** | Humana/Algorítmica. | Alta para fontes (explicam o "Nutrition Label" do site). | Estritamente institucional e formal. | Apenas Extensão de navegador e licenciamento (B2B). | Foca quase exclusivamente na **Fonte** (reputação do domínio). |
| **Notas da Comunidade (X/Twitter)** | Humana (Crowdsourcing). Lenta, requer consenso político/social. | Alta (usuários inserem links de fontes). | Neutra/Variável (depende de quem escreve a nota). | Apenas dentro do próprio X/Twitter. | Foca no **Conteúdo/Contexto** da postagem. |
| **IAs Generativas "Puras"** | LLM Passiva. Muito cara, alto risco de alucinação e viés no treinamento. | Baixa/Média (gera um texto genérico sem auditar rigorosamente de onde extraiu o dado). | Neutra, programada para ser servil e fria. | Interface própria na Web/App, não se insere no contexto natural. | Foca apenas no **Conteúdo** fornecido no prompt. |
| **⭐ Senhora Vera (Nosso Produto)** | **ML Clássico + LLM (N0-N4)**. Custo escalonado e rápido. | **Altíssima**. Mostra a faixa, os sinais encontrados, o peso de cada um e a justificativa clara. | **Identidade empática ("Vó fofoqueira")**, carinhosa, que acolhe em vez de humilhar. | **Extensão (na tela)**, Web e PWA. Atua on-the-fly. | **Conjunto**: Analisa a Fonte (idade, reputação) e o Conteúdo (emoção, estilo, alegações). |

## 4. Análise de Diferenciais (Gaps e Oportunidades)

A partir da matriz, ficam claros os diferenciais que justificam os Requisitos definidos para a Vera:

1. **Eficiência Tecnológica:** Nenhuma ferramenta atual democratiza o uso de uma arquitetura N0-N4 focada no usuário final. O uso de ML Clássico antes de chamar uma LLM garante que a Vera seja muito mais rápida (latência < 2s para maioria dos casos) e barata do que usar o ChatGPT.
2. **Empatia como Ferramenta de Engajamento:** As soluções atuais têm tom professoral, o que pode causar o *efeito tiro pela culatra* (backfire effect) — afastar a pessoa desinformada. A persona da Vera ataca a notícia, não o usuário, o que é um diferencial gigantesco no letramento midiático.
3. **Visão Holística (Fonte + Conteúdo):** Soluções como NewsGuard falham ao olhar só a fonte (uma fonte boa pode errar; uma fonte nova pode acertar). A Vera usa as camadas para somar Fonte + Estilo de Escrita (Emoção) + Corroboração.
4. **Presença no Momento Crítico:** A exigência de multicanalidade (RF-33) com a extensão de navegador resolve o principal gap: a fricção. O usuário não precisa sair do site suspeito para consultar a Vera; a Vera já está lá com o selo e o contexto.
