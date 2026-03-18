#!/usr/bin/env python3
"""
pass14_final_polish.py — PASSE 1.4 : Polissage de Haute Précision
===================================================================
Élimine les scories ultra-spécifiques restées après les passes précédentes
(ex: 'œ' en début de phrase, queues binaires type 'r ^z_jõ...').
"""

import json
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "liturgi_final_surrealdb.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "liturgi_final_surrealdb_polished.json")

def ultra_clean(text):
    if not text: return ""
    
    # 1. Retirer la queue binaire spécifique ZV/RY
    text = re.sub(r'\s+[a-z]\s+\^z_jõ[^\s]*?\[[Y\d].*', '', text)
    
    # 2. Retirer le 'œ' parasite au début s'il est suivi d'une majuscule
    text = re.sub(r'^œ(?=[A-ZÀ-Ÿ])', '', text)
    
    # 3. Retirer les résidus de crochets mal formés
    text = re.sub(r'\[à?ZZ\[é?ZZ\^.*', '', text)

    # 4. Nettoyage final des espaces multiples
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def main():
    print("✨ PASSE 1.4 — Polissage de Haute Précision")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Erreur : {INPUT_FILE} introuvable.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"📥 {len(data)} records en cours de polissage final...")
    
    for rec in data:
        rec["titre"] = ultra_clean(rec.get("titre", ""))
        rec["contenu"] = ultra_clean(rec.get("contenu", ""))
        
        # Polissage aussi des tags communs pour la cohérence
        if "tags_communs" in rec:
            for tag in rec["tags_communs"]:
                tag["valeur"] = ultra_clean(tag.get("valeur", ""))

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Remplacer le fichier final par la version polie
    os.replace(OUTPUT_FILE, INPUT_FILE)
    
    print(f"✅ Polissage final terminé.")

if __name__ == "__main__":
    main()
