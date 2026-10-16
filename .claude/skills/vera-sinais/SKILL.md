---
name: vera-sinais
description: Use ao criar, alterar ou calibrar um sinal (S-01 a S-13) do motor de veracidade da Vera, ao mexer nas fórmulas de score ou confiança, ou ao implementar uma regra de negócio RN-xx. Gatilhos: "novo sinal", "peso do sinal", "calibrar", "score de veracidade", "confiança", "S-01".."S-13", "RN-01".."RN-12", "faixa de veracidade", "zona de dúvida", "regra de parada".
---

# Sinais e pontuação da Vera

O motor de veracidade não pontua por regra ad-hoc: ele **coleta sinais** e aplica uma
média ponderada. Toda camada que "sabe algo" sobre a notícia expressa esse saber como
sinal, nunca mexendo no score direto.

## A invariante central

**Um sinal sem dado é excluído do cálculo e nunca vale zero** (RN-06).

Essa é a regra que mais se quebra sem querer. "Não consegui medir a reputação do
veículo" e "o veículo tem péssima reputação" são coisas opostas; tratar as duas como
zero faz a Vera acusar de falsidade toda notícia sobre a qual ela não sabe nada.

Na prática: use `medir("S-XX", None, "por que não deu")`, nunca `medir("S-XX", 0.0)`
para representar ausência. O efeito correto de não saber é **derrubar a cobertura**, e
portanto a confiança — não o score.

## Onde as coisas vivem

| Arquivo | Responsabilidade |
| --- | --- |
| `backend/src/core/entities/signal.py` | Catálogo: IDs, nomes, pesos, dimensões |
| `backend/src/core/engine/scoring.py` | Fórmulas de `V` e `C`, faixas, regra de parada |
| `backend/src/core/engine/business_rules.py` | RN-01 a RN-04, que sobrepõem o score |
| `backend/tests/test_scoring.py` | Âncora das fórmulas, incl. o exemplo da documentação |

A fonte da verdade conceitual é `docs/produto/classificacao.md`, **na branch `docs`**.
Leia com `git show origin/docs:docs/produto/classificacao.md`.

## Criar um sinal novo

1. Defina-o primeiro em `docs/produto/classificacao.md` (branch `docs`): ID, nome, peso,
   dimensão, camada e como pontuar. Sem isso o sinal não tem critério de aceite.
2. Acrescente a `DefinicaoSinal` em `signal.py` e inclua-a em `CATALOGO`.
3. **Rebalanceie os pesos da dimensão.** `PESO_TOTAL` precisa continuar 100 — o teste
   `test_peso_total_do_catalogo_fecha_em_cem` falha se não fechar, porque a cobertura
   deixaria de ser uma fração interpretável.
4. Meça o sinal na camada correspondente, via `resultado.registrar(medir(...))`.
5. Escreva o teste do sinal na camada e atualize o histórico de calibração na doc.

## Alterar um peso

Mudar peso muda todo resultado já publicado. O processo é:

1. Ter a evidência: métrica sobre dataset rotulado (RNF-07), não intuição.
2. Alterar o peso em `signal.py` **e** na tabela da documentação.
3. Rodar `uv run pytest backend/tests/test_scoring.py` — o teste
   `test_exemplo_da_documentacao` vai quebrar se a doc e o código divergirem. Isso é
   proposital: ele existe para forçar os dois a andarem juntos.
4. Registrar linha nova no **histórico de calibração** de `classificacao.md`, com data,
   versão, mudança e a evidência que a justificou.

## As fórmulas

```
V = 100 × Σ(w·s) / Σ(w)        sobre os sinais DISPONÍVEIS
C = cobertura × concordância
    cobertura    = Σ(w disponível) / 100
    concordância = 1 − σ(scores por dimensão)
```

`V` devolve `None` quando nada foi medido. Não substitua por 50: "não sei" não é "está
na dúvida", e 50 cairia na faixa Inconclusiva dando a impressão de que houve análise.

## Regras de negócio

RN-01 a RN-04 se aplicam **depois** do cálculo, em `business_rules.aplicar`, na ordem:

1. **RN-03** (opinião/sátira) — não recebe porcentagem, vence tudo: não é alegação de fato.
2. **RN-01** (agência IFCN) — o veredito humano publicado prevalece sobre o score.
3. **RN-02** (domínio impostor) — teto de 15. É teto, não atribuição: não levanta score baixo.
4. **RN-04** (confiança < 0,5 no fim) — Inconclusivo.

Ao adicionar uma regra, insira-a na ordem certa e escreva o teste de precedência contra
as regras vizinhas — a ordem é a parte que silenciosamente dá errado.

## Antes de dar por pronto

- [ ] `uv run pytest` passa
- [ ] `PESO_TOTAL` continua 100
- [ ] Nenhum caminho usa `0.0` para representar ausência de dado
- [ ] A doc em `origin/docs` foi atualizada, com linha no histórico de revisão
- [ ] O sinal aparece no detalhamento da API (RF-33) com justificativa legível
