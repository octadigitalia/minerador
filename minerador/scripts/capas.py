#!/usr/bin/env python3
"""YouTube: baixa as capas dos videos selecionados, mede e monta folhas de contato.

Uso:
  capas.py <pasta> <id>[:razao] <id>[:razao] ...
  capas.py <pasta> --ids-file ids.txt          (um id[:razao] por linha)
  capas.py <pasta> --local                     (usa o que ja esta em <pasta>/_tmp/capas/<id>.jpg)

Saidas:
  <pasta>/folhas/capas_01.jpg ...   folhas com 8 capas, id e razao escritos em cima (Rota A: o modelo olha com Read)
  <pasta>/metricas_capas.csv        uma linha por capa
  stdout                            tabela objetiva (cores, brilho, contraste, saturacao, texto OCR e tamanho)
Codigo de saida 3 = rede bloqueada (nenhuma capa baixou): use o workbench do Composio (Rota C do carrossel.md).
"""
import sys, os, csv, urllib.request, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageStat
import slides as S

def baixar(ids, destino):
    ok, erros = [], []
    for i in ids:
        p = os.path.join(destino, f"{i}.jpg")
        for nome in ("maxresdefault", "hqdefault"):
            try:
                req = urllib.request.Request(f"https://i.ytimg.com/vi/{i}/{nome}.jpg", headers={"User-Agent": S.UA})
                with urllib.request.urlopen(req, timeout=25) as r:
                    open(p, "wb").write(r.read())
                ok.append(i); break
            except Exception as e:
                ultimo = f"{i}: {e}"
        else:
            erros.append(ultimo)
    return ok, erros

def folhas(itens, pasta, por_folha=8, larg=480):
    os.makedirs(os.path.join(pasta, "folhas"), exist_ok=True)
    out = []
    for n in range(0, len(itens), por_folha):
        lote = itens[n:n + por_folha]
        cel = []
        for i, razao, im in lote:
            t = im.convert("RGB").resize((larg, int(im.height * larg / im.width)))
            c = Image.new("RGB", (larg, t.height + 26), (20, 20, 20))
            c.paste(t, (0, 26))
            ImageDraw.Draw(c).text((6, 6), f"{i}  outlier {razao}", fill=(255, 255, 255))
            cel.append(c)
        cols = 4
        linhas = [cel[k:k + cols] for k in range(0, len(cel), cols)]
        alt = sum(max(c.height for c in l) for l in linhas) + 8 * (len(linhas) + 1)
        sh = Image.new("RGB", (cols * larg + 8 * (cols + 1), alt), (40, 40, 40))
        y = 8
        for l in linhas:
            x = 8
            for c in l:
                sh.paste(c, (x, y)); x += larg + 8
            y += max(c.height for c in l) + 8
        f = os.path.join(pasta, "folhas", f"capas_{n // por_folha + 1:02d}.jpg")
        sh.save(f, quality=82); out.append(f)
    return out

def main():
    a = sys.argv[1:]
    if len(a) < 2: sys.exit(__doc__)
    pasta = a[0]
    tmp = os.path.join(pasta, "_tmp", "capas"); os.makedirs(tmp, exist_ok=True)
    if a[1] == "--local":
        pares = [(f[:-4], "") for f in sorted(os.listdir(tmp)) if f.endswith(".jpg")]
        erros = []
    else:
        brutos = open(a[2]).read().split() if a[1] == "--ids-file" else a[1:]
        pares = [(x.split(":")[0], x.split(":")[1] if ":" in x else "") for x in brutos]
        ok, erros = baixar([p[0] for p in pares], tmp)
        pares = [p for p in pares if p[0] in ok]
    if not pares:
        print("REDE_BLOQUEADA: nenhuma capa baixou. Use o workbench do Composio (Rota C).")
        for e in erros[:3]: print(" ", e)
        sys.exit(3)
    itens, linhas = [], []
    print("id | outlier | cores dominantes | brilho | contraste | saturacao | palavras | maior texto | texto OCR")
    for i, razao in pares:
        im = Image.open(os.path.join(tmp, f"{i}.jpg")).convert("RGB")
        im.thumbnail((960, 960))
        itens.append((i, razao, im))
        lum = ImageStat.Stat(im.convert("L"))
        sat = ImageStat.Stat(im.convert("HSV")).mean[1]
        pal = S.paleta(im)
        o = S.ocr(im) if S.OCR else dict(texto="", palavras=0, maior=0)
        cores = " ".join(f"{S.hexcor(c)}({p:.0%})" for c, p in pal[:3])
        txt = o["texto"].replace("\n", " / ")
        print(f"{i} | {razao} | {cores} | {lum.mean[0]:.0f} | {lum.stddev[0]:.0f} | {sat:.0f} | {o['palavras']} | {o['maior']:.1%} | {txt}")
        linhas.append([i, razao, cores, round(lum.mean[0]), round(lum.stddev[0]), round(sat), o["palavras"], round(o["maior"], 3), txt])
    with open(os.path.join(pasta, "metricas_capas.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["id", "outlier", "cores", "brilho", "contraste", "saturacao", "palavras", "maior_texto", "ocr"]); w.writerows(linhas)
    fs = folhas(itens, pasta)
    if erros: print("falhas:", "; ".join(erros))
    print("(medidas objetivas; rosto, expressao e enquadramento so entram com leitura visual das folhas)")
    print("folhas:", ", ".join(fs))

if __name__ == "__main__":
    main()
