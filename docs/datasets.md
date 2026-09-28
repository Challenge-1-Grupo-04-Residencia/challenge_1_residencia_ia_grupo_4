# Datasets

??? abstract "Histórico de revisão"

    | Data | Versão | Descrição | Autor |
    | :---: | :---: | --- | --- |
    | 21/09 | 1.0 | Levantamento, download e verificação das bases em PT-BR | Ian Costa, Luísa Brambilla, Maykon Soares, Natália Evelin, Rebeca Bontempo |
    | 21/09 | 1.1 | Padronização: esquema único de colunas, dicionário e ficha por dataset | Ian Costa, Luísa Brambilla, Maykon Soares, Natália Evelin, Rebeca Bontempo |

Todas as bases desta página são **em português do Brasil** e foram **baixadas e conferidas**:
os números abaixo são a contagem real dos arquivos, não o que o artigo original anuncia.

## Organização padronizada

Um comando baixa tudo, normaliza e gera a documentação de cada base:

```bash
./scripts/baixar_datasets.sh              # baixa o que falta, padroniza e documenta
./scripts/baixar_datasets.sh --docs       # só refaz a padronização e a documentação
./scripts/baixar_datasets.sh --so fake-br # apenas um dataset
./scripts/baixar_datasets.sh --completo   # inclui o download pesado do FKTC (460 MB)
```

Toda base recebe **a mesma estrutura de pasta**, para que importar uma ou todas dê o mesmo
trabalho:

```
datasets/<slug>/
├── dados/               arquivos originais, como vieram da fonte
├── padronizado.parquet  mesmas colunas em todos os datasets
├── metadata.json        ficha legível por código (fonte, licença, contagens)
├── README.md            o que é, de onde veio e como usar no projeto
└── dicionario.md        colunas, tipos e exemplos, gerados dos dados reais
```

Como o esquema é igual em todas, **importar o conjunto inteiro é uma linha**:

```python
import pandas as pd, glob
df = pd.concat(map(pd.read_parquet, glob.glob("datasets/*/padronizado.parquet")))
# 346.813 linhas, 10 colunas
```

### Esquema comum

| Coluna | Descrição |
| --- | --- |
| `id` | `<slug>:<n>`, único entre todos os datasets |
| `dataset` | slug de origem, para filtrar ou remover uma base |
| `canal` | `noticia`, `rede_social`, `whatsapp`, `checagem` ou `sintetico` |
| `titulo` | título, quando a fonte tem |
| `texto` | corpo do conteúdo |
| `rotulo` | `falso`, `verdadeiro` ou `outro` |
| `rotulo_original` | rótulo como veio da fonte, sem tradução, para auditar a conversão |
| `data` | data de publicação, quando existir |
| `veiculo` | veículo ou fonte declarada |
| `url` | link de origem |

O `rotulo_original` existe porque agências usam escalas diferentes: o que é "Enganoso" ou
"FORA DE CONTEXTO" vira `outro`, e o valor de origem fica registrado para revisão.

### O que há hoje

| Dataset | Slug | Canal | Linhas | falso | verdadeiro | outro |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Fake.Br Corpus | `fake-br` | notícia | 7.200 | 3.600 | 3.600 | 0 |
| FakeRecogna | `fakerecogna` | notícia | 11.902 | 5.951 | 5.951 | 0 |
| FakeTrue.Br | `faketrue-br` | notícia | 3.582 | 1.791 | 1.791 | 0 |
| FakenewsBR v6 | `fakenewsbr-v6` | notícia | 297.672 | 66.772 | 230.900 | 0 |
| FakeWhatsApp.Br | `fakewhatsapp-br` | WhatsApp | 9.824 | 4.214 | 5.610 | 0 |
| MuMiN-PT e COVID19.BR | `portuguese-fact-checking` | rede social | 3.391 | 2.207 | 1.184 | 0 |
| Central de Fatos | `central-de-fatos` | checagem | 11.643 | 10.196 | 250 | 1.197 |
| FACTCK.BR | `factck-br` | checagem | 1.300 | 933 | 123 | 244 |
| FakeTweet.Br | `faketweet-br` | rede social | 279 | 188 | 91 | 0 |
| FakeGen.BR | `fakegen-br` | sintético | 20 | 20 | 0 | 0 |
| FKTC | `fktc` | notícia | sob demanda | | | |

