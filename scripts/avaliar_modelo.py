import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import pandas as pd
import requests
import json
import time
import argparse
from datetime import datetime
# Configs
API_URL = "http://localhost:8000/api/v1/checar"
from src.infrastructure.database import SessionLocal


def classificar_dataset(caminho_parquet, nome_dataset, limite=100):
    print(f"\n🚀 Iniciando avaliação do dataset: {nome_dataset}")
    try:
        df = pd.read_parquet(caminho_parquet)
    except Exception as e:
        print(f"❌ Erro ao ler {caminho_parquet}: {e}")
        return

    # Tenta achar a coluna de texto e label
    col_texto = 'texto' if 'texto' in df.columns else 'text' if 'text' in df.columns else df.columns[0]
    
    # Busca coluna de classe/label
    col_label = None
    for c in ['classe', 'label', 'verdadeiro', 'is_fake', 'fake', 'rotulo']:
        if c in df.columns:
            col_label = c
            break

    if not col_label:
        print("⚠️ Não achei coluna de classe (Falso/Verdadeiro). Pegando apenas as amostras.")
        amostras = df.head(limite)
    else:
        print(f"✅ Coluna de texto: '{col_texto}' | Coluna de label: '{col_label}'")
        # Estratificando: Metade de cada classe
        classes = df[col_label].unique()
        amostras = pd.DataFrame()
        por_classe = limite // len(classes)
        for cls in classes:
            amostras = pd.concat([amostras, df[df[col_label] == cls].head(por_classe)])
        
        # Se faltar para dar o limite, pega aleatório
        if len(amostras) < limite:
            faltam = limite - len(amostras)
            amostras = pd.concat([amostras, df[~df.index.isin(amostras.index)].head(faltam)])

    amostras = amostras.sample(frac=1).reset_index(drop=True) # Shuffle
    
    total = len(amostras)
    acertos = 0
    falsos_positivos = 0
    inconclusivos = 0
    inicio = time.time()

    print(f"⏳ Disparando {total} requisições contra a API ({API_URL})...")
    
    for i, row in amostras.iterrows():
        texto = str(row[col_texto])
        if col_label:
            label_real = str(row[col_label]).lower()
            # Mapeia para booleano: True = Falso, False = Verdadeiro (ou vice versa dependendo do dataset)
            # Assumimos que "verdade" ou "true" ou "1" significa Verdadeiro
            e_realmente_verdade = "verdade" in label_real or label_real in ["1", "true", "real"]
        else:
            e_realmente_verdade = None

        try:
            resp = requests.post(API_URL, json={"texto": texto}, timeout=30)
            if resp.status_code == 200:
                resultado = resp.json()
                faixa = resultado.get("faixa", "").lower()
                
                # Inconclusivo
                if "inconclusiv" in faixa:
                    inconclusivos += 1
                elif e_realmente_verdade is not None:
                    e_vera_verdade = "verdadeir" in faixa
                    
                    if e_vera_verdade == e_realmente_verdade:
                        acertos += 1
                    else:
                        # Vera errou
                        if e_vera_verdade and not e_realmente_verdade:
                            falsos_positivos += 1
            else:
                print(f"Falha API: {resp.status_code}")
        except requests.exceptions.RequestException as e:
             print(f"Erro de conexão com API: {e}")
             continue
             
        # Mostrar progresso
        if (i+1) % 10 == 0:
            print(f"   Progresso: {i+1}/{total} processados...")

    tempo_medio = int(((time.time() - inicio) / total) * 1000)
    
    # Calcular %
    taxa_inconclusivos = int((inconclusivos / total) * 100)
    validos = total - inconclusivos
    
    if validos > 0:
        acuracia = int((acertos / validos) * 100)
        tx_falsos_positivos = int((falsos_positivos / validos) * 100)
    else:
        acuracia = 0
        tx_falsos_positivos = 0

    print("\n📊 RESULTADOS:")
    print(f"   Acurácia (excluindo inconclusivos): {acuracia}%")
    print(f"   Falsos Positivos: {tx_falsos_positivos}%")
    print(f"   Inconclusivos (Proteção): {taxa_inconclusivos}%")
    print(f"   Tempo Médio por requisição: {tempo_medio}ms")

    # Salva no Banco de Dados
    from src.infrastructure.database import HistoricoAvaliacaoLote
    try:
        with SessionLocal() as db:
            nova_aval = HistoricoAvaliacaoLote(
                data_execucao=datetime.now().isoformat(),
                dataset=nome_dataset,
                qtd_amostras=total,
                acuracia=acuracia,
                taxa_falsos_positivos=tx_falsos_positivos,
                taxa_inconclusivos=taxa_inconclusivos,
                tempo_medio_ms=tempo_medio
            )
            db.add(nova_aval)
            db.commit()
            print("💾 Avaliação salva no banco de dados com sucesso!")
    except Exception as e:
        print(f"⚠️ Não foi possível salvar no banco (o banco subiu?): {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auditoria de Datasets da Vera")
    parser.add_argument("--dataset", required=True, help="Ex: fakewhatsapp-br")
    parser.add_argument("--n", type=int, default=100, help="Quantidade de amostras para testar")
    args = parser.parse_args()

    caminho = f"../datasets/{args.dataset}/padronizado.parquet" if not args.dataset.endswith(".parquet") else args.dataset
    import os
    if not os.path.exists(caminho):
        # Tenta no formato relativo padrão
        caminho = f"datasets/{args.dataset}/padronizado.parquet"
        
    classificar_dataset(caminho, args.dataset, args.n)
