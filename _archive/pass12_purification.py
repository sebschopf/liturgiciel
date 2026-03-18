#!/usr/bin/env python3
"""
pass12_purification.py — PASSE 1.2 : Purification et Dédoublonnage
==================================================================
Nettoie les titres (prefixes ZZ), fusionne les doublons de contenu 
et élimine les fragments orphelins insignifiants.
"""

import json
import os
import re
import hashlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "liturgi_raw_refined.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "liturgi_raw_purified.json")

def clean_title(t):
    if not t: return ""
    # Retirer les préfixes types [œZZ[à] œ ou ZZ[¯] ¸ ou [Y1]
    # On cherche à retirer tout ce qui précède le premier mot réel
    t = re.sub(r'^(?:ZZ|\[|[\x00-\x1f\\])+[^a-zA-ZÀ-ÿ0-9]*', '', t)
    # Nettoyage résiduel des crochets et ZZ
    t = re.sub(r'ZZ\[.*?\]', '', t)
    t = re.sub(r'[Z\[\]\s\x00-\x1f\\]{2,}', ' ', t)
    return t.strip()

def get_norm_hash(rec):
    # Texte normalisé pour dédoublonnage (minuscules, sans ponctuation)
    t = rec.get("title", "")
    c = rec.get("content", "")
    full = (t + c).lower()
    full = re.sub(r'[^a-z0-9]', '', full)
    return hashlib.md5(full.encode('utf-8')).hexdigest()

def is_insignificant(rec):
    t = rec.get("title", "").strip()
    c = rec.get("content", "").strip()
    # Si pas de titre et contenu très court ou sans lettres
    if not t and len(c) < 50:
        if not re.search(r'[a-zA-ZÀ-ÿ]', c): return True
    if len(t) < 3 and len(c) < 30:
        if not re.search(r'[a-zA-ZÀ-ÿ]', t + c): return True
    return False

def main():
    print("🧹 PASSE 1.2 — Purification et Dédoublonnage")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Erreur : {INPUT_FILE} introuvable.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"📥 {len(data)} records chargés.")
    
    # 1. Nettoyage des titres et filtrage junk
    cleaned = []
    for rec in data:
        rec["title"] = clean_title(rec.get("title", ""))
        if not is_insignificant(rec):
            cleaned.append(rec)
    
    print(f"   → {len(data) - len(cleaned)} fragments insignifiants supprimés.")

    # 2. Dédoublonnage par contenu normalisé
    unique_records = {} # hash -> record
    dupe_count = 0
    
    for rec in cleaned:
        h = get_norm_hash(rec)
        if h in unique_records:
            dupe_count += 1
            # On garde celui qui a le plus de contenu ou de métadonnées
            existing = unique_records[h]
            if len(rec["content"]) > len(existing["content"]):
                unique_records[h] = rec
            # Fusionner les sources
            unique_records[h]["source_files"] = list(set(unique_records[h]["source_files"] + rec["source_files"]))
        else:
            unique_records[h] = rec

    final_list = list(unique_records.values())
    final_list.sort(key=lambda x: x["internal_id"])
    
    print(f"   → {dupe_count} doublons fusionnés.")
    print(f"✅ Export Purifié : {len(final_list)} records.")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
