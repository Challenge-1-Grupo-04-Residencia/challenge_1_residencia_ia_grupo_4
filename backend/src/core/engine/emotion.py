"""Análise de Intensidade Emocional usada pela camada N2 (RF-23, S-08)."""

import re
from collections import Counter

# Mini-Léxico inspirado no NRC Emotion Lexicon. Em produção, substitua
# pelo carregamento de um arquivo JSON/CSV oficial do NRC em Português.
LEXICO_EMOCIONAL_PT = {
    # Raiva (Anger)
    "ódio": "raiva", "revolta": "raiva", "absurdo": "raiva", "canalha": "raiva",
    "corrupção": "raiva", "bandido": "raiva", "vergonha": "raiva", "covardia": "raiva",
    "roubo": "raiva", "assassino": "raiva", "culpa": "raiva", "mentira": "raiva",
    "indignação": "raiva", "ladrão": "raiva", "canalhas": "raiva",
    
    # Medo (Fear)
    "perigo": "medo", "ameaça": "medo", "pânico": "medo", "terror": "medo",
    "morte": "medo", "risco": "medo", "cuidado": "medo", "assustador": "medo",
    "vírus": "medo", "fatal": "medo", "crise": "medo", "urgente": "medo",
    "doença": "medo", "destruição": "medo", "guerra": "medo",
    
    # Nojo (Disgust)
    "nojo": "nojo", "repugnante": "nojo", "sujeira": "nojo", "podre": "nojo",
    "doente": "nojo", "verme": "nojo", "lixo": "nojo", "imundo": "nojo",
    "asqueroso": "nojo", "esgoto": "nojo"
}

_PALAVRA = re.compile(r"\b[\wÀ-ÿ]+\b", re.UNICODE)

def analisar_emocoes(texto: str) -> dict[str, int]:
    """Conta a frequência de cada emoção predominante no texto."""
    baixo = texto.lower()
    palavras = _PALAVRA.findall(baixo)
    
    contagem = Counter()
    for p in palavras:
        if p in LEXICO_EMOCIONAL_PT:
            emocao = LEXICO_EMOCIONAL_PT[p]
            contagem[emocao] += 1
            
    return dict(contagem)

def indice_intensidade_emocional(texto: str) -> tuple[float, str]:
    """
    Retorna (indice_de_0_a_1, emocao_predominante).
    Mede a densidade de palavras emocionais extremas no texto.
    """
    palavras = _PALAVRA.findall(texto.lower())
    if not palavras:
        return 0.0, ""
        
    contagem = analisar_emocoes(texto)
    total_emocionais = sum(contagem.values())
    
    if total_emocionais == 0:
        return 0.0, ""
    
    # Matemática do Sinal: Se 3% ou mais das palavras forem extremas, satura em 1.0.
    densidade = total_emocionais / len(palavras)
    indice = min(1.0, densidade / 0.03)
    
    emocao_predominante = max(contagem.items(), key=lambda x: x[1])[0]
        
    return indice, emocao_predominante
