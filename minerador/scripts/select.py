#!/usr/bin/env python3
"""Seleciona a amostra a partir de candidatos.tsv (sai do jq da etapa 2).

Colunas de candidatos.tsv (sem cabecalho):
rede formato conta id metrica razao mediana likes comentarios extra data legenda

Uso: select.py <pasta> [--n 30] [--max-por-conta 4]
Escreve <pasta>/selecao.tsv e imprime uma tabela curta (o que fica no contexto).
Regras: equilibra redes, reserva espaco para carrossel se existir, respeita o maximo por
conta, e inclui 1 contraste (razao < 1) por rede quando houver.
"""
import argparse, csv, sys, os
from collections import defaultdict, Counter

COLS = "rede formato conta id metrica razao mediana likes comentarios extra data legenda".split()

def load(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.reader(f, delimiter="\t"):
            if len(r) < 11:
                continue
            r = r + [""] * (12 - len(r))
            d = dict(zip(COLS, r[:12]))
            try:
                d["razao"] = float(d["razao"])
            except ValueError:
                continue
            rows.append(d)
    seen, out = set(), []
    for d in rows:
        k = (d["rede"], d["id"])
        if k not in seen:
            seen.add(k)
            out.append(d)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta")
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--max-por-conta", type=int, default=4)
    a = ap.parse_args()
    rows = load(os.path.join(a.pasta, "candidatos.tsv"))
    if not rows:
        sys.exit("candidatos.tsv vazio ou sem as 11 colunas esperadas")
    out_rows = [r for r in rows if r["razao"] >= 1]
    contr = [r for r in rows if r["razao"] < 1]
    out_rows.sort(key=lambda r: -r["razao"])

    redes = sorted({r["rede"] for r in out_rows})
    n_contr = min(len(redes), len(contr)) if contr else 0
    n_main = a.n - n_contr
    quota = {r: n_main // max(len(redes), 1) for r in redes}
    for r in redes[: n_main - sum(quota.values())]:
        quota[r] += 1

    por_conta = Counter()
    chosen = []
    # dentro de cada rede, intercala formatos para nao deixar carrossel de fora
    for rede in redes:
        pool = [r for r in out_rows if r["rede"] == rede]
        por_fmt = defaultdict(list)
        for r in pool:
            por_fmt[r["formato"]].append(r)
        fmts = sorted(por_fmt, key=lambda f: -len(por_fmt[f]))
        pesos = {f: (0.25 if f == "carrossel" else 1.0) for f in fmts}
        got = 0
        idx = {f: 0 for f in fmts}
        score = {f: 0.0 for f in fmts}
        while got < quota[rede]:
            cand = [f for f in fmts if idx[f] < len(por_fmt[f])]
            if not cand:
                break
            f = min(cand, key=lambda x: score[x] / pesos[x] if pesos[x] else 9e9)
            r = por_fmt[f][idx[f]]
            idx[f] += 1
            if por_conta[(rede, r["conta"])] >= a.max_por_conta:
                continue
            por_conta[(rede, r["conta"])] += 1
            chosen.append(r)
            score[f] += 1
            got += 1
    for rede in redes:
        c = [r for r in contr if r["rede"] == rede]
        if c and n_contr:
            c.sort(key=lambda r: r["razao"])
            x = dict(c[0]); x["extra"] = x["extra"]
            x["razao"] = c[0]["razao"]
            x["papel"] = "contraste"
            chosen.append(x)
    for r in chosen:
        r.setdefault("papel", "outlier")

    path = os.path.join(a.pasta, "selecao.tsv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        for r in chosen:
            w.writerow([r[c] for c in COLS] + [r["papel"]])
    print(f"selecao.tsv: {len(chosen)} itens de {len(rows)} candidatos")
    print("rede\tformato\tconta\tid\tmetrica\trazao\tpapel")
    for r in chosen:
        print("\t".join(str(r[c]) for c in ("rede", "formato", "conta", "id", "metrica", "razao", "papel")))
    resumo = Counter((r["rede"], r["formato"]) for r in chosen)
    print("distribuicao:", dict(resumo))
    if len(chosen) < a.n:
        print(f"AVISO: so {len(chosen)} itens atendem as regras (pedido: {a.n}). Rode mais descoberta ou aceite a amostra menor.")

if __name__ == "__main__":
    main()
