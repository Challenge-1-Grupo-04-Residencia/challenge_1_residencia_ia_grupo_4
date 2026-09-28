# Classificação e pesos

??? abstract "Histórico de revisão"

    | Data | Versão | Descrição | Autor |
    | :---: | :---: | --- | --- |
    | 16/09 | 1.0 | Criação da página | Maykon Soares |
    | 21/09 | 1.1 | Remoção das histórias de usuário e ajuste das referências | Ian Costa, Luísa Brambilla, Maykon Soares, Natália Evelin, Rebeca Bontempo |

!!! danger "Pesos iniciais, não definitivos"
    Os pesos desta página são uma **hipótese de partida** vinda do brainstorm. Eles serão
    calibrados com datasets rotulados (RNF-07).
    Toda mudança de peso deve ser registrada no [histórico de calibração](#historico-de-calibracao).

## O que é fake news para a Vera?

Para efeito do produto, a Vera classifica **alegações apresentadas como fato** conforme o
quanto são sustentadas por evidências e fontes confiáveis. Ela diferencia:

| Tipo | Definição | A Vera… |
| --- | --- | --- |
| **Fabricação** | Conteúdo inventado apresentado como notícia | Classifica |
| **Conteúdo manipulado** | Informação real alterada (números, citações, imagens) | Classifica |
| **Contexto falso** | Conteúdo real fora de contexto (data, lugar, pessoa) | Classifica |
| **Conteúdo enganoso** | Uso tendencioso de uma informação verdadeira | Classifica, com ressalva |
| **Sátira/paródia** | Humor sem intenção de enganar | Sinaliza como sátira |
| **Opinião** | Juízo de valor, não verificável | **Não** classifica: explica que é opinião |

!!! note "Base teórica a aprofundar"
    A tipologia acima se apoia na classificação de *information disorder* de Wardle &
    Derakhshan (2017), que deve entrar em [Referências](../referencias.md) na Investigate.

## Sinais e pesos

Os sinais estão divididos em três dimensões, que respondem às perguntas do brainstorm.
Cada sinal gera uma nota `s` entre **0** (indica falsidade) e **1** (indica veracidade).

### Dimensão 1 — Fonte · 35 pontos

*Quem publicou? Esse veículo teve outras notícias falsas recentemente?*

| ID | Sinal | Peso | Camada | Como pontuar (`s`) |
| --- | --- | --- | --- | --- |
| S-01 | Reputação do veículo na base curada | **12** | N1 | Confiável = 1 · Misto = 0,5 · Não confiável = 0 · Desconhecido = sem nota |
| S-02 | Histórico recente de fakes do domínio (12 meses) | **8** | N1 | 0 fakes = 1 · 1–2 = 0,5 · 3+ = 0 |
| S-03 | Idade do domínio (RDAP/WHOIS) | **6** | N1 | < 30 dias = 0 · 30 d–6 meses = 0,3 · 6 meses–2 anos = 0,6 · > 2 anos = 1 |
| S-04 | Transparência da página (autor, data, expediente, contato) | **5** | N1 | Proporção dos itens presentes |
| S-05 | Autor identificável (nome com histórico de publicações) | **4** | N1 | Identificável = 1 · Anônimo = 0 |

### Dimensão 2 — Conteúdo · 25 pontos

*Como está escrito? O que no texto entrega que algo é falso?*

| ID | Sinal | Peso | Camada | Como pontuar (`s`) |
| --- | --- | --- | --- | --- |
| S-06 | Classificador estilístico (TF-IDF + SVM/RL) | **10** | N2 | Probabilidade da classe "verdadeira" |
| S-07 | Sensacionalismo (CAIXA ALTA, "!!!", *clickbait*, urgência) | **5** | N2 | `1 − índice normalizado` |
| S-08 | Intensidade emocional (NRC: medo, raiva) | **5** | N2 | `1 − pico normalizado` |
| S-09 | Cita fontes verificáveis (links, estudos, órgãos oficiais) | **3** | N2 | Proporção de citações verificáveis |
| S-10 | Probabilidade de texto gerado por IA | **2** | N2 | `1 − probabilidade` |

!!! info "Por que S-10 pesa pouco?"
    Detectores de texto gerado por IA são pouco confiáveis e texto feito por IA não é
    falso por definição. O sinal entra como indício fraco.

### Dimensão 3 — Corroboração · 40 pontos

*A mesma notícia está em outros sites? As fontes usadas são corretas? É plágio?*

| ID | Sinal | Peso | Camada | Como pontuar (`s`) |
| --- | --- | --- | --- | --- |
| S-11 | Veículos confiáveis que publicaram o mesmo fato | **15** | N3 | 0 = 0 · 1 = 0,5 · 2 = 0,8 · 3+ = 1 |
| S-12 | NLI: evidências sustentam ou contradizem as alegações | **20** | N4 | `sustenta / (sustenta + contradiz)` |
| S-13 | Originalidade (é cópia alterada de outra fonte?) | **5** | N3 | Cópia com alteração de fatos = 0 · Original ou replicação fiel = 1 |

### Sinais só de contexto (peso 0)

O brainstorm levantou sinais que **não indicam falsidade por si só**. Eles aparecem na
explicação, mas **não entram no score**:

| Sinal | Por que não pontua |
| --- | --- |
| Viés político do veículo | Um veículo enviesado pode publicar fatos verdadeiros. Pontuar viés misturaria opinião com veracidade |
| Aceitação por grupo de usuários (idosos, jovens, ativistas) | Mede popularidade, não veracidade |
| Tempo que a postagem está no ar | Ajuda a detectar **notícia antiga recirculando** (contexto falso), mas não indica falsidade sozinho |
| Jornalista formado | Não há base pública confiável e a formação não garante veracidade |

!!! question "Em aberto para a Investigate"
    Fonte que é **artigo científico**: como avaliar revisão por pares, metodologia e base
    de publicação? Proposta: sinal extra S-14 (periódico indexado e revisado por pares),
    ativado só quando a fonte citada for um artigo.

## Regras que sobrepõem o score

| Regra | Efeito |
| --- | --- |
| **RN-01** Checagem de agência signatária da IFCN encontrada | O veredito da agência prevalece: falso → `V ≤ 10`, verdadeiro → `V ≥ 90`. A agência é citada |
| **RN-02** Domínio imita um veículo conhecido (ex.: `g1-noticias.com`) | `V ≤ 15` e alerta de site impostor |
| **RN-03** Conteúdo classificado como opinião ou sátira | Sem porcentagem: a Vera explica a natureza do conteúdo |
| **RN-04** Confiança `C < 0,5` ao final de todas as camadas | Resultado **Inconclusivo**, sem porcentagem definitiva |

A lista completa está em [Regras de negócio](../requisitos/regras-de-negocio.md).

## Fórmula

**Score de veracidade:** média ponderada **só dos sinais disponíveis**. Um sinal sem dado
não conta como zero.

$$
V = 100 \times \frac{\sum_{i \in D} w_i \, s_i}{\sum_{i \in D} w_i}
$$

**Confiança:** combina a cobertura (quanto do peso foi observado) e a concordância entre as
dimensões.

$$
C = \underbrace{\frac{\sum_{i \in D} w_i}{100}}_{\text{cobertura}} \times \underbrace{\left(1 - \sigma_{\text{dimensões}}\right)}_{\text{concordância}}
$$

Onde `D` é o conjunto de sinais disponíveis, `w` é o peso e `σ` é o desvio-padrão entre os
scores das três dimensões (0 a 1).

### Exemplo

> Link de `saudenatural-agora.com` dizendo que "vacina X causa Y".

| Sinal | Peso | `s` | `w × s` |
| --- | --- | --- | --- |
| S-01 Reputação: desconhecido | — | — | — |
| S-03 Domínio com 20 dias | 6 | 0 | 0 |
| S-04 Sem autor, sem expediente | 5 | 0,25 | 1,25 |
| S-05 Autor anônimo | 4 | 0 | 0 |
| S-06 Classificador: 0,15 | 10 | 0,15 | 1,5 |
| S-07 Muito sensacionalista | 5 | 0,1 | 0,5 |
| S-08 Pico de medo | 5 | 0,2 | 1 |
| **Total** | **35** | | **4,25** |

`V = 100 × 4,25 / 35 ≈ 12`. Cobertura de 35%, mas N1 e N2 concordam. A confiança ainda é
baixa, então a Vera sobe para **N3**: nenhum veículo confiável publicou (S-11 = 0). Ela
responde **"Provavelmente falsa"**, com a dificuldade **Mediano**.

## Faixas de veracidade

| Faixa | Rótulo | Cor | Humor da Vera |
| --- | --- | --- | --- |
| 0–20 | **Provavelmente falsa** | :material-square:{ style="color: #c62828" } Vermelho | Brava |
| 21–40 | **Duvidosa** | :material-square:{ style="color: #ef6c00" } Laranja | Desconfiada |
| 41–60 | **Inconclusiva** | :material-square:{ style="color: #f9a825" } Amarelo | Pensativa |
| 61–80 | **Provavelmente verdadeira** | :material-square:{ style="color: #7cb342" } Verde-claro | Satisfeita |
| 81–100 | **Confirmada por fontes** | :material-square:{ style="color: #2e7d32" } Verde | Orgulhosa |

## Histórico de calibração

| Data | Versão | Mudança | Evidência (dataset / métrica) |
| --- | --- | --- | --- |
| 16/09/2026 | v0.1 | Pesos iniciais do brainstorm | Nenhuma: hipótese |
