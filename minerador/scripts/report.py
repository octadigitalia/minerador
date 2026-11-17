#!/usr/bin/env python3
"""Gera pesquisa.pdf a partir da pasta da pesquisa.

Uso: report.py <pasta> [--titulo "Nicho"]
Le: padroes.md, selecao.tsv, folhas/*.jpg (opcional). Escreve: pesquisa.pdf
Markdown aceito em padroes.md: #, ##, ###, listas com - ou *, **negrito**, paragrafos.
"""
import sys, os, re, csv, glob, html
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.utils import ImageReader

def limpa(t):
    t = t.replace("—", ",").replace("–", "-").replace("▸", ">")
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`(.+?)`", r"<font face='Courier'>\1</font>", t)
    return t.encode("cp1252", "replace").decode("cp1252")

def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    pasta = sys.argv[1]
    titulo = sys.argv[sys.argv.index("--titulo") + 1] if "--titulo" in sys.argv else os.path.basename(os.path.abspath(pasta))
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Heading1"], fontSize=20, spaceAfter=10)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=14, spaceBefore=12, spaceAfter=6)
    h3 = ParagraphStyle("h3", parent=ss["Heading3"], fontSize=11, spaceBefore=8, spaceAfter=4)
    body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=9.5, leading=13)
    small = ParagraphStyle("s", parent=body, fontSize=7.5, leading=9)
    el = [Paragraph(limpa("Minerador: " + titulo), h1)]

    p = os.path.join(pasta, "padroes.md")
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8").read().splitlines():
            s = ln.strip()
            if not s: el.append(Spacer(1, 4)); continue
            if s.startswith("### "): el.append(Paragraph(limpa(s[4:]), h3))
            elif s.startswith("## "): el.append(Paragraph(limpa(s[3:]), h2))
            elif s.startswith("# "): el.append(Paragraph(limpa(s[2:]), h2))
            elif s[:2] in ("- ", "* "): el.append(Paragraph("&bull; " + limpa(s[2:]), body))
            else: el.append(Paragraph(limpa(s), body))

    sp = os.path.join(pasta, "selecao.tsv")
    if os.path.exists(sp):
        el += [PageBreak(), Paragraph("Itens analisados", h2)]
        rows = [["Rede", "Formato", "Conta", "Id", "Metrica", "Razao", "Papel"]]
        for r in csv.reader(open(sp, encoding="utf-8"), delimiter="\t"):
            if len(r) >= 6:
                rows.append([r[0], r[1], r[2], r[3].rstrip("/").split("/")[-1][:22], r[4], r[5], r[12] if len(r) > 12 else ""])
        data = [[Paragraph(limpa(str(c)), small) for c in row] for row in rows]
        t = Table(data, repeatRows=1, colWidths=[1.6*cm, 1.8*cm, 3.2*cm, 4.2*cm, 2*cm, 1.4*cm, 2*cm])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8")),
                               ("GRID", (0, 0), (-1, -1), 0.25, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        el.append(t)

    folhas = sorted(glob.glob(os.path.join(pasta, "folhas", "*.jpg")))
    if folhas:
        el += [PageBreak(), Paragraph("Carrosseis analisados (folhas de contato)", h2)]
        for f in folhas:
            w, h = ImageReader(f).getSize()
            lw = 17 * cm
            el += [Paragraph(limpa(os.path.basename(f)[:-4]), h3), Image(f, width=lw, height=lw * h / w), Spacer(1, 8)]

    out = os.path.join(pasta, "pesquisa.pdf")
    SimpleDocTemplate(out, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm,
                      title="Minerador: " + titulo).build(el)
    print("gerado:", out)

if __name__ == "__main__":
    main()
