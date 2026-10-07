#!/usr/bin/env python
"""Roda o pipeline completo numa alegação, do terminal, para inspeção manual.

    uv run python backend/scripts/debug_pipeline.py
    uv run python backend/scripts/debug_pipeline.py "o texto que você quer checar"

Usa a infraestrutura real — GDELT e Ollama —, então é diagnóstico e não teste: serve
para ver o que cada camada mediu numa checagem de verdade. Com o GDELT fora do ar ou o
Ollama desligado, S-11 e S-12 saem indisponíveis, que é o comportamento correto (RN-06),
e as justificativas dizem qual das duas coisas aconteceu.

Estava em ``backend/debug_pipeline.py``, dentro do pacote: como ``--app-dir backend``
coloca ``backend/`` no ``sys.path``, o script virava módulo importável ao lado de
``src``. Aqui fica claro que é ferramenta, não código de produção.
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.engine.n2_content import CamadaN2Conteudo  # noqa: E402
from src.core.engine.n3_corroboration import CamadaN3Corroboracao  # noqa: E402
from src.core.engine.n4_nli import CamadaN4Inferencia  # noqa: E402
from src.core.engine.orchestrator import Orquestrador  # noqa: E402
from src.core.entities.claim import NoticiaRequest  # noqa: E402
from src.infrastructure.search.gdelt import BuscadorGdelt  # noqa: E402

TEXTO_PADRAO = (
    "Chá de limão com alho mata completamente o vírus da COVID-19 em 24 horas, "
    "afirma estudo que a mídia não mostra. URGENTE, REPASSEM!!!"
)


def run(texto: str = TEXTO_PADRAO) -> None:
    # Os avisos das camadas (GDELT fora do ar, Ollama sem resposta) vão para o log; sem
    # isto o diagnóstico fica cego justamente quando algo falha.
    logging.basicConfig(level=logging.INFO, format="  [%(name)s] %(message)s")

    print("Montando o pipeline N2 -> N3 -> N4...")
    n2 = CamadaN2Conteudo()
    n3 = CamadaN3Corroboracao(BuscadorGdelt())
    n4 = CamadaN4Inferencia()
    n2.set_proxima(n3).set_proxima(n4)
    orquestrador = Orquestrador(n2)

    noticia = NoticiaRequest(texto=texto)
    print(f"\nAlegação: {texto!r}")
    print("Aguarde: a N3 consulta o GDELT e a N4 chama o modelo.\n")

    veredito = orquestrador.veredito(noticia)
    resultado = noticia.resultado

    print("=" * 78)
    print(f"Veredito:         {veredito.faixa.value}")
    veracidade = (
        "sem porcentagem"
        if veredito.veracidade is None
        else f"{veredito.veracidade:.1f}%"
    )
    print(f"Veracidade:       {veracidade}")
    print(f"Confiança:        {veredito.confianca:.2f}")
    print(f"Cobertura:        {resultado.cobertura:.2f} do que sabemos medir "
          f"({resultado.cobertura_do_catalogo:.2f} do catálogo completo)")
    print(f"Parou em:         {resultado.camada_atual}")
    print(f"Regra aplicada:   {veredito.regra_aplicada or '(nenhuma)'}")
    print("\nExplicação da Vera:")
    print(f"  {(veredito.motivo_regra + ' ' + resultado.explicacao).strip()}")

    print("\nSinais:")
    for sinal in resultado.sinais:
        score = "indisponível" if sinal.score is None else f"{sinal.score:.2f}"
        print(f"  {sinal.id} peso {sinal.peso:>4}  {score:>12}  {sinal.justificativa}")

    if resultado.documentos_relacionados:
        print("\nPublicações encontradas:")
        for documento in resultado.documentos_relacionados:
            selo = "confiável" if documento.fonte_confiavel else "fora da base"
            print(f"  [{selo}] {documento.fonte}: {documento.titulo[:60]}")


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else TEXTO_PADRAO)
