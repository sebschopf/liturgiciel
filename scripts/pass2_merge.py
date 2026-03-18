#!/usr/bin/env python3
"""
pass2_merge.py — PASSE 2 : Résolution des Liens et Fallback Titre
==============================================================
1. Charge liturgi_raw.json.
2. Résout les liens WT.
3. Fallback : Si titre vide, utilise la 1ère ligne du contenu.
"""

import json
import os
import re

_SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_SCRIPT_DIR)

INPUT_FILE  = os.path.join(_PROJECT_DIR, "liturgi_raw_v2.json")
OUTPUT_FILE = os.path.join(_PROJECT_DIR, "liturgi_merged.json")

def extract_wt_ids(text):
    if not text: return []
    return re.findall(r'WT(\d{14})', str(text))

def clean_first_line(text):
    """Nettoie une ligne de ses résidus binaires et ponctuations isolées."""
    if not text: return ""
    # On prend la première ligne
    line = text.split('\n')[0].split('\r')[0]
    # En V2, le contenu est déjà largement propre.
    # On retire juste les caractères bizarres au début si nécessaire.
    line = re.sub(r'^[^a-zA-ZÀ-ÿ0-9]+', '', line)
    return line.strip()

def main():
    print("🔗 Passe 2 — Résolution des Liens & Fallback Titre (Mode V2)")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Erreur : {INPUT_FILE} introuvable.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"📥 {len(data)} records chargés.")

    # Indexation
    by_id = {rec['id_fiche']: rec for rec in data}
    
    resolved_links = 0
    generated_titles = 0

    for rec in data:
        # 1. Résolution WT
        for label, val in rec.get("raw_fields", {}).items():
            wt_targets = []
            if label == "WT":
                # Find all 14-digit IDs in the value
                wt_targets = re.findall(r'(\d{14})', str(val))
            else:
                # Find WT followed by digits in any field
                wt_targets = re.findall(r'WT(\d{14})', str(val))
                
            for target_id in wt_targets:
                if target_id in by_id and target_id != rec['id_fiche']:
                    target_rec = by_id[target_id]
                    # On propage les rubriques de classement vers le contenu
                    for k, v in rec['raw_fields'].items():
                        if k not in ('_T', '8T', 'HT', 'WT', 'id_fiche', 'titre', 'auteur'):
                            if f"IDX_{k}" in target_rec['raw_fields']:
                                if v not in target_rec['raw_fields'][f"IDX_{k}"]:
                                    target_rec['raw_fields'][f"IDX_{k}"] += " | " + v
                            else:
                                target_rec['raw_fields'][f"IDX_{k}"] = v
                    resolved_links += 1

        # 2. Fallback Titre
        if not rec.get("titre") and rec.get("contenu"):
            fallback = clean_first_line(rec["contenu"])
            if len(fallback) > 3:
                rec["titre"] = fallback
                generated_titles += 1

    print(f"   → {resolved_links} liens d'indexation (WT) résolus.")
    print(f"   → {generated_titles} titres générés par fallback.")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Export → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
