#!/usr/bin/env python3
"""Analyse détaillée de la zone de données d'Echanges.lit autour de pos=410906"""
import re, os

XOR = 0x5A
SRC = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN/Echanges.lit"

with open(SRC, 'rb') as f:
    raw = f.read()

data = bytes(b ^ XOR for b in raw)
text = data.decode('mac_roman', errors='replace')

# Chercher toutes les occurrences de 'EERV' et voir le contexte autour
print("=== Contexte autour de 'EERV' (3 premières occurrences) ===")
for i, m in enumerate(re.finditer('EERV', text)):
    if i >= 3: break
    pos = m.start()
    chunk = text[max(0,pos-200):pos+300]
    chunk = ''.join(c if ord(c)>=32 else '·' for c in chunk)
    print(f"\n[{i+1}] pos={pos}:")
    print(chunk)

# Chercher auteur markers \[w
print("\n\n=== Auteurs (\\[w) ===")
for i, m in enumerate(re.finditer(r'\\\[w', text)):
    if i >= 5: break
    pos = m.start()
    chunk = text[pos:pos+100]
    chunk = ''.join(c if ord(c)>=32 else '·' for c in chunk)
    print(f"  [{i+1}] pos={pos}: {chunk}")

# Regarder les blocs de texte lisible dans la zone 380000-500000
print("\n\n=== Blocs de texte dans la zone data (380000-480000) ===")
zone = text[380000:480000]
zone_clean = ''.join(c if ord(c)>=32 or c in '\n\r' else '\x00' for c in zone)
blocks = [(m.start()+380000, m.group()) for m in re.finditer(r'[^\x00]{30,}', zone_clean)]
print(f"Blocs trouvés: {len(blocks)}")
for start, content in blocks[:25]:
    c = ''.join(c if ord(c)>=32 else '·' for c in content[:150])
    if any(ord(ch) > 127 for ch in content[:50]):  # Texte avec accents = français probable
        print(f"  [{start:8d}] *** {c[:150]}")
    else:
        print(f"  [{start:8d}]     {c[:80]}")
