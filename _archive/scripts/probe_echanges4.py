#!/usr/bin/env python3
"""Context complet autour de la prière trouvée à pos=410906"""
import re, os

XOR = 0x5A
SRC = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN/Echanges.lit"

with open(SRC, 'rb') as f:
    raw = f.read()

data = bytes(b ^ XOR for b in raw)
text = data.decode('mac_roman', errors='replace')

def show(t, label=""):
    return ''.join(c if ord(c) >= 32 else f'[{ord(c):02x}]' for c in t)

# Contexte large autour du texte de prière
pos = 410906
print("=== 2000 chars avant le texte de prière ===")
chunk = text[pos-2000:pos+800]
print(show(chunk))

print("\n\n=== Chercher tous les '^[' (IDs de fiches) dans la zone 400000-450000 ===")
zone = text[400000:450000]
for m in re.finditer(r'\^\[([0-9]+\.[0-9]+)', zone):
    fid = m.group(1)
    start = m.start()
    context = zone[max(0,start-20):start+150]
    print(f"  [{400000+start:8d}] ^[{fid}: {show(context)[:150]}")
