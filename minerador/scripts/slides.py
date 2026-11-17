#!/usr/bin/env python3
"""Baixa os slides de um carrossel, monta a folha de contato e mede o design.

Uso:
  slides.py <pasta> <id> <url1> <url2> ...
  slides.py <pasta> <id> --urls-file urls.txt
  slides.py <pasta> <id> --local            (analisa o que ja esta em <pasta>/_tmp/<id>/)

Saidas:
  <pasta>/folhas/<id>.jpg   folha de contato (Rota A: o modelo olha esta imagem com Read)
  stdout                    texto OCR por slide + medidas objetivas (Rota B: so isto entra no contexto)
Codigo de saida 3 = rede bloqueada (nenhum slide baixou): rode este script no workbench do Composio.
Dependencias: Pillow (obrigatorio); pytesseract + tesseract (opcional, para texto e hierarquia).
"""
import sys, os, math, urllib.request, urllib.error, statistics, warnings
warnings.filterwarnings("ignore")
from PIL import Image, ImageStat

try:
    import pytesseract
    pytesseract.get_tesseract_version()
    OCR = True
except Exception:
    OCR = False

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

def baixar(urls, destino):
    ok, erros = [], []
    for i, u in enumerate(urls, 1):
        p = os.path.join(destino, f"slide_{i:02d}.jpg")
        try:
            req = urllib.request.Request(u, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=25) as r:
                open(p, "wb").write(r.read())
            ok.append(p)
        except Exception as e:
            erros.append(f"slide {i}: {e}")
    return ok, erros

def hexcor(c): return "#%02x%02x%02x" % c

def paleta(img, k=4):
    pq = img.convert("RGB").resize((96, 96)).quantize(k, method=Image.Quantize.MEDIANCUT)
    pal = pq.getpalette()[: k * 3]
    cont = sorted(pq.getcolors(), reverse=True)
    out = []
    tot = 96 * 96
    for n, idx in cont:
        out.append((tuple(pal[idx * 3: idx * 3 + 3]), n / tot))
    return out

def entropia(img):
    g = img.convert("RGB").resize((128, 128))
    h = {}
    for px in g.getdata():
        k = (px[0] >> 5, px[1] >> 5, px[2] >> 5)
        h[k] = h.get(k, 0) + 1
    n = 128 * 128
    return -sum((v / n) * math.log2(v / n) for v in h.values())

def rotulo_visual(e):
    return "plano/grafico" if e < 2.5 else ("misto" if e < 4.0 else "fotografico")

def ocr(img):
    W, H = img.size
    lang = "por+eng"
    try:
        d = pytesseract.image_to_data(img.convert("RGB"), lang=lang, output_type=pytesseract.Output.DICT)
    except Exception:
        d = pytesseract.image_to_data(img.convert("RGB"), output_type=pytesseract.Output.DICT)
    palavras, alturas, area, cx, cy = [], [], 0, [], []
    linhas = {}
    for i, t in enumerate(d["text"]):
        t = t.strip()
        try:
            conf = float(d["conf"][i])
        except Exception:
            conf = -1
        if not t or conf < 40:
            continue
        w, h, x, y = d["width"][i], d["height"][i], d["left"][i], d["top"][i]
        palavras.append(t); alturas.append(h); area += w * h
        cx.append((x + w / 2) / W); cy.append((y + h / 2) / H)
        linhas.setdefault((d["block_num"][i], d["par_num"][i], d["line_num"][i]), []).append(t)
    texto = "\n".join(" ".join(v) for _, v in sorted(linhas.items()))
    if not palavras:
        return dict(texto="", palavras=0, area=0, maior=0, mediana=0, hier=0, cx=None, cy=None)
    alturas_s = sorted(alturas)
    mediana = statistics.median(alturas_s)
    p90 = alturas_s[int(0.9 * (len(alturas_s) - 1))]
    return dict(texto=texto, palavras=len(palavras), area=area / (W * H), maior=max(alturas) / H,
                mediana=mediana / H, hier=(p90 / mediana if mediana else 0),
                cx=statistics.mean(cx), cy=statistics.mean(cy))

