#!/usr/bin/env python3
"""
pass6_export.py — PASSE 6 : Formatage Final SurrealDB (V2.2)
============================================================
Reformate les données en JSON épuré prêt pour l'application.
Référence : Implementation Plan V2.2
"""

import json
import os

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE  = os.path.join(BASE_DIR, "liturgi_rubriques.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "liturgi_final_surrealdb.json")

def map_record(rec: dict) -> dict:
    """
    Transforme un record en structure cible épurée.
    """
    return {
        "id_utilisateur":    rec.get("id_utilisateur", "system"),
        "id_fiche":          rec.get("id_fiche", ""),
        "titre":             rec.get("titre") or None,
        "contenu":           rec.get("contenu") or None,
        "auteur":            rec.get("auteur") or None,
        "source":            rec.get("source") or None,
        "langue":            rec.get("langue", "fr"),
        "temps_liturgiques": rec.get("temps_liturgiques", []),
        "tags_communs":      rec.get("tags_communs", []),
        "types":             rec.get("types", "autres"),
        "tags_personnels":   rec.get("tags_personnels", []),
        "date_creation":     rec.get("date_creation"),
        "date_modification": rec.get("date_modification"),
    }

def main():
    print("📦 Passe 6 — Format Final Épuré")
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Erreur: {INPUT_FILE} introuvable.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    mapped = [map_record(rec) for rec in data]

    # Stats
    with_titre   = sum(1 for r in mapped if r['titre'])
    with_contenu = sum(1 for r in mapped if r['contenu'])
    with_dates   = sum(1 for r in mapped if r['date_creation'] or r['date_modification'])

    print(f"\n📊 Résumé V2.2 :")
    print(f"   Total records        : {len(mapped)}")
    print(f"   Avec titre           : {with_titre}")
    print(f"   Avec contenu         : {with_contenu}")
    print(f"   Avec dates           : {with_dates}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(mapped, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Sortie → {OUTPUT_FILE}")
    print(f"✅ Pipeline V2.2 terminée.")

if __name__ == '__main__':
    main()
