# Datasets

??? abstract "Histórico de revisão"

    | Data | Versão | Descrição | Autor |
    | :---: | :---: | --- | --- |
    | 21/09 | 1.0 | Levantamento, download e verificação das bases em PT-BR | Ian Costa, Luísa Brambilla, Maykon Soares, Natália Evelin, Rebeca Bontempo |

Todas as bases desta página são **em português do Brasil** e foram **baixadas e conferidas**:
os números abaixo são a contagem real dos arquivos, não o que o artigo original anuncia.

!!! tip "Como baixar"
    ```bash
    ./scripts/baixar_datasets.sh
    ```
    O script recria a pasta `datasets/` (cerca de 1,3 GB), que fica **fora do controle de
    versão**. Nenhum dado é commitado no repositório.

## Corpora rotulados: treinar e avaliar o classificador

Servem à camada **N2 · Conteúdo** ([RF-21](requisitos/funcionais.md) a
[RF-26](requisitos/funcionais.md)) e ao conjunto de avaliação exigido pelo
[RNF-06](requisitos/nao-funcionais.md).

| Dataset | Tamanho conferido | Conteúdo | Licença | Link |
| --- | --- | --- | --- | --- |
| **Fake.Br Corpus** | 3.600 falsas + 3.600 verdadeiras | Texto integral, versão pré-processada e normalizada por tamanho, com metadados | Acadêmica, citar o artigo | [github.com/roneysco/Fake.br-Corpus](https://github.com/roneysco/Fake.br-Corpus) |
| **FakeRecogna** | 11.903 registros | Título, subtítulo, texto, **categoria**, data, autor, URL e classe | MIT | [huggingface.co/datasets/recogna-nlp/FakeRecogna](https://huggingface.co/datasets/recogna-nlp/FakeRecogna) |
| **FakeTrue.Br** | 1.791 pares | Cada notícia falsa **pareada com a verdadeira** sobre o mesmo fato, com os dois links | Acadêmica | [github.com/jpchav98/FakeTrue.Br](https://github.com/jpchav98/FakeTrue.Br) |
| **FKTC** | 2.168 notícias | Política, eleições de 2018 e 2019, vindas de Aos Fatos, Lupa e UOL Confere | Acadêmica | [github.com/GoloMarcos/FKTC](https://github.com/GoloMarcos/FKTC) |
| **Fake.Br no Hugging Face** | o mesmo Fake.Br | Carregamento direto pela biblioteca `datasets` | Acadêmica | [huggingface.co/datasets/fake-news-UFG/fakebr](https://huggingface.co/datasets/fake-news-UFG/fakebr) |
| **Expanded Fake News Corpus** | JSON | Expansão do Fake.Br com mais notícias | Verificar no repositório | [github.com/Pedrest15/expanded_fake_news_corpus](https://github.com/Pedrest15/expanded_fake_news_corpus) |

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
