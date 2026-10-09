"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { Avaliacao, listarAvaliacoesLote } from "@/lib/api";

export default function HistoricoAvaliacoesPage() {
  const [avaliacoes, setAvaliacoes] = useState<Avaliacao[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listarAvaliacoesLote()
      .then((data) => {
        setAvaliacoes(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Erro ao buscar histórico:", err);
        setLoading(false);
      });
  }, []);

  return (
    <main className="min-h-screen bg-papel p-8">
      <div className="mx-auto max-w-5xl">
        <header className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-serif text-tinta">
              Histórico de Avaliações em Lote (Auditoria)
            </h1>
            <p className="mt-2 text-tinta-2">
              Resultados das baterias de testes automatizados com datasets de benchmark.
            </p>
          </div>
          <Link
            href="/"
            className="rounded bg-tinta-3 px-4 py-2 text-sm text-papel hover:bg-tinta transition-colors"
          >
            Voltar para a Vera
          </Link>
        </header>

        {loading ? (
          <p className="text-tinta-2">Carregando métricas...</p>
        ) : avaliacoes.length === 0 ? (
          <div className="rounded-xl border border-borda bg-papel-2 p-8 text-center">
            <p className="text-tinta-2">Nenhuma avaliação encontrada.</p>
            <p className="text-sm text-tinta-3 mt-2">
              Rode o script <code>python scripts/avaliar_modelo.py --dataset fakewhatsapp-br</code> no terminal para gerar a primeira avaliação.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-borda bg-papel-2 shadow-sm">
            <table className="w-full text-left text-sm text-tinta">
              <thead className="border-b border-borda bg-papel-3/50 text-tinta-2">
                <tr>
                  <th className="px-6 py-4 font-medium">Data</th>
                  <th className="px-6 py-4 font-medium">Dataset</th>
                  <th className="px-6 py-4 font-medium">Amostras</th>
                  <th className="px-6 py-4 font-medium">Acurácia</th>
                  <th className="px-6 py-4 font-medium">Falsos Positivos</th>
                  <th className="px-6 py-4 font-medium">Inconclusivos</th>
                  <th className="px-6 py-4 font-medium">Latência Média</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-borda">
                {avaliacoes.map((av) => (
                  <tr key={av.id} className="hover:bg-papel/50 transition-colors">
                    <td className="px-6 py-4">
                      {new Date(av.data_execucao).toLocaleString("pt-BR")}
                    </td>
                    <td className="px-6 py-4 font-medium">{av.dataset}</td>
                    <td className="px-6 py-4">{av.qtd_amostras}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${av.acuracia >= 80 ? 'bg-verdadeira/10 text-verdadeira' : 'bg-falsa/10 text-falsa'}`}>
                        {av.acuracia}%
                      </span>
                    </td>
                    <td className="px-6 py-4">
                       <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${av.taxa_falsos_positivos <= 5 ? 'bg-verdadeira/10 text-verdadeira' : 'bg-falsa/10 text-falsa'}`}>
                        {av.taxa_falsos_positivos}%
                      </span>
                    </td>
                    <td className="px-6 py-4">{av.taxa_inconclusivos}%</td>
                    <td className="px-6 py-4">{av.tempo_medio_ms} ms</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </main>
  );
}
