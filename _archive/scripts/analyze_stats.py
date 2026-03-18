#!/usr/bin/env python3
"""
analyze_stats.py — Analyse de la densité textuelle du binaire décodé.
Objectif : Identifier tous les blocs de texte liturgique indépendamment des IDs Yo.
"""

import os
import re

XOR_VAL = 0x5A

def decode_mac_roman(b_data):
    return b_data.decode('mac_roman', errors='replace')

def get_text_density(chunk):
    """Calcule le % de caractères imprimables MacRoman dans un chunk."""
    if not chunk: return 0
    printable = sum(1 for b in chunk if (b >= 32 and b <= 126) or (b >= 128))
    return printable / len(chunk)

def main():
    source_file = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN/Sauvegarde.lit"
    if not os.path.exists(source_file):
        print("Fichier non trouvé.")
        return

    with open(source_file, 'rb') as f:
        data = f.read()
    
    # XOR 0x5A
    decoded = bytes(b ^ XOR_VAL for b in data)
    
    chunk_size = 1024
    print(f"Index | Densité | Extrait")
    print("-" * 40)
    
    for i in range(0, len(decoded), chunk_size):
        chunk = decoded[i:i+chunk_size]
        density = get_text_density(chunk)
        if density > 0.7:  # Seuil de texte dense
            text = decode_mac_roman(chunk[:100]).replace("\n", " ")
            print(f"{i:8d} | {density:.2f} | {text}")

if __name__ == "__main__":
    main()
