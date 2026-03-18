#!/usr/bin/env python3
"""
convert_v7.py — Extracteur haute-fidélité pour LiturgiCielauri
Utilise les délimiteurs binaires découverts (z•, zV, YoXXXX).
"""

import os
import re
import json

XOR_VAL = 0x5A

def decode_xor(in_path):
    if not os.path.exists(in_path): return None
    with open(in_path, 'rb') as f:
        data = f.read()
    return bytes(b ^ XOR_VAL for b in data)

def clean_text(text):
    if not text: return ""
    # Remove known binary tags while preserving following text
    # Tags like \8T, \PT, \PC, \PS followed by meta-info
    text = re.sub(r'\\8T[0-9]+', ' ', text)
    text = re.sub(r'\\PT', ' ', text)
    text = re.sub(r'\\PC', ' ', text)
    text = re.sub(r'\\PS', ' ', text)
    
    # Remove complex FileMaker structural patterns
    text = re.sub(r'S⁄TbT⁄J\][0-9]+T⁄O\][0-9]*', ' ', text)
    text = re.sub(r'T⁄<\][0-9]+', ' ', text)
    text = re.sub(r'S⁄\*1X¶\[.*?z', ' ', text)
    text = re.sub(r'[A-Za-z]⁄\\_[A-Z][0-9]+', ' ', text)
    
    # Standard cleanup
    text = re.sub(r'Z{2,}', ' ', text)
    text = "".join(c for c in text if ord(c) >= 32 or c in '\n\r\t')
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def extract_v7(data):
    db = []
    # Support multiple prefixes like Yo, Xo, Zo
    pattern = re.compile(br'([A-Z]o)([0-9]{1,4})')
    
    matches = list(pattern.finditer(data))
    print(f"🔍 {len(matches)} ancres identifiées.")

    for i, m in enumerate(matches):
        prefix = m.group(1).decode('ascii')
        idx = m.group(2).decode('ascii')
        
        # Déterminer le bloc de données (entre deux ancres)
        start = matches[i-1].end() if i > 0 else 0
        end = m.start()
        chunk_raw = data[start:end]
        
        # On ne traite que si le bloc est assez gros
        if len(chunk_raw) < 50: continue
        
        text = chunk_raw.decode('mac_roman', errors='replace')
        
        # Séparation par les délimiteurs FileMaker habituels (z + char spécial)
        # On utilise une regex qui splittent sur les séquences de contrôle
        parts = re.split(r'z[\x00-\x7F]⁄\\+\[', text)
        
        # Nettoyage des segments
        cleaned_parts = [clean_text(p) for p in parts if len(clean_text(p)) > 1]
        
        if not cleaned_parts: continue
        
        # Tentative de mappage intelligent basé sur la structure observée
        # 1. Le titre est souvent la première partie longue
        # 2. Les auteurs / source suivent
        # 3. Le contenu est la partie la plus longue
        
        record = {
            "id": idx,
            "brut": cleaned_parts,
            "titre": "",
            "auteurs": "",
            "source": "",
            "categorie": "",
            "contenu": ""
        }
        
        if len(cleaned_parts) >= 1: record["titre"] = cleaned_parts[0]
        if len(cleaned_parts) >= 2: record["auteurs"] = cleaned_parts[1]
        
        # Le contenu est généralement le bloc le plus gros
        record["contenu"] = max(cleaned_parts, key=len)
        
        # On essaie d'extraire la categorie (souvent une partie courte)
        shorts = [p for p in cleaned_parts if len(p) < 50 and p != record["titre"]]
        if shorts: record["categorie"] = shorts[0]

        db.append(record)
        
    return db

def main():
    source_dir = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN"
    target_file = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN/LiturgiCielauri/scripts/fiches_v7.json"
    
    all_data = []
    for fname in ["Fiches.lit"]:
        path = os.path.join(source_dir, fname)
        print(f"📖 Traitement de {fname}...")
        data = decode_xor(path)
        if data:
            fiches = extract_v7(data)
            all_data.extend(fiches)
        
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
        
    print(f"✨ Succès : {len(all_data)} fiches extraites dans {target_file}")

if __name__ == "__main__":
    main()
