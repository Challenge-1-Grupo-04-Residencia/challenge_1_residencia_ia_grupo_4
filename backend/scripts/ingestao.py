import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from src.infrastructure.database import SessionLocal, ChecagemCache, iniciar_banco

def carregar_dataset(caminho: str, db):
    if not os.path.exists(caminho):
        print(f"[{caminho}] Arquivo não encontrado.")
        return 0

    print(f"[{caminho}] Lendo parquet...")
    df = pd.read_parquet(caminho)
    
    # Filtra apenas linhas que têm URL, já que a N0 atual pesquisa por link
    df = df.dropna(subset=['url'])
    df = df.drop_duplicates(subset=['url'])

    # Puxa o que já tem no banco para não duplicar
    urls_existentes = {u[0] for u in db.query(ChecagemCache.url_agencia).all()}

    lote = []
    inseridos = 0

    for _, row in df.iterrows():
        url = str(row['url']).strip()
        
        # Ignora se já inserimos antes
        if url in urls_existentes:
            continue
            
        rotulo = str(row['rotulo']).strip().lower()
        # A N0 é um fast-track que corta caminho para coisas muito óbvias. 
        # Vamos inserir apenas os "falso" e "verdadeiro".
        if rotulo not in ["falso", "verdadeiro"]:
            continue
            
        titulo = str(row['titulo']).strip() if pd.notna(row['titulo']) else str(row['texto']).strip()
        veiculo = str(row['veiculo']).strip() if pd.notna(row['veiculo']) else "Agência de Checagem"

        lote.append(
            ChecagemCache(
                texto_alegacao=titulo[:2000],  # Corte de segurança para textos gigantes
                veredicto=rotulo.capitalize(),
                agencia=veiculo,
                url_agencia=url
            )
        )
        
        urls_existentes.add(url)
        
        # Insere em lotes de 1000 para ser rápido e não explodir a RAM
        if len(lote) >= 1000:
            db.bulk_save_objects(lote)
            db.commit()
            inseridos += len(lote)
            lote.clear()

    # Salva o restinho que sobrou
    if lote:
        db.bulk_save_objects(lote)
        db.commit()
        inseridos += len(lote)

    print(f"[{caminho}] {inseridos} links injetados com sucesso!")
    return inseridos


def main():
    print("Iniciando ingestão massiva de checagens para a Camada N0...")
    # Garante que as tabelas existam
    iniciar_banco()
    
    # Os dois datasets apontados por você que têm (canal = checagem)
    datasets = [
        "datasets/central-de-fatos/padronizado.parquet",
        "datasets/factck-br/padronizado.parquet"
    ]
    
    db = SessionLocal()
    try:
        total = 0
        for ds in datasets:
            total += carregar_dataset(ds, db)
        print(f"--- Ingestão 100% concluída! Um total de {total} novas URLs agora são conhecidas pela Vera ---")
    except Exception as e:
        print(f"Erro na ingestão: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
