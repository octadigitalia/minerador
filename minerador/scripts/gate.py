#!/usr/bin/env python3
"""Portoes de qualidade.

  gate.py cobertura <pasta>             le termos_contas.tsv (rodada grupo termo conta)
  gate.py fichas <pasta> [--carrossel]  confere selecao.tsv contra fichas/<id>.md
"""
import sys, os, csv, re, unicodedata
from collections import Counter, defaultdict

COMUM = ["Encaixe", "Alcance", "Foco da conta", "Destino do CTA", "Comentarios", "Por que funcionou"]
SECOES_VIDEO = ["Gancho", "Promessa", "Estrutura", "Legenda"] + COMUM
SECOES_CARROSSEL = ["Gancho", "Promessa", "Slide a slide", "Legenda", "Analise visual"] + COMUM
SECOES_YOUTUBE = ["Gancho", "Promessa", "Estrutura", "Retencao", "Titulo", "Capa"] + COMUM

def norm(t):
    return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))

def cobertura(pasta):
    p = os.path.join(pasta, "termos_contas.tsv")
    rows = [r for r in csv.reader(open(p, encoding="utf-8"), delimiter="\t") if len(r) >= 4]
    contas_por_termo = defaultdict(set)
    todas = set()
    rodadas = defaultdict(set)
    for rod, grupo, termo, conta in rows:
        contas_por_termo[termo].add(conta)
        todas.add(conta)
        rodadas[rod].add(conta)
    if not todas:
        sys.exit("termos_contas.tsv vazio")
    ordem = sorted(rodadas, key=lambda x: (len(x), x))
    anteriores = set()
    novas_ultima = 0
    for rod in ordem[:-1]:
        anteriores |= rodadas[rod]
    ult = rodadas[ordem[-1]]
    novas_ultima = len(ult - anteriores) / max(len(ult), 1) if len(ordem) > 1 else 1.0
    # expansao por contas similares nao conta como termo (nao e busca por palavra)
    cand = {t: c for t, c in contas_por_termo.items() if not norm(t).startswith("similar")}
    topo = max((cand or contas_por_termo).items(), key=lambda kv: len(kv[1]))
    share = len(topo[1]) / len(todas)
    print(f"contas unicas: {len(todas)} | termos: {len(contas_por_termo)} | rodadas: {len(ordem)}")
    print(f"maior termo: '{topo[0]}' gera {share:.0%} das contas (limite 40%) -> {'OK' if share <= .40 else 'FALHA'}")
    print(f"contas novas na ultima rodada: {novas_ultima:.0%} (limite 15%) -> {'OK' if novas_ultima < .15 else 'FALHA'}")
    sys.exit(0 if (share <= .40 and novas_ultima < .15) else 2)

def fichas(pasta, carrossel):
    sel = [r for r in csv.reader(open(os.path.join(pasta, "selecao.tsv"), encoding="utf-8"), delimiter="\t") if len(r) >= 4]
    faltam, incompletas, ok = [], [], []
    contas = defaultdict(set)
    n_carr = 0
    for r in sel:
        rede, fmt, conta, id_ = r[0], r[1], r[2], r[3]
        slug = re.sub(r"[^A-Za-z0-9_-]", "_", id_.rstrip("/").split("/")[-1])
        f = os.path.join(pasta, "fichas", slug + ".md")
        if not os.path.exists(f):
            faltam.append(slug); continue
        txt = norm(open(f, encoding="utf-8").read())
        secoes = SECOES_YOUTUBE if rede == "youtube" else (SECOES_CARROSSEL if fmt == "carrossel" else SECOES_VIDEO)
        vazias = []
        for s in secoes:
            m = re.search(r"^#{1,4}\s*" + re.escape(s) + r"[^\n]*\n(.*?)(?=^#{1,4}\s|\Z)", txt, re.S | re.M | re.I)
            if not m or len(m.group(1).strip()) < 15:
                vazias.append(s)
        if vazias:
            incompletas.append((slug, vazias)); continue
        ok.append(slug); contas[rede].add(conta)
        n_carr += fmt == "carrossel"
    print(f"fichas completas: {len(ok)}/{len(sel)}")
    if faltam: print("sem ficha:", ", ".join(faltam))
    for s, v in incompletas: print(f"incompleta {s}: faltam {', '.join(v)}")
    falha = bool(faltam or incompletas)
    for rede, cs in contas.items():
        if len(cs) < 2:
            print(f"FALHA: {rede} tem so {len(cs)} conta(s) com ficha completa (minimo 2)"); falha = True
    if carrossel and n_carr < 2:
        print(f"FALHA: carrosseis completos: {n_carr} (minimo 2)"); falha = True
    print("GATE:", "FALHOU" if falha else "OK")
    sys.exit(2 if falha else 0)

if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit(__doc__)
    if sys.argv[1] == "cobertura": cobertura(sys.argv[2])
    elif sys.argv[1] == "fichas": fichas(sys.argv[2], "--carrossel" in sys.argv)
    else: sys.exit(__doc__)
