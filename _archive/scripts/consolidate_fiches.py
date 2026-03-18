#!/usr/bin/env python3
"""
consolidate_fiches.py — Consolidateur de données liturgiques.
Liaison intelligente entre les métadonnées techniques et les textes sacrés extraits.
"""

import json
import re

def clean(text):
    if not text: return ""
    return re.sub(r'\s{2,}', ' ', text).strip()

def main():
    # Chargement des sources
    try:
        with open("fiches_exhaustive.json", "r") as f:
            fiches_meta = json.load(f)
        with open("liturgy_content.json", "r") as f:
            liturgy_texts = json.load(f)
    except FileNotFoundError:
        print("Fichiers sources manquants.")
        return

    # On veut rattacher les textes de liturgy_content aux fiches de fiches_exhaustive
    # Stratégie :
    # 1. Si une fiche a déjà un contenu long (>200), on le garde.
    # 2. Sinon, on cherche dans liturgy_texts un texte qui contient le titre ou des mots-clés.
    
    final_db = []
    texts_assigned = [False] * len(liturgy_texts)
    
    for fiche in fiches_meta:
        if len(fiche["contenu"]) < 100:
            # Recherche d'un texte plus riche
            best_match = ""
            for i, text in enumerate(liturgy_texts):
                # On cherche si les 50 premiers caractères du titre sont dans le texte
                simplified_title = re.sub(r'[^a-zA-Z]', '', fiche["titre"][:50]).lower()
                if simplified_title and simplified_title in re.sub(r'[^a-zA-Z]', '', text[:200]).lower():
                    if len(text) > len(best_match):
                        best_match = text
                        texts_assigned[i] = True
            
            if best_match:
                fiche["contenu"] = best_match
        
        if fiche["titre"] or len(fiche["contenu"]) > 50:
            final_db.append(fiche)

    # Ajout des textes orphelins (qui n'ont pas trouvé de titre mais sont des prières)
    for i, text in enumerate(liturgy_texts):
        if not texts_assigned[i]:
            final_db.append({
                "id": f"orph_{i}",
                "titre": "Texte liturgique extrait",
                "auteur": "Inconnu",
                "source": "Sauvegarde.lit",
                "contenu": text
            })

    # Export final
    with open("liturgy_db_final.json", "w", encoding="utf-8") as f:
        json.dump(final_db, f, indent=2, ensure_ascii=False)
        
    print(f"✨ Base de données consolidée : {len(final_db)} records dans liturgy_db_final.json")

if __name__ == "__main__":
    main()
