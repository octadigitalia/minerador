#!/usr/bin/env python3
"""Apaga temporarios da execucao (slides baixados, cache). Uso: cleanup.py <pasta> [--manter-folhas]"""
import sys, os, shutil
pasta = sys.argv[1]
tmp = os.path.join(pasta, "_tmp")
apagados = 0
if os.path.isdir(tmp):
    for raiz, _, arqs in os.walk(tmp):
        apagados += len(arqs)
    shutil.rmtree(tmp)
print(f"removidos {apagados} arquivos temporarios de {tmp}")
