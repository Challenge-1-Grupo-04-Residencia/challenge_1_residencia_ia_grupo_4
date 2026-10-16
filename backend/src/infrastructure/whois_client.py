import os
import logging
from datetime import datetime
from functools import lru_cache

import httpx

_log = logging.getLogger(__name__)

@lru_cache(maxsize=1000)
def consultar_idade_meses(dominio: str) -> int | None:
    """Consulta a idade do domínio em meses usando cache para não repetir."""
    api_key = os.getenv("WHOIS_API_KEY")
    if not api_key:
        _log.warning("WHOIS_API_KEY não configurada. Consulta WHOIS pulada.")
        return None

    # Usamos uma API genérica como exemplo
    url = "https://api.api-ninjas.com/v1/whois"
    headers = {"X-Api-Key": api_key}
    params = {"domain": dominio}

    try:
        response = httpx.get(url, headers=headers, params=params, timeout=5.0)
        response.raise_for_status()
        dados = response.json()

        data_criacao_timestamp = dados.get("creation_date")
        if not data_criacao_timestamp:
            return None

        data_criacao = datetime.fromtimestamp(data_criacao_timestamp)
        hoje = datetime.now()
        
        diferenca_dias = (hoje - data_criacao).days
        diferenca_meses = diferenca_dias // 30
        return max(0, diferenca_meses)

    except (httpx.RequestError, httpx.HTTPStatusError, ValueError, TypeError) as e:
        _log.warning(f"Falha ao consultar WHOIS para {dominio}: {e}")
        return None