def folha(imgs, destino, por_linha=5, larg=540):
    thumbs = []
    for im in imgs:
        r = larg / im.width
        thumbs.append(im.convert("RGB").resize((larg, int(im.height * r))))
    linhas = [thumbs[i:i + por_linha] for i in range(0, len(thumbs), por_linha)]
    alt = sum(max(t.height for t in l) for l in linhas) + 8 * (len(linhas) + 1)
    larg_tot = por_linha * larg + 8 * (por_linha + 1) if len(thumbs) >= por_linha else len(thumbs) * larg + 8 * (len(thumbs) + 1)
    sheet = Image.new("RGB", (larg_tot, alt), (30, 30, 30))
    y = 8
    for l in linhas:
        x = 8
        for t in l:
            sheet.paste(t, (x, y)); x += larg + 8
        y += max(t.height for t in l) + 8
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    sheet.save(destino, quality=82)

def main():
    a = sys.argv[1:]
    if len(a) < 3: sys.exit(__doc__)
    pasta, id_ = a[0], a[1]
    tmp = os.path.join(pasta, "_tmp", id_)
    os.makedirs(tmp, exist_ok=True)
    if a[2] == "--local":
        arqs = sorted(os.path.join(tmp, f) for f in os.listdir(tmp) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))
        erros = []
    else:
        urls = open(a[3]).read().split() if a[2] == "--urls-file" else a[2:]
        arqs, erros = baixar(urls, tmp)
    if not arqs:
        print("REDE_BLOQUEADA: nenhum slide baixou. Rode este script no workbench do Composio.")
        for e in erros[:3]: print(" ", e)
        sys.exit(3)
    imgs = [Image.open(p) for p in arqs]
    folha(imgs, os.path.join(pasta, "folhas", f"{id_}.jpg"))

    print(f"# {id_}: {len(imgs)} slides, {imgs[0].width}x{imgs[0].height}"
          f" (razao {imgs[0].width / imgs[0].height:.2f}), OCR={'sim' if OCR else 'NAO (instale tesseract para texto e hierarquia)'}")
    if erros: print("falhas de download:", "; ".join(erros))
    print("slide | cores dominantes | brilho | contraste | visual | palavras | texto% | maior texto | hierarquia | centro(x,y)")
    dom, brilhos, centros_y, textos = [], [], [], []
    for i, im in enumerate(imgs, 1):
        rgb = im.convert("RGB")
        lum = rgb.convert("L")
        st = ImageStat.Stat(lum)
        pal = paleta(rgb)
        dom.append(pal[0][0]); brilhos.append(st.mean[0])
        e = entropia(rgb)
        o = ocr(rgb) if OCR else dict(texto="", palavras=0, area=0, maior=0, mediana=0, hier=0, cx=None, cy=None)
        textos.append(o["texto"])
        if o["cy"] is not None: centros_y.append(o["cy"])
        cores = " ".join(f"{hexcor(c)}({p:.0%})" for c, p in pal[:3])
        cxy = f"{o['cx']:.2f},{o['cy']:.2f}" if o["cx"] is not None else "-"
        print(f"{i} | {cores} | {st.mean[0]:.0f} | {st.stddev[0]:.0f} | {rotulo_visual(e)} | {o['palavras']} | {o['area']:.0%} | {o['maior']:.1%} | {o['hier']:.1f} | {cxy}")
    def dist(c1, c2): return math.sqrt(sum((x - y) ** 2 for x, y in zip(c1, c2)))
    pares = [dist(dom[i], dom[j]) for i in range(len(dom)) for j in range(i + 1, len(dom))]
    cons = 1 - (statistics.mean(pares) / 441.7) if pares else 1.0
    print(f"\nconsistencia de cor entre slides: {cons:.0%} | variacao de brilho: {statistics.pstdev(brilhos):.0f}"
          + (f" | variacao da posicao vertical do texto: {statistics.pstdev(centros_y):.2f}" if len(centros_y) > 1 else ""))
    print("(medidas objetivas; nao substituem a leitura visual da folha de contato)")
    if OCR:
        print("\n## Texto por slide (OCR)")
        for i, t in enumerate(textos, 1):
            print(f"[slide {i}]\n{t if t else '(sem texto detectado)'}")
    print(f"\nfolha de contato: {os.path.join(pasta, 'folhas', id_ + '.jpg')}")

if __name__ == "__main__":
    main()
