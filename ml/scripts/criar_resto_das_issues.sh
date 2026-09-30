#!/bin/bash
REPO="Challenge-1-Grupo-04-Residencia/challenge_1_residencia_ia_grupo_4"

echo "Criando Épico E1: Chat com a Vera..."
E1_URL=$(./gh issue create --repo "$REPO" --title "[Épico E1] Chat com a Vera" --body "Objetivo: Conversar com a Vera para checar uma notícia. (Tema T1)")
E1_NUM=${E1_URL##*/}

./gh issue create --repo "$REPO" --title "[US] Entrada de dados para checagem" --body "**História de Usuário**
Como leitor, quero poder colar um link, um texto ou digitar uma afirmação, para que a Vera inicie a investigação.

**Requisito Base:** RF-01
**Critérios de Aceitação:**
* **Dado que** o usuário acessa o chat da Vera,
* **Quando** enviar um link, texto livre ou afirmação na caixa de mensagem,
* **Então** o sistema deve reconhecer o tipo de entrada e despachar para o Motor de Veracidade.
**Dependência:** Faz parte do Épico #$E1_NUM"

./gh issue create --repo "$REPO" --title "[US] Resposta em formato de chat" --body "**História de Usuário**
Como leitor, quero que o resultado da investigação seja explicado em formato de conversa, em linguagem simples e não técnica, para fácil entendimento.

**Requisito Base:** RF-02
**Critérios de Aceitação:**
* **Dado que** o Motor de Veracidade concluiu a checagem,
* **Quando** o resultado for devolvido para a interface,
* **Então** deve ser exibido como um balão de chat (persona da Vera).
* **E** o vocabulário não deve conter jargões técnicos de machine learning.
**Dependência:** Faz parte do Épico #$E1_NUM"

./gh issue create --repo "$REPO" --title "[US] Feedback de carregamento em etapas" --body "**História de Usuário**
Como leitor ansioso, quero ver o andamento da investigação enquanto espero, para saber que o sistema não travou.

**Requisito Base:** RF-03
**Critérios de Aceitação:**
* **Dado que** uma checagem profunda (ex: N3/N4) leva mais tempo,
* **Quando** o Motor estiver processando,
* **Então** a UI deve exibir indicadores visuais das camadas (ex: 'Lendo o site...', 'Buscando evidências...').
**Dependência:** Faz parte do Épico #$E1_NUM"

./gh issue create --repo "$REPO" --title "[US] Perguntas de acompanhamento" --body "**História de Usuário**
Como leitor crítico, quero poder fazer perguntas extras sobre o resultado que recebi, para aprofundar meu entendimento sobre o caso.

**Requisito Base:** RF-04
**Critérios de Aceitação:**
* **Dado que** o chat já exibiu o veredito final,
* **Quando** o usuário digitar uma nova pergunta no mesmo contexto,
* **Então** a Camada N4 (LLM) deve responder usando as evidências já recuperadas na N3 como contexto.
**Dependência:** Faz parte do Épico #$E1_NUM"

echo "Criando Épico E2: Persona e identidade visual..."
E2_URL=$(./gh issue create --repo "$REPO" --title "[Épico E2] Persona e identidade visual" --body "Objetivo: Vera tematizada, colorida e animada. (Tema T1)")
E2_NUM=${E2_URL##*/}

./gh issue create --repo "$REPO" --title "[US] Reação da Persona" --body "**História de Usuário**
Como usuário, quero que a expressão visual da Vera mude de acordo com a veracidade da notícia, para reforçar a mensagem.

**Requisito Base:** RF-05, RNF-20
**Critérios de Aceitação:**
* **Dado que** a notícia foi classificada como Falsa, Verdadeira ou Imprecisa,
* **Quando** o card for renderizado,
* **Então** o avatar ou as cores do layout devem refletir o resultado (ex: vermelho/brava para falso, verde/sorrindo para verdadeiro).
**Dependência:** Faz parte do Épico #$E2_NUM"

echo "Criando Épico E6: Corroboração..."
E6_URL=$(./gh issue create --repo "$REPO" --title "[Épico E6] Corroboração" --body "Objetivo: Saber se outros publicaram o mesmo e se sustentam os fatos. (Tema T2)")
E6_NUM=${E6_URL##*/}

./gh issue create --repo "$REPO" --title "[US] Busca de notícias semelhantes" --body "**História de Usuário**
Como Motor, preciso buscar matérias relacionadas em veículos confiáveis, para atestar se a informação está sendo corroborada.

**Requisito Base:** RF-27
**Critérios de Aceitação:**
* **Dado que** o fluxo atingiu a Camada N3,
* **Quando** o texto for avaliado,
* **Então** o sistema deve realizar busca por similaridade semântica (embeddings/TF-IDF) em bases/GDELT.
* **E** recuperar o top-5 de documentos relacionados.
**Dependência:** Faz parte do Épico #$E6_NUM"

./gh issue create --repo "$REPO" --title "[US] Inferência Lógica de Evidências (NLI)" --body "**História de Usuário**
Como gestor do sistema, quero que a LLM leia as evidências achadas e diga se elas sustentam ou contradizem a notícia original, para não depender de similaridade burra.

**Requisito Base:** RF-29, RF-30
**Critérios de Aceitação:**
* **Dado que** a Camada N3 recuperou as evidências,
* **Quando** a Camada N4 for ativada,
* **Então** a LLM deve classificar a relação entre a notícia e a evidência (Contradiz, Sustenta, Neutro).
* **E** gerar um resumo do motivo.
**Dependência:** Faz parte do Épico #$E6_NUM"

echo "Criando Épico E7: Explicabilidade..."
E7_URL=$(./gh issue create --repo "$REPO" --title "[Épico E7] Explicabilidade" --body "Objetivo: Mostrar o porquê do resultado. (Tema T1)")
E7_NUM=${E7_URL##*/}

./gh issue create --repo "$REPO" --title "[US] Detalhamento do Veredito" --body "**História de Usuário**
Como leitor, quero ver exatamente quais sinais (fontes, estilo, emoção) levaram àquela nota, para auditar a decisão da Vera.

**Requisito Base:** RF-32, RF-33
**Critérios de Aceitação:**
* **Dado que** o usuário expandiu a análise,
* **Quando** olhar os detalhes,
* **Então** a interface deve listar os fatores positivos e negativos separados, com suas respectivas fontes e pesos.
**Dependência:** Faz parte do Épico #$E7_NUM"

echo "Criando Épico E8: Extensão de navegador..."
E8_URL=$(./gh issue create --repo "$REPO" --title "[Épico E8] Extensão de navegador" --body "Objetivo: Vera dentro da página lida. (Tema T3)")
E8_NUM=${E8_URL##*/}

./gh issue create --repo "$REPO" --title "[US] Checagem de aba atual e selo de reputação" --body "**História de Usuário**
Como usuário de computador, quero um botão no meu navegador que avalie automaticamente a página que estou lendo no momento.

**Requisito Base:** RF-36, RF-37
**Critérios de Aceitação:**
* **Dado que** a extensão está instalada,
* **Quando** o usuário abrir uma matéria jornalística,
* **Então** o ícone da extensão deve mostrar a reputação do site (Verde/Amarelo/Vermelho).
* **E** permitir acionar a análise do texto completo com 1 clique.
**Dependência:** Faz parte do Épico #$E8_NUM"

echo "Criando Épico E9, E10 e E11..."
E9_URL=$(./gh issue create --repo "$REPO" --title "[Épico E9] Celular" --body "Objetivo: Vera no celular. (Tema T3)")
E9_NUM=${E9_URL##*/}
E10_URL=$(./gh issue create --repo "$REPO" --title "[Épico E10] Dados e avaliação" --body "Objetivo: Datasets, métricas e calibração. (Tema T4)")
E10_NUM=${E10_URL##*/}
E11_URL=$(./gh issue create --repo "$REPO" --title "[Épico E11] Histórico e últimas notícias" --body "Objetivo: Memória das checagens. (Tema T1)")
E11_NUM=${E11_URL##*/}

./gh issue create --repo "$REPO" --title "[US] Compartilhamento nativo no Celular (PWA)" --body "**História de Usuário**
Como usuário mobile, quero poder compartilhar uma notícia suspeita do WhatsApp direto para o app da Vera, para não ter que copiar e colar o texto.

**Requisito Base:** RF-40, RF-41
**Critérios de Aceitação:**
* **Dado que** o sistema é instalado via navegador (PWA),
* **Quando** o usuário clicar em 'Compartilhar' em outro app,
* **Então** a Vera deve aparecer na bandeja nativa do celular e receber o link.
**Dependência:** Faz parte do Épico #$E9_NUM"

./gh issue create --repo "$REPO" --title "[US] Pipeline de Treinamento e Calibração (ML)" --body "**História de Usuário**
Como Cientista de Dados, preciso manter os modelos e limiares calibrados contra os datasets de referência, para garantir F1-Macro >= 0.80.

**Requisito Base:** RNF-06, RNF-07
**Critérios de Aceitação:**
* **Dado que** a distribuição dos dados de desinformação muda,
* **Quando** os scripts de retreinamento rodarem na infraestrutura,
* **Então** devem gerar novos relatórios de métricas (Precision, Recall) e atualizar os artefatos (.joblib).
**Dependência:** Faz parte do Épico #$E10_NUM"

./gh issue create --repo "$REPO" --title "[US] Feed de últimas checagens" --body "**História de Usuário**
Como visitante do site principal, quero ver as mentiras que estão em alta e já foram desmentidas, para me informar de forma preventiva.

**Requisito Base:** RF-43
**Critérios de Aceitação:**
* **Dado que** entro na home page da Vera,
* **Quando** a página carregar,
* **Então** deve exibir uma lista com o histórico das notícias falsas mais checadas ou recentes pela comunidade.
**Dependência:** Faz parte do Épico #$E11_NUM"

echo "Concluído! Todos os Épicos restantes foram criados com suas USs principais."
