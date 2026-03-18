#!/usr/bin/env python3
"""Analyse Echanges.lit pour trouver le texte complet exporté."""
import re
import os
from typing import List, Set

XOR = 0x5A
SRC = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN/Echanges.lit"

print(f"Taille: {os.path.getsize(SRC)//1024} Ko")

with open(SRC, 'rb') as f:
    raw = f.read()

xored = bytes(b ^ XOR for b in raw)


def make_snippet(text: str, pos: int, before: int = 100, after: int = 400) -> str:
    start = max(0, pos - before)
    end = pos + after
    chunk: str = text[start:end]  # type: ignore[index]
    return ''.join(c if ord(c) >= 32 else '\u00b7' for c in chunk)  # type: ignore[misc]


for label, data in [("RAW", raw), ("XOR", xored)]:
    text: str = data.decode('mac_roman', errors='replace')

    # Chercher le texte visible dans le screenshot
    for needle in ["Jeu d'orgue", "assembl\u00e9e se recueille", "Seigneur : tu es", "D'apr\u00e8s Singer"]:
        pos = text.find(needle)
        if pos >= 0:
            snippet = make_snippet(text, pos)
            print(f"\n\u2705 [{label}] '{needle}' \u00e0 pos={pos} (bloc #{pos//4096}):")
            print(snippet[:400])  # type: ignore[index]
            break
    else:
        ids: List[str] = re.findall(r'Yo[0-9]{4}', text)  # type: ignore[assignment]
        print(f"[{label}] texte non trouv\u00e9. IDs Yo: {len(ids)}")

    # Compter les enregistrements
    yo_ids: Set[str] = set(re.findall(r'Yo([0-9]{4})', text))  # type: ignore[assignment]
    if yo_ids:
        top10: List[str] = list(sorted(yo_ids))[:10]  # type: ignore[index]
        print(f"[{label}] IDs Yo trouv\u00e9s: {top10}... total={len(yo_ids)}")
