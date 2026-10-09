import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import pandas as pd
import requests
import json
import time
import argparse
from datetime import datetime
import os

def descobrir_url_api():
    if "API_URL" in os.environ:
        return os.environ["API_URL"]
    for porta in [8010, 8000]:
        try:
            resp = requests.get(f"http://localhost:{porta}/health", timeout=1)
            if resp.status_code == 200:
                return f"http://localhost:{porta}/api/v1/checar"
        except Exception:
            pass
    return "http://localhost:8010/api/v1/checar"

API_URL = descobrir_url_api()
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

    col_url = 'url' if 'url' in df.columns else None

    if not col_label:
        print("⚠️ Não achei coluna de classe (Falso/Verdadeiro). Pegando apenas as amostras.")
        amostras = df.head(limite)
    else:
        print(f"✅ Coluna de texto: '{col_texto}' | Coluna de label: '{col_label}'" + (f" | Coluna URL: '{col_url}'" if col_url else ""))
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

    amostras = amostras.sample(frac=1, random_state=42).reset_index(drop=True) # Shuffle reproduzível
    
    total = len(amostras)
    acertos = 0
    falsos_positivos = 0
    inconclusivos = 0
    inicio = time.time()

    print(f"⏳ Disparando {total} requisições contra a API ({API_URL})...\n")
    
    for i, row in amostras.iterrows():
        texto = str(row[col_texto])
        payload = {"texto": texto}
        if col_url and pd.notna(row[col_url]):
            url_cand = str(row[col_url]).strip()
            if url_cand.startswith("http"):
                payload["url"] = url_cand

        if col_label:
            label_real = str(row[col_label]).lower()
            # Mapeia para booleano: True = Falso, False = Verdadeiro (ou vice versa dependendo do dataset)
            # Assumimos que "verdade" ou "true" ou "1" significa Verdadeiro
            e_realmente_verdade = "verdade" in label_real or label_real in ["1", "true", "real"]
        else:
            e_realmente_verdade = None

        try:
            resp = requests.post(API_URL, json=payload, timeout=35)
            if resp.status_code == 200:
                resultado = resp.json()
                faixa_raw = resultado.get("faixa", "").strip()
                faixa = faixa_raw.lower()
                veracidade = resultado.get("veracidade")
                confianca = resultado.get("confianca", 0.0)
                camada_parou = resultado.get("camada_atual", "N?")

                # No catálogo oficial da Vera:
                # - "Confirmada por fontes" e "Provavelmente verdadeira" -> Verdadeiro
                # - "Provavelmente falsa" e "Duvidosa" -> Falso
                # - "Inconclusiva" -> Abstenção / Proteção
                if "inconclusiv" in faixa:
                    inconclusivos += 1
                    diagnostico = "⚪ INCONCLUSIVO"
                elif e_realmente_verdade is not None:
                    e_vera_verdade = ("verdadeir" in faixa or "confirmada" in faixa)
                    
                    if e_vera_verdade == e_realmente_verdade:
                        acertos += 1
                        diagnostico = "✅ ACERTO"
                    else:
                        diagnostico = "❌ ERRO"
                        if e_vera_verdade and not e_realmente_verdade:
                            falsos_positivos += 1
                else:
                    diagnostico = "❓ SEM RÓTULO"

                v_str = f"{veracidade:.1f}%" if veracidade is not None else "s/p"
                print(f"   [{i+1:>2}/{total}] {diagnostico} | Real: {'Verdadeiro' if e_realmente_verdade else 'Falso':<10} | Vera: {faixa_raw:<25} (V={v_str:<6} C={confianca:.2f} Parou:{camada_parou})")
            else:
                print(f"   [{i+1:>2}/{total}] ⚠️ Falha API HTTP {resp.status_code}")
        except requests.exceptions.RequestException as e:
             print(f"   [{i+1:>2}/{total}] ⚠️ Erro de conexão com API: {e}")
             continue

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

DATASETS_BENCHMARK = ["fake-br", "fakerecogna", "faketrue-br", "fakewhatsapp-br"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auditoria de Datasets da Vera")
    parser.add_argument("--dataset", default="todos", help="Ex: fake-br, fakerecogna, faketrue-br, fakewhatsapp-br ou 'todos'")
    parser.add_argument("--n", type=int, default=20, help="Quantidade de amostras por dataset para testar")
    args = parser.parse_args()

    import os

    alvos = DATASETS_BENCHMARK if args.dataset.lower() in ["todos", "all"] else [args.dataset]

    for ds in alvos:
        caminho = f"../datasets/{ds}/padronizado.parquet" if not ds.endswith(".parquet") else ds
        if not os.path.exists(caminho):
            caminho = f"datasets/{ds}/padronizado.parquet"
            
        if os.path.exists(caminho):
            classificar_dataset(caminho, ds, args.n)
        else:
            print(f"⚠️ Dataset '{ds}' não encontrado no caminho {caminho}")

