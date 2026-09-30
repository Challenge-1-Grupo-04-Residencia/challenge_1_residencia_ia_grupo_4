# ml — dados, análise exploratória e treino

O lado de ciência de dados do projeto: os corpora brasileiros de fake news, as EDAs que
respondem às Guiding Questions da fase Investigate e o treino dos modelos que o
`backend/` consome em produção.

```
ml/
├── notebooks/   uma EDA por camada do pipeline
├── scripts/     download e padronização dos datasets
└── datasets/    corpora padronizados (fora do controle de versão)
```

## Primeiros passos

```bash
uv sync
./ml/scripts/baixar_datasets.sh      # rodar da raiz do repositório, só na 1ª vez
uv run jupyter lab
```

No VS Code, abra o notebook em `ml/notebooks/` e selecione o kernel Python de `.venv`.

Opções úteis do script:

```bash
./ml/scripts/baixar_datasets.sh --docs           # só refaz padronização e documentação
./ml/scripts/baixar_datasets.sh --so fake-br     # apenas um dataset
./ml/scripts/baixar_datasets.sh --completo       # inclui downloads pesados (FKTC, 460 MB)
```

## Os caminhos são relativos a `ml/`

Os notebooks leem `../datasets/<slug>/padronizado.parquet`, e o script resolve o destino
a partir da própria localização (`Path(__file__).parent.parent`). Por isso os três
diretórios se movem **juntos**: separar `datasets/` de `notebooks/` quebra todos os
caminhos de uma vez.

`datasets/` está no `.gitignore` — os corpora somam vários GB e são reproduzíveis pelo
script. Quem já tinha a pasta na raiz do repositório antes desta reorganização precisa
movê-la uma vez:

```bash
mv datasets ml/datasets
```

## Os notebooks

| Notebook | Camada | Pergunta |
| --- | --- | --- |
| `01_eda_n0_cache_checagens` | N0 | Vale a pena cachear? Quanta redundância existe nos desmentidos? |
| `02_eda_n1_fontes_reputacao` | N1 | É possível montar uma base de reputação a partir dos datasets? |
| `03_eda_n2_estilo_e_sensacionalismo` | N2 | O estilo de escrita separa verdadeiro de falso? |
| `04_eda_n2_redes_e_whatsapp` | N2 | Texto de mensageiro e de rede social se comportam igual? |
| `05_eda_n3_n4_corroboracao_e_ia` | N3/N4 | Qual limiar de similaridade separa corroboração de ruído? |

## Toda descoberta vai para a documentação

O registro das descobertas fica em `docs/investigacao.md`, **na branch `docs`** — é o que
liga uma métrica a uma decisão de arquitetura, e o que impede um número de virar
constante mágica no código.

O formato é: data, quem, descoberta e **impacto** (que peso, regra ou requisito ela
muda). Um exemplo já em uso: a EDA de 28/09 mediu que o limiar de similaridade de 0,10
dá 79,4% de recall com 0,6% de falsos positivos, e é isso que justifica o valor em
`backend/src/infrastructure/search/tfidf_search.py`.

```bash
git show origin/docs:docs/investigacao.md
```

## Do notebook para produção

Modelo treinado no notebook vira artefato em
`backend/src/infrastructure/ml_models/`, carregado pela camada correspondente. O
notebook **não** é executado em produção: ele produz o `.joblib` e registra a métrica
que justifica o modelo escolhido.

Antes de trocar um modelo, confira o RNF de desempenho aplicável (a N2 tem meta de
F1-Macro ≥ 0,80) e registre a comparação em `investigacao.md`.
