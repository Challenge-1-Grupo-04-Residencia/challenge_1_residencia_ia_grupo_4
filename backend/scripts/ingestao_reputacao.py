import sys
import os
from urllib.parse import urlparse

# Truque para enxergar a pasta src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from src.infrastructure.database import SessionLocal, DominioReputacao, iniciar_banco

def extrair_dominio(veiculo, url):
    """Tenta puxar o nome do site. Se não tiver, puxa a raiz da URL."""
    if pd.notna(veiculo) and str(veiculo).strip() != "":
        return str(veiculo).strip().lower()
    if pd.notna(url) and str(url).strip() != "":
        try:
            return urlparse(str(url)).netloc.lower()
        except:
            return None
    return None

def main():
    print("Iniciando cálculo de reputação das fontes...")
    iniciar_banco()
    
    # Datasets focados em Notícias (Onde faz sentido medir reputação de site)
    caminhos = [
        "datasets/fake-br/padronizado.parquet",
        "datasets/fakerecogna/padronizado.parquet",
        "datasets/faketrue-br/padronizado.parquet",
        "datasets/fakenewsbr-v6/padronizado.parquet"
    ]
    
    dfs = []
    for caminho in caminhos:
        if os.path.exists(caminho):
            print(f"Lendo {caminho}...")
            # Puxamos só o que importa pra não engasgar a memória do Mac
            dfs.append(pd.read_parquet(caminho, columns=['veiculo', 'url', 'rotulo']))

    if not dfs:
        print("Nenhum dataset de notícias encontrado!")
        return

    df_total = pd.concat(dfs, ignore_index=True)
    
    print("Mapeando os sites (domínios)...")
    df_total['dominio'] = df_total.apply(lambda row: extrair_dominio(row['veiculo'], row['url']), axis=1)
    df_total = df_total.dropna(subset=['dominio'])
    
    # Limpa labels sujas
    df_total['rotulo'] = df_total['rotulo'].astype(str).str.lower().str.strip()
    df_total = df_total[df_total['rotulo'].isin(['falso', 'verdadeiro'])]

    print("Contando as verdades e mentiras de cada site...")
    # Faz uma tabela dinâmica contando quantos falsos e verdadeiros cada domínio tem
    agrupado = df_total.groupby('dominio')['rotulo'].value_counts().unstack(fill_value=0)
    
    if 'falso' not in agrupado.columns: agrupado['falso'] = 0
    if 'verdadeiro' not in agrupado.columns: agrupado['verdadeiro'] = 0

    agrupado['total'] = agrupado['falso'] + agrupado['verdadeiro']
    
    # Calcula o score (0 a 100)
    agrupado['score'] = (agrupado['verdadeiro'] / agrupado['total']) * 100
    agrupado['score'] = agrupado['score'].fillna(50).astype(int)

    db = SessionLocal()
    try:
        print("Salvando as notas de reputação no Postgres...")
        # Apaga o antigo pra não dar conflito se você rodar 2 vezes
        db.query(DominioReputacao).delete()
        
        lote = []
        for dominio, row in agrupado.iterrows():
            lote.append(DominioReputacao(
                dominio=dominio[:255],
                total_noticias=int(row['total']),
                noticias_falsas=int(row['falso']),
                noticias_verdadeiras=int(row['verdadeiro']),
                score_confiabilidade=int(row['score'])
            ))
            
            # Insere em lotes pra ser super rápido
            if len(lote) >= 1000:
                db.bulk_save_objects(lote)
                db.commit()
                lote.clear()
        
        if lote:
            db.bulk_save_objects(lote)
            db.commit()

        print(f"Sucesso Total! A ficha criminal de {len(agrupado)} sites foi salva no banco!")
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