**346.813 linhas padronizadas.** A pasta `datasets/` tem cerca de 1,3 GB e fica **fora do
controle de versão**: nenhum dado é commitado.

## Corpora rotulados: treinar e avaliar o classificador

Servem à camada **N2 · Conteúdo** ([RF-21](requisitos/funcionais.md) a
[RF-26](requisitos/funcionais.md)) e ao conjunto de avaliação exigido pelo
[RNF-06](requisitos/nao-funcionais.md).

| Dataset | Tamanho conferido | Conteúdo | Licença | Link |
| --- | --- | --- | --- | --- |
| **Fake.Br Corpus** | 3.600 falsas + 3.600 verdadeiras | Texto integral, versão pré-processada e normalizada por tamanho, com metadados | Acadêmica, citar o artigo | [github.com/roneysco/Fake.br-Corpus](https://github.com/roneysco/Fake.br-Corpus) |
| **FakeRecogna** | 11.902 registros (5.951 de cada) | Título, subtítulo, texto, **categoria**, data, autor, URL e classe | MIT | [huggingface.co/datasets/recogna-nlp/FakeRecogna](https://huggingface.co/datasets/recogna-nlp/FakeRecogna) |
| **FakeTrue.Br** | 1.791 pares | Cada notícia falsa **pareada com a verdadeira** sobre o mesmo fato, com os dois links | Acadêmica | [github.com/jpchav98/FakeTrue.Br](https://github.com/jpchav98/FakeTrue.Br) |
| **FKTC** | 2.168 notícias | Política, eleições de 2018 e 2019, de Aos Fatos, Lupa e UOL Confere. Os dados não estão no repositório: vêm de um zip de 460 MB no Zenodo, baixado só com `--completo` | Acadêmica | [github.com/GoloMarcos/FKTC](https://github.com/GoloMarcos/FKTC) |
| **Fake.Br no Hugging Face** | o mesmo Fake.Br | Carregamento direto pela biblioteca `datasets` | Acadêmica | [huggingface.co/datasets/fake-news-UFG/fakebr](https://huggingface.co/datasets/fake-news-UFG/fakebr) |
| **FakeGen.BR** (Expanded Fake News Corpus) | 20 itens | **Não é corpus coletado**: são notícias geradas por LLM a partir do Fake.Br. Serve de material para o RF-25 (texto gerado por IA), não para treino | Verificar no repositório | [github.com/Pedrest15/expanded_fake_news_corpus](https://github.com/Pedrest15/expanded_fake_news_corpus) |

## Ciclo de vida da desinformação: como uma alegação nasce e se espalha

Estas bases respondem a uma pergunta diferente das anteriores: **não "este texto é falso?", e
sim "como isso começou e por onde andou?"**. São a matéria-prima para calibrar os sinais de
tempo e de corroboração ([RF-16](requisitos/funcionais.md),
[RF-27](requisitos/funcionais.md), [RF-28](requisitos/funcionais.md)).

| Dataset | Tamanho conferido | Por que serve | Link |
| --- | --- | --- | --- |
| **FakenewsBR v6** | **297.672 linhas**, 23 colunas | A mais completa. Tem `date_iso`, veículo de origem, `factcheck_rating`, `factcheck_claimant` e **marcas de estilo já calculadas**: número de exclamações, de interrogações, de reticências e proporção de palavras em caixa alta. Cobre 2021 a 2026, com 230.900 verdadeiras e 66.772 falsas | [github.com/thiago-cg/fakenewsbr-v4](https://github.com/thiago-cg/fakenewsbr-v4) |
| **FakeWhatsApp.Br** | **282.601 mensagens** (2018) e 2.898 rotuladas (2020) | Mensagens de grupos públicos com **data, hora, grupo e estado**, contagem de compartilhamentos e um **grafo de propagação** (`edges.p`). É onde dá para ver a mensagem nascendo e circulando | [github.com/cabrau/FakeWhatsApp.Br](https://github.com/cabrau/FakeWhatsApp.Br) |
| **Central de Fatos** | **11.647 checagens**, de 2013 a 2021 | Seis agências reunidas: Boatos (5.523), Lupa (2.574), Aos Fatos (1.679), Fato ou Fake (917), Estadão Verifica (593) e Comprova (361), com data e veredito | [huggingface.co/datasets/fake-news-UFG/central_de_fatos](https://huggingface.co/datasets/fake-news-UFG/central_de_fatos) |
| **MuMiN-PT** | 1.404 publicações | Cada publicação ligada à alegação checada, com **quase-duplicatas**, resultados de busca e de checagem. Mostra a **mesma alegação reaparecendo reescrita** | [huggingface.co/datasets/ju-resplande/portuguese-fact-checking](https://huggingface.co/datasets/ju-resplande/portuguese-fact-checking) |
| **COVID19.BR** | 1.987 publicações | Mesmo formato do MuMiN-PT, recorte de pandemia | (mesmo link acima) |
| **FACTCK.BR** | 1.313 alegações | Padrão **ClaimReview**, com escala fina de veredito: Falso 943, Verdadeiro 119, Exagerado 87, Distorcido 54, Sem contexto 42 | [github.com/jghm-f/FACTCK.BR](https://github.com/jghm-f/FACTCK.BR) |
| **FakeTweetBr** | 279 publicações | Pequeno, mas traz `retweets`, `favorites` e data | [github.com/prc992/FakeTweet.Br](https://github.com/prc992/FakeTweet.Br) |

!!! tip "O cruzamento mais útil para o Challenge"
    **FakenewsBR v6 + FakeWhatsApp.Br.** O primeiro dá o texto com as marcas de estilo e a
    data em que a agência checou; o segundo dá a difusão real, com hora e grupo. Cruzando os
    dois dá para medir **quanto tempo passa entre a mensagem começar a circular e o
    desmentido sair** — exatamente a janela em que a Vera precisa agir, e uma resposta direta
    à Guiding Question sobre como a desinformação se espalha.

## Ainda não baixados

| Dataset | Situação | Link |
| --- | --- | --- |
| **Fake news in Portuguese** (Kaggle) | Exige credencial: colocar `kaggle.json` em `~/.kaggle/` | [kaggle.com/datasets/fabioselau/fakes-news-portuguese](https://www.kaggle.com/datasets/fabioselau/fakes-news-portuguese) |
| **Telegram, 50 milhões de mensagens** (2022–2026, 655 grupos) | Maior fonte de propagação existente para o Brasil; acesso restrito e criptografado, mediante pedido ao autor | [zenodo.org/records/18946601](https://zenodo.org/records/18946601) |
| **Fakepedia Corpus** | A avaliar | [github.com/andersoncordeiro/Fakepedia-Corpus](https://github.com/andersoncordeiro/Fakepedia-Corpus) |
| **FactNews** | Factualidade por sentença, não por notícia | [github.com/franciellevargas/FactNews](https://github.com/franciellevargas/FactNews) |
| **FakeNewsSet** | A avaliar | [huggingface.co/datasets/fake-news-UFG/FakeNewsSet](https://huggingface.co/datasets/fake-news-UFG/FakeNewsSet) |

## Cuidados antes de treinar

- **Vazamento entre bases.** FakenewsBR v6 já incorpora 7.160 registros do Fake.Br. Treinar
  em uma e avaliar na outra infla a métrica.
- **Desbalanceamento.** FakenewsBR v6 tem 3,5 verdadeiras para cada falsa. Fake.Br e
  FakeRecogna são balanceados. A escolha muda a leitura do F1 exigido pelo
  [RNF-06](requisitos/nao-funcionais.md).
- **Idade dos dados.** Fake.Br e FKTC são de 2018 e 2019. Um modelo treinado só neles aprende
  o vocabulário daquelas eleições.
- **Viés de tema.** As bases concentram política, saúde e pandemia. Fora desses temas, o
  desempenho cai.
- **Licença e citação.** Cada base tem sua exigência de citação; registrar antes de publicar
  qualquer resultado.
