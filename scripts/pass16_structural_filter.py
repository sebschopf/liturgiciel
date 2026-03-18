#!/usr/bin/env python3
"""
pass16_structural_filter.py — PASSE 1.6 : Filtrage Structurel (Phase 3 ULTIMATE)
=============================================================================
"""

import json
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "liturgi_final_surrealdb.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "liturgi_final_surrealdb_filtered.json")

def is_structural_junk(rec):
    iid = str(rec.get("id_filemaker", ""))
    titre = str(rec.get("titre") or "").strip()
    contenu = str(rec.get("contenu") or "").strip()
    auteur = str(rec.get("auteur") or "").strip()

    # RÈGLE D'OR : On supprime tous les records sans contenu substantiel
    if len(contenu) < 50:
        # Sauf si le titre est très spécifique et liturgique
        liturgical_titles = {"baptême", "mariage", "noël", "pâques"}
        if titre.lower() not in liturgical_titles:
            return True

    # RÈGLE D'OR 2 : On supprime les ghosts identifiés par ID
    GHOST_PREFIXES = ("103918400016", "103918400010")
    if any(iid.startswith(p) for p in GHOST_PREFIXES):
        if len(contenu) < 200:
            return True

    # RÈGLE D'OR 3 : Titres techniques
    if titre.lower() in ("ordinaire", "sauvegarde", "echanges", "tous les temps", "titre"):
        return True

    return False

def main():
    print("🧹 PASSE 1.6 — Filtrage Structurel Ultimate")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Erreur : {INPUT_FILE} introuvable.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"📥 {len(data)} records en cours de filtrage...")
    
    filtered_data = [rec for rec in data if not is_structural_junk(rec)]
    
    removed_count = len(data) - len(filtered_data)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, indent=2, ensure_ascii=False)
    
    os.replace(OUTPUT_FILE, INPUT_FILE)
    
    print(f"✅ Filtrage terminé. {removed_count} records techniques supprimés.")
    print(f"📊 Dataset final : {len(filtered_data)} fiches.")

if __name__ == "__main__":
    main()
