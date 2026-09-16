# Regras de negócio

As regras de negócio valem para **todos os canais** (site, extensão e celular) e são
referenciadas pelos requisitos e critérios de aceite.

| ID | Regra |
| --- | --- |
| **RN-01** | Se houver checagem de agência signatária da IFCN sobre a alegação, o veredito da agência prevalece sobre o score calculado, e a agência é citada com link |
| **RN-02** | Domínio que imita um veículo conhecido (nome parecido, *typosquatting*) recebe `V ≤ 15` e um alerta de site impostor |
| **RN-03** | Opinião e sátira não recebem porcentagem de veracidade; a Vera explica a natureza do conteúdo |
| **RN-04** | Com confiança final `C < 0,5`, o resultado é **Inconclusivo** |
| **RN-05** | Todo resultado mostra **porcentagem, rótulo da faixa, principais sinais e fontes consultadas**. Resultado sem explicação não é exibido |
| **RN-06** | Sinais sem dado são **excluídos** do cálculo e não contam como zero |
| **RN-07** | A LLM (camada N4) só é chamada se as camadas N0 a N3 não atingirem a regra de parada |
| **RN-08** | Viés político, popularidade e formação do jornalista são **contexto**: aparecem na explicação e não alteram o score |
| **RN-09** | Checagens em cache valem por **7 dias** para notícias e **30 dias** para a reputação de domínios; depois disso são refeitas |
| **RN-10** | Uma notícia é contada no histórico de fakes de um domínio (S-02) só quando confirmada por RN-01 ou por revisão humana, nunca apenas pelo score da Vera |
| **RN-11** | O humor da persona nunca substitui a informação: frase temática e resultado técnico aparecem juntos |
| **RN-12** | A Vera não afirma certeza absoluta: os rótulos usam "provavelmente" e "confirmada **por fontes**" |
