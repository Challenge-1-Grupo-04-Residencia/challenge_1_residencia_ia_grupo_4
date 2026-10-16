/**
 * Página inicial.
 *
 * O chat fica **aqui**, e não atrás de um link. A tela de entrada sem a caixa de
 * texto obrigava quem chegou com uma dúvida — que é a razão de a pessoa estar
 * aqui — a reconhecer um botão e navegar para outra tela antes de poder
 * perguntar.
 *
 * Quem decide o que aparece é `TelaInicial`, do lado do cliente: a abertura em
 * quadrinhos na primeira visita, depois a apresentação com o chat, e o chat
 * sozinho a partir da primeira pergunta.
 *
 * `/checar` continua existindo, com a mesma conversa sem a abertura, para quem
 * chega por link direto ou com `?q=`.
 */

import { TelaInicial } from "@/components/home/TelaInicial";

export default function Home() {
  return <TelaInicial />;
}
