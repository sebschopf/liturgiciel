#!/usr/bin/env python3
"""Analyse la structure des délimiteurs de fiches dans Echanges.lit"""
import re, os

XOR = 0x5A
SRC = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN/Echanges.lit"

with open(SRC, 'rb') as f:
    raw = f.read()

data = bytes(b ^ XOR for b in raw)
text = data.decode('mac_roman', errors='replace')

# Remplacer les non-printables par \x00
clean = ''.join(c if ord(c) >= 32 or c in '\n\r' else '\x00' for c in text)

# Trouver tous les blocs de texte lisible (>= 40 chars)
blocks = [(m.start(), m.end(), m.group()) for m in re.finditer(r'[^\x00]{40,}', clean)]
print(f"Blocs de texte (>=40 chars): {len(blocks)}")

# Afficher les 20 premiers blocs avec leur position
print("\n--- 20 premiers blocs ---")
for start, end, content in blocks[:20]:
    c = ''.join(c if ord(c) >= 32 else '·' for c in content[:120])
    print(f"  [{start:8d}] {c[:120]}")

# Chercher les marqueurs de séparation entre blocs
# Regarder le binaire entre deux blocs de texte
print("\n--- Séparateurs entre blocs (hex) ---")
for i in range(min(5, len(blocks)-1)):
    end1 = blocks[i][1]
    start2 = blocks[i+1][0]
    sep_bytes = data[end1:start2]
    if 0 < len(sep_bytes) < 200:
        print(f"  Entre bloc {i} et {i+1}: {sep_bytes[:40].hex()} ({len(sep_bytes)} bytes)")

# Chercher des patterns répétitifs dans les séparateurs
# qui pourraient être des délimiteurs de fiches
print("\n--- Pattern de recherche ---")
# Dans FM Echanges, les fiches sont souvent séparées par des séquences spécifiques
for pattern in [b'\r\x00\r', b'\x00\x00\x00\x00', b'EEEE', b'ZZZ']:
    decoded_pattern = bytes(b ^ XOR for b in pattern)
    count = data.count(decoded_pattern)
    if count > 0:
        print(f"  Pattern {pattern!r} XOR={decoded_pattern.hex()}: {count} occurrences")

# Chercher dans les blocs de texte les marqueurs spécifiques au format Echanges
print("\n--- Marqueurs FM dans le texte ---")
for marker in [r'\\PF', r'\\PU', r'\\PV', r'\[cf', r'\[w', r'EERV', r'FEER']:
    matches = [m.start() for m in re.finditer(re.escape(marker), text)]
    if matches:
        print(f"  '{marker}': {len(matches)} fois")
