#!/usr/bin/env bash
# Baixa os datasets em PT-BR usados na fase Investigate.
# Uso: ./scripts/baixar_datasets.sh
# Destino: datasets/ (~1,3 GB, fora do controle de versão).
set -euo pipefail

DESTINO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/datasets"
mkdir -p "$DESTINO"
cd "$DESTINO"

clonar() {  # clonar <repo> <pasta>
  if [ -d "$2" ]; then echo "já existe: $2"; else
    echo "clonando $2..."; git clone -q --depth 1 "https://github.com/$1.git" "$2"
  fi
}

baixar() {  # baixar <url> <arquivo>
  if [ -f "$2" ]; then echo "já existe: $2"; else
    echo "baixando $2..."; mkdir -p "$(dirname "$2")"; curl -sL -o "$2" "$1"
  fi
}

# Corpora rotulados
clonar roneysco/Fake.br-Corpus        Fake.br-Corpus
clonar GoloMarcos/FKTC                FKTC
clonar jpchav98/FakeTrue.Br           FakeTrue.Br
clonar Pedrest15/expanded_fake_news_corpus expanded_fake_news_corpus
baixar https://huggingface.co/datasets/recogna-nlp/FakeRecogna/resolve/main/FakeRecogna.csv \
       FakeRecogna/FakeRecogna.csv

# Ciclo de vida e propagação
clonar cabrau/FakeWhatsApp.Br         FakeWhatsApp.Br
clonar prc992/FakeTweet.Br            FakeTweet.Br
clonar thiago-cg/fakenewsbr-v4        fakenewsbr-v4
# os CSV do fakenewsbr-v4 estão em Git LFS: baixados pela URL de mídia
for f in FakenewsBR_v6_public.csv FakenewsBR_v6_labels.csv; do
  baixar "https://media.githubusercontent.com/media/thiago-cg/fakenewsbr-v4/main/data/$f" \
         "fakenewsbr-v4/data/$f"
done
baixar https://huggingface.co/datasets/fake-news-UFG/central_de_fatos/resolve/main/central_de_fatos.tsv \
       central_de_fatos/central_de_fatos.tsv
baixar https://raw.githubusercontent.com/jghm-f/FACTCK.BR/master/FACTCKBR.tsv \
       FACTCK.BR/FACTCKBR.tsv
for f in MuMiN-PT.parquet MuMiN-PT_raw.parquet COVID19.BR.parquet COVID19.BR_raw.parquet Fake.br.parquet; do
  baixar "https://huggingface.co/datasets/ju-resplande/portuguese-fact-checking/resolve/main/$f" \
         "portuguese-fact-checking/$f"
done

echo
echo "pronto. tamanho:"; du -sh "$DESTINO"
