#!/usr/bin/env python3
"""
extract_texts.py — Extracteur de contenu textuel dense pour Sauvegarde.lit.
Scanne le binaire Sauvegarde.lit et extrait les blocs de texte liturgique.
"""

import os
import re
import json

XOR_VAL = 0x5A

def decode_mac_roman(b_data):
    return b_data.decode('mac_roman', errors='replace')

def clean_text(text):
    if not text: return ""
    # Supprime les séquences techniques [u1[j1 etc.
    text = re.sub(r'\[[a-z][0-9]', ' ', text)
    # Supprime les répétitions de Z
    text = re.sub(r'Z{2,}', ' ', text)
    # Garde les imprimables
    text = "".join(c for c in text if ord(c) >= 32 or c in '\n\r\t')
    return re.sub(r'\s{2,}', ' ', text).strip()

def main():
    source_file = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN/Sauvegarde.lit"
    target_file = "sauvegarde_texts.json"
    
    if not os.path.exists(source_file):
        print("Fichier non trouvé.")
        return

    with open(source_file, 'rb') as f:
        data = f.read()
    
    # XOR 0x5A
    decoded = bytes(b ^ XOR_VAL for b in data)
    text_full = decode_mac_roman(decoded)
    
    # On cherche des blocs de texte long délimités par du "bruit" binaire
    # Un bloc liturgique est typiquement > 100 caractères
    blocks = re.split(r'[\x00-\x1f\x7f-\x9f\xad\xbc\xbe\xda\xbf\xca\xa2\xa1\xa6\xb9]{2,}', text_full)
    
    extracted = []
    for b in blocks:
        cleaned = clean_text(b)
        if len(cleaned) > 100: # Seuil pour une prière ou un chant
            # On cherche si un ID Yo est à proximité (dans les 1000 char précédents du bloc brute)
            # Mais souvent les blocs sont groupés.
            extracted.append(cleaned)
            
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(extracted, f, indent=2, ensure_ascii=False)
        
    print(f"✨ {len(extracted)} blocs de texte liturgique extraits dans {target_file}")

if __name__ == "__main__":
    main()
