#!/usr/bin/env python3
"""
extract_liturgy.py — Extracteur de "Textes Sacrés" par densité linguistique.
Objectif : Récupérer toutes les prières et chants de Sauvegarde.lit.
"""

import os
import re
import json

XOR_VAL = 0x5A

def decode_mac_roman(b_data):
    return b_data.decode('mac_roman', errors='replace')

def clean(text):
    text = re.sub(r'\[[a-z][0-9]', ' ', text)
    text = re.sub(r'Z{2,}', ' ', text)
    text = "".join(c for c in text if ord(c) >= 32 or c in '\n\r\t')
    return re.sub(r'\s{2,}', ' ', text).strip()

def is_liturgical(text):
    """Vérifie si le texte ressemble à une prière ou un chant français."""
    text_l = text.lower()
    keywords = ["seigneur", "père", "dieu", " christ", "amen", "esprit", "bénis", "grâce", "foi", "saint"]
    count = sum(1 for k in keywords if k in text_l)
    # Une prière a souvent plusieurs de ces mots
    return count >= 2 and len(text) > 150

def main():
    source = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN/Sauvegarde.lit"
    if not os.path.exists(source): return
    
    with open(source, 'rb') as f:
        data = f.read()
    
    decoded = bytes(b ^ XOR_VAL for b in data)
    text_full = decode_mac_roman(decoded)
    
    # Segmentation par blocs de ponctuation et sauts de ligne
    # Les textes liturgiques sont souvent séparés par des caractères de contrôle \x1e, \x00, etc.
    blocks = re.split(r'[\x00-\x1f\x7f-\x9f]{1,}', text_full)
    
    liturgy = []
    seen = set()
    
    for b in blocks:
        cleaned = clean(b)
        if is_liturgical(cleaned):
            # Dédoublonnage par préfixe
            prefix = cleaned[:100]
            if prefix not in seen:
                seen.add(prefix)
                liturgy.append(cleaned)
                
    with open("liturgy_content.json", "w", encoding="utf-8") as f:
        json.dump(liturgy, f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(liturgy)} textes liturgiques (prières/chants) extraits.")

if __name__ == "__main__":
    main()
