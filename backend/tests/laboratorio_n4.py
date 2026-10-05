#!/usr/bin/env python
"""Laboratório da camada N4: roda contra o Ollama **de verdade** (RF-30, S-12).

    docker compose up -d ollama
    docker exec -it vera_ollama ollama pull llama3
    uv run python backend/tests/laboratorio_n4.py

Não é suíte de teste, e o nome não começa com ``test_`` justamente por isso: o pytest
não o coleta. Serve para avaliar a **qualidade do julgamento do modelo** nos casos
difíceis de inferência — distorção de magnitude, equivalência semântica, citação fora de
contexto —, que é coisa que duplo de teste não mede.

Os testes automatizados da camada ficam em ``test_n4_nli.py`` e usam duplo: eles cobrem
a matemática do S-12, o tratamento de falha do provedor e o parsing de resposta
malformada, sem tocar a rede. Antes, os casos daqui estavam dentro da suíte com um
``pytest.skip`` quando o Ollama não respondia — o efeito era a camada que mede o sinal
mais pesado do catálogo ficar com zero cobertura real em toda máquina sem Docker ligado,
e na CI.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.engine.n4_nli import CamadaN4Inferencia, ErroDoProvedor  # noqa: E402
from src.core.entities.claim import NoticiaRequest  # noqa: E402

SUSTENTA, CONTRADIZ, NEUTRO = "SUSTENTA", "CONTRADIZ", "NEUTRO"

CASOS: tuple[tuple[str, str, list[str], str], ...] = (
    (
        "Fake news clara",
        "Chá de limão com alho mata completamente o vírus da COVID-19 em 24 horas, "
        "afirma estudo vazado.",
        [
            "A Organização Mundial da Saúde declarou que não existem provas "
            "científicas de que chás caseiros ou alho eliminem o vírus da COVID-19.",
            "Infectologistas alertam que curas milagrosas baseadas em limão não "
            "substituem a vacinação e os tratamentos médicos oficiais.",
        ],
        CONTRADIZ,
    ),
    (
        "Notícia verdadeira",
        "O Brasil ganhou a medalha de ouro no futebol masculino nas Olimpíadas do Rio "
        "em 2016.",
        [
            "Em uma partida emocionante no Maracanã, a seleção brasileira de futebol "
            "masculino venceu a Alemanha nos pênaltis e garantiu o ouro inédito nas "
            "Olimpíadas de 2016.",
        ],
        SUSTENTA,
    ),
    (
        "Inconclusivo por neutralidade",
        "O prefeito vai anunciar um novo imposto sobre bicicletas elétricas no mês que "
        "vem.",
        [
            "O prefeito discursou hoje dizendo que a prefeitura vai investir em novas "
            "ciclovias e melhorias para ciclistas.",
            "Câmara de vereadores debate projeto de lei sobre impostos veiculares, mas "
            "o texto foca apenas em carros a diesel.",
        ],
        NEUTRO,
    ),
    (
        "Distorção de magnitude",
        "A bolsa de valores caiu impressionantes 50% hoje devido ao novo imposto.",
        [
            "O mercado financeiro fechou o dia em leve baixa. O principal índice da "
            "bolsa recuou 2% após o anúncio da nova taxação.",
        ],
        CONTRADIZ,
    ),
    (
        "Equivalência semântica",
        "A capital da França baniu definitivamente o uso de patinetes elétricos nas "
        "ruas.",
        [
            "Paris implementou hoje a nova lei municipal proibindo a circulação de "
            "e-scooters alugados, após referendo aprovado pela população.",
        ],
        SUSTENTA,
    ),
    (
        "Distorção temporal",
        "Urgente: o presidente do Brasil renunciou ao cargo na noite de ontem.",
        [
            "O presidente do Brasil assinou ontem um decreto sobre novas regras "
            "trabalhistas.",
            "Em 1992, o então presidente do Brasil renunciou ao cargo durante o "
            "processo de impeachment.",
        ],
        CONTRADIZ,
    ),
    (
        "Correlação versus causalidade",
        "Estudo comprova que vacinas da gripe causam autismo em crianças recém-nascidas.",
        [
            "Pesquisadores explicam que os sintomas de autismo costumam ser "
            "identificados na mesma faixa etária em que as crianças recebem as "
            "primeiras vacinas, mas dezenas de estudos globais provam que não existe "
            "relação biológica entre os dois eventos.",
        ],
        CONTRADIZ,
    ),
    (
        "Citação fora de contexto",
        "O Papa declarou hoje publicamente que ama o Diabo e suas obras.",
        [
            "Durante a missa de domingo, o Papa discursou: 'Devemos amar o pecador, "
            "mas jamais devemos amar o Diabo ou aceitar suas obras tentadoras'.",
        ],
        CONTRADIZ,
    ),
    (
        "Equivalência numérica",
        "A empresa de tecnologia faturou mais de 1 bilhão de reais no último ano.",
        [
            "O balanço financeiro divulgado pela corporação registra que o faturamento "
            "total do ano passado fechou em 1.250.000.000,00 BRL.",
        ],
        SUSTENTA,
    ),
    (
        "Irrelevância total",
        "Elon Musk comprou a rede de fast food McDonald's.",
        [
            "Elon Musk, dono da Tesla, concluiu a aquisição do Twitter por 44 bilhões "
            "de dólares.",
            "O McDonald's anunciou hoje o lançamento de um novo hambúrguer vegano.",
        ],
        NEUTRO,
    ),
)


def _classificar(score: float | None) -> str:
    if score is None:
        return NEUTRO
    if score > 0.5:
        return SUSTENTA
    if score < 0.5:
        return CONTRADIZ
    return "DIVIDIDO"


def main() -> int:
    camada = CamadaN4Inferencia()
    acertos = 0

    for nome, alegacao, evidencias, esperado in CASOS:
        noticia = NoticiaRequest(texto=alegacao)
        noticia.resultado.evidencias = evidencias
        try:
            camada.processar(noticia)
        except ErroDoProvedor as erro:
            print(f"[{nome}] provedor indisponível: {erro}")
            print("Suba o Ollama antes de rodar o laboratório.")
            return 2

        sinal = next(s for s in noticia.resultado.sinais if s.id == "S-12")
        obtido = _classificar(sinal.score)
        ok = obtido == esperado
        acertos += ok

        print(f"\n{'=' * 78}\n{nome}")
        print(f"  alegação:  {alegacao[:70]}")
        print(f"  esperado:  {esperado}   obtido: {obtido}   {'OK' if ok else 'ERROU'}")
        score = "indisponível" if sinal.score is None else f"{sinal.score:.2f}"
        print(f"  S-12:      {score}")
        print(f"  justifica: {sinal.justificativa}")

    print(f"\n{'=' * 78}")
    print(f"{acertos} de {len(CASOS)} casos como esperado.")
    print(
        "Divergência aqui é qualidade de julgamento do modelo, não defeito do código: "
        "avalie se vale trocar o modelo ou ajustar o prompt."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
