# O Desafio (CBL)

A fase **Engage** parte de um conceito amplo e afunila, por meio de questionamento,
até um desafio concreto, pessoal e acionável. Os três pilares definidos pela equipe:

## Big Idea

> Em um mundo com excesso de informação, como distinguir fatos, evidências e opiniões?
> A IA pode apoiar a investigação da confiabilidade das informações, fortalecendo o
> pensamento crítico em vez de substituí-lo.

## Essential Question

> Como sistemas de IA podem ajudar as pessoas a avaliar a confiabilidade de informações
> **sem substituir seu pensamento crítico**?

## Challenge

> Construir uma solução/protótipo com suporte de IA que atue de forma **transparente**
> na detecção de desinformação e **explique seus critérios** para o usuário.

A resposta do grupo ao Challenge é a [**Senhora Vera**](produto/vera.md).

## Guiding Questions

No CBL tradicional as Guiding Questions marcam a transição para a fase de Investigação.
Conforme o roteiro do desafio, foram elaboradas já como entrega da Semana 1 e guiarão a
pesquisa das Semanas 2 e 3.

### Fator humano

- Quais vieses cognitivos e psicológicos fazem com que as pessoas aceitem e compartilhem
  informações falsas com tanta facilidade?
- Que público é mais exposto (idosos, jovens, ativistas) e como cada um consome notícias?

### Tecnologia e IA

- De que maneira os avanços em inteligência artificial generativa aumentaram a
  complexidade e o realismo das campanhas de desinformação?
- Como sistemas de IA podem ajudar as pessoas a avaliar a confiabilidade de informações
  sem substituir seu pensamento?
- Quais critérios e evidências objetivas precisamos estabelecer para que uma ferramenta
  de IA auxilie na verificação de fatos sem anular o pensamento crítico humano?

### O que é e como identificar

- O que se classifica como uma fake news?
- Como uma fake news pode ser identificada? O que no texto entrega que algo é falso?
- Qual é a forma de escrita? O texto foi gerado por inteligência artificial?
- É plágio de outra fonte? As fontes usadas são corretas?

### Fontes e veículos

- Quais são os veículos confiáveis? Qual a credibilidade do veículo (empresa, universidade etc.)?
- Qual a data de criação do website? Qual a sua credibilidade recente?
- O veículo teve outras notícias falsas recentemente?
- Suas publicações são politicamente enviesadas?
- Quem é o autor? É jornalista formado? É enviesado?
- Se a fonte é um artigo científico: foi revisado por pares? Qual metodologia? Em que base foi publicado?
- Se a fonte é um website, ela também precisa ser checada por completo?

### Corroboração

- A mesma notícia está presente em outros sites? Outros sites a replicaram?
- Há quanto tempo a postagem está no ar?

### Solução

- É possível criar uma API que identifica se um veículo é confiável?
- Usar IA para resumir a notícia e buscar pontos incompatíveis?
- Fazer web scraping para descobrir a veracidade?
- Fazer etapas de classificação para poupar poder computacional e tempo?
- Que pesos cada critério deve ter?

As respostas propostas estão em [Classificação e pesos](produto/classificacao.md) e em
[Como a Vera funciona](produto/funcionamento.md). A pesquisa que as valida fica em
[Investigação](investigacao.md).

!!! note "Transparência como requisito, não como recurso"
    O Challenge exige que a solução atue de forma transparente. Isso descarta, por
    princípio, um classificador que apenas devolve "verdadeiro/falso" sem mostrar o
    caminho até a conclusão.
