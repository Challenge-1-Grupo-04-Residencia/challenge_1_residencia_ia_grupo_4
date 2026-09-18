# Requisitos não funcionais

??? abstract "Histórico de revisão"

    | Data | Versão | Descrição | Autor |
    | :---: | :---: | --- | --- |
    | 16/09 | 1.0 | Criação da página | Maykon Soares |

Os valores-alvo são a proposta inicial e devem ser confirmados antes do início da fase Act.

| ID | Categoria | Requisito | Métrica / alvo | MoSCoW |
| --- | --- | --- | --- | --- |
| RNF-01 | **Transparência** | Todo resultado é explicável: sinais, pesos e fontes ficam visíveis | 100% dos resultados com explicação (RN-05) | M |
| RNF-02 | **Desempenho** | Resposta rápida quando a checagem para cedo | N0–N1: p95 < 3 s | M |
| RNF-03 | **Desempenho** | Resposta completa em tempo aceitável para um chat | N0–N4: p95 < 25 s, com feedback de progresso | M |
| RNF-04 | **Custo** | A maior parte das checagens é resolvida sem LLM | ≥ 60% das checagens resolvidas até N3 | S |
| RNF-05 | **Custo** | Custo de LLM previsível | Teto de gastos por dia configurável; ao atingir, entra o modo econômico | S |
| RNF-06 | **Qualidade do modelo** | Desempenho mínimo no dataset de avaliação | F1 macro ≥ 0,80 (Fake.Br) na versão do MVP | M |
| RNF-07 | **Calibração** | A porcentagem significa o que diz | Erro de calibração (ECE) ≤ 0,15 | C |
| RNF-08 | **Acessibilidade** | Interface acessível apesar das animações | WCAG 2.1 AA; `prefers-reduced-motion` desliga animações; contraste ≥ 4,5:1 | M |
| RNF-09 | **Acessibilidade** | O resultado não depende só de cor | Rótulo textual sempre junto da cor da faixa | M |
| RNF-10 | **Responsividade** | Funciona no celular | Layout utilizável a partir de 360 px | M |
| RNF-11 | **Privacidade (LGPD)** | Dados mínimos do usuário | Histórico anônimo por padrão; nenhum dado pessoal enviado à LLM | M |
| RNF-12 | **Segurança** | Resistência a *prompt injection* vinda das páginas analisadas | Conteúdo extraído vai como dado delimitado, nunca como instrução; testes com páginas maliciosas | M |
| RNF-13 | **Segurança** | Extensão com permissões mínimas | Só `activeTab`, `contextMenus` e `storage`; sem acesso a todas as páginas por padrão | S |
| RNF-14 | **Ética de scraping** | Coleta responsável | Respeitar `robots.txt`, limitar a taxa de requisições, identificar o *user-agent* | M |
| RNF-15 | **Disponibilidade** | Degradação graciosa | Se uma API externa ou a LLM falhar, a Vera responde com as camadas disponíveis e avisa | S |
| RNF-16 | **Idioma** | Foco em português do Brasil | Modelos e léxicos avaliados em PT-BR | M |
| RNF-17 | **Observabilidade** | Rastreabilidade de cada checagem | Log por checagem: camadas executadas, sinais, tempo e custo | S |
| RNF-18 | **Manutenibilidade** | Pesos e limiares configuráveis sem alterar código | Pesos em arquivo de configuração versionado | S |
| RNF-19 | **Compatibilidade** | Navegadores suportados pela extensão | Chrome e Edge (Manifest V3); Firefox depois do MVP | S |
| RNF-20 | **Identidade** | Experiência totalmente tematizada | Todos os estados da interface com a identidade da Vera (validação em teste de usabilidade) | S |
