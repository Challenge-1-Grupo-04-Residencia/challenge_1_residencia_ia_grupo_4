from src.core.engine.orchestrator import CamadaVerificacao, Evento
from src.core.entities.claim import NoticiaRequest, DocumentoRelacionado
from src.core.entities.signal import medir

# Importa o banco que você criou no passo anterior
from src.infrastructure.database import SessionLocal, ChecagemCache

class CamadaN0Cache(CamadaVerificacao):
    """N0 (Cache) - Corta caminho se a notícia já estiver no banco (RF-17)."""

    nome: str = "N0"

    def processar(self, noticia: NoticiaRequest) -> NoticiaRequest:
        resultado = noticia.resultado
        resultado.camada_atual = "N0"
        
        # Limpa espaços e quebras de linha em volta do texto que veio do Frontend
        texto_limpo = noticia.texto.strip() if noticia.texto else ""
        
        url_busca = noticia.url
        if not url_busca and texto_limpo.startswith("http"):
            url_busca = texto_limpo

        print(f"[DEBUG N0] URL extraída para busca: {url_busca}")

        if not url_busca:
            print("[DEBUG N0] Nenhuma URL detectada. Repassando para N2.")
            return self.repassar(noticia)

        try:
            with SessionLocal() as db:
                cache_hit = db.query(ChecagemCache).filter(
                    (ChecagemCache.url_agencia == url_busca)
                    | (ChecagemCache.url_agencia == url_busca.rstrip("/"))
                    | (ChecagemCache.url_agencia == url_busca.rstrip("/") + "/")
                ).first()
                print(f"[DEBUG N0] Resultado da busca no banco: {cache_hit}")

                if cache_hit:
                    veredicto_limpo = cache_hit.veredicto.strip().lower()
                    nota = 0.0 if veredicto_limpo == "falso" else 1.0

                    agencia_nome = cache_hit.agencia or "Agência de Checagem"
                    if agencia_nome.lower() == "lupa":
                        agencia_nome = "Agência Lupa"
                    elif agencia_nome.lower() == "aos fatos":
                        agencia_nome = "Aos Fatos"
                    elif agencia_nome.islower():
                        agencia_nome = agencia_nome.title()

                    # Preenche os metadados para ativar a RN-01 no Orquestrador
                    resultado.veredito_agencia = "falso" if veredicto_limpo == "falso" else "verdadeiro"
                    resultado.agencia = agencia_nome

                    # Registra o sinal S-00 com peso 100 para demonstrar cobertura completa
                    sinal_n0 = medir("S-00", nota, f"Checagem instantânea confirmada via {agencia_nome}.")
                    sinal_n0.peso = 100.0
                    resultado.registrar(sinal_n0)
                    resultado.veracidade = 10.0 if veredicto_limpo == "falso" else 90.0
                    resultado.confianca = 1.0

                    # Adiciona aos documentos relacionados para o frontend exibir o card oficial clicável
                    resultado.documentos_relacionados.append(
                        DocumentoRelacionado(
                            titulo=cache_hit.texto_alegacao or f"Checagem oficial — {agencia_nome}",
                            url=cache_hit.url_agencia,
                            fonte=agencia_nome,
                            similaridade=1.0,
                            similaridade_textual=True,
                            fonte_confiavel=True,
                            e_checagem=True,
                        )
                    )
                    if cache_hit.url_agencia:
                        resultado.fontes_citadas.append(cache_hit.url_agencia)

                    # Justificativa concisa sem duplicar o motivo_regra (RN-01 já traz a agência)
                    resultado.explicacao = (
                        f"A apuração foi concluída diretamente na camada N0 (Cache), "
                        f"pois o link já consta verificado na base oficial."
                    )

                    self._avisar(
                        Evento(
                            tipo="concluiu",
                            camada=self.nome,
                            mensagem=f"Checagem oficial encontrada via {agencia_nome}.",
                            sinais=resultado.sinais,
                        )
                    )

                    # RETORNO IMEDIATO: Impede que a N1, N2, N3 e N4 rodem!
                    return noticia
                    
        except Exception as e:
            print(f"[Aviso N0] Falha ao consultar o banco de dados: {e}")

        # Se não achou, passa a bola pra Camada N1/N2 ter que trabalhar
        return self.repassar(noticia)