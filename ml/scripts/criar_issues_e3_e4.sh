#!/bin/bash
REPO="Challenge-1-Grupo-04-Residencia/challenge_1_residencia_ia_grupo_4"

echo "Criando Épico E3: Pipeline em Camadas..."
E3_URL=$(./gh issue create --repo "$REPO" --title "[Épico E3] Pipeline em camadas" --body "Objetivo: Orquestrar N0 a N4 com regra de parada. (Tema T2)")
E3_NUM=${E3_URL##*/}

./gh issue create --repo "$REPO" --title "[US] Extração de metadados da notícia" --body "**História de Usuário**
Como motor de busca, preciso conseguir ler o conteúdo de um link enviado, para que a Vera possa avaliar notícias baseadas apenas na URL.

**Requisito Base:** RF-06
**Critérios de Aceitação:**
* **Dado que** o usuário envia um link ao invés de texto,
* **Quando** o sistema recebe a requisição,
* **Então** ele deve extrair o Título, Corpo do Texto, Autor e Data de Publicação.
* **E** deve limpar tags HTML antes de repassar ao orquestrador.
**Dependência:** Faz parte do Épico #$E3_NUM"

./gh issue create --repo "$REPO" --title "[US] Orquestração e Regra de Parada" --body "**História de Usuário**
Como gestor do sistema, quero que as notícias sejam processadas em camadas (N0 a N4) e parem assim que atingirem confiança suficiente, para economizar custos de API (LLM).

**Requisitos Base:** RF-07, RF-08
**Critérios de Aceitação:**
* **Dado que** o texto foi carregado no orquestrador,
* **Quando** a camada N1/N2 atingir uma Confiança >= C_min E a veracidade estiver fora da zona de dúvida (<= 25 ou >= 75),
* **Então** o sistema deve parar imediatamente o processamento e devolver o resultado, pulando as camadas seguintes.
**Dependência:** Faz parte do Épico #$E3_NUM"

./gh issue create --repo "$REPO" --title "[US] Score de Veracidade e Confiança" --body "**História de Usuário**
Como leitor, quero receber uma nota clara (0 a 100) e saber a confiança do sistema nessa nota, para decidir se acredito na checagem.

**Requisito Base:** RF-09
**Critérios de Aceitação:**
* **Dado que** as camadas analisaram a notícia,
* **Quando** devolverem seus sinais,
* **Então** o sistema deve aplicar a fórmula matemática de Veracidade.
* **E** calcular o peso dos sinais coletados contra o total de sinais possíveis para definir a Confiança.
**Dependência:** Faz parte do Épico #$E3_NUM"

echo "Criando Épico E4: Reputação de Fontes..."
E4_URL=$(./gh issue create --repo "$REPO" --title "[Épico E4] Reputação de fontes" --body "Objetivo: Saber quem é confiável. (Tema T2)")
E4_NUM=${E4_URL##*/}

./gh issue create --repo "$REPO" --title "[US] Consulta à reputação do veículo" --body "**História de Usuário**
Como leitor, quero saber se o site que estou lendo tem histórico de publicar fake news, para que eu possa duvidar de tudo que vem dali.

**Requisito Base:** RF-14, RF-18
**Critérios de Aceitação:**
* **Dado que** a notícia veio de uma URL (ex: meudominio.com),
* **Quando** bater na Camada N1,
* **Então** o sistema deve consultar a base interna para ver se há histórico de infrações desse domínio.
* **E** se houver histórico repetido de fakes, a credibilidade deve ser punida imediatamente.
**Dependência:** Faz parte do Épico #$E4_NUM"

./gh issue create --repo "$REPO" --title "[US] Checagem preemptiva (Fact Check API)" --body "**História de Usuário**
Como sistema, quero conferir se agências profissionais já desmentiram essa notícia recentemente, para poupar o trabalho de ter que deduzir isso do zero.

**Requisito Base:** RF-17
**Critérios de Aceitação:**
* **Dado que** a notícia entrou no pipeline,
* **Quando** consultada a Google Fact Check API,
* **Então** o sistema deve procurar aspas diretas ou similaridades em checagens recentes.
* **E** se achar um desmentido de agência IFCN, deve ativar a RN-01 (sobreposição) e devolver \"Falso\" imediatamente.
**Dependência:** Faz parte do Épico #$E4_NUM"

echo "Concluído! Issues criadas."
