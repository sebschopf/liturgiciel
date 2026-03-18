#!/usr/bin/env python3
"""
pass13_surgical_scrub.py — PASSE 1.3 : Polissage Chirurgical Final
===================================================================
Nettoie les scories résiduelles persistantes (œ, [, ], ZZ) dans les
champs finaux. S'exécute sur le fichier final pour garantir la pureté.
"""

import json
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "liturgi_final_surrealdb.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "liturgi_final_surrealdb_clean.json")

def surgical_clean(text):
    if not text: return ""
    
    # 1. Retirer les scories ZZ[...] et variations
    text = re.sub(r'ZZ\[.*?\]', ' ', text)
    text = re.sub(r'\[à?ZZ\[é?ZZ\^.*?\d+', ' ', text) # Queue de binaires
    text = re.sub(r'ZZ\^[àéèîïôûœA-Z0-9\\]', ' ', text)
    text = re.sub(r'\[\w\]', ' ', text)
    
    # 2. Retirer les caractères non-alphanumériques au DEBUT (scories comme [œ)
    # On garde les chiffres et les lettres accentuées, ainsi que ponctuation de début
    text = re.sub(r'^[^a-zA-ZÀ-ÿ0-9"\'(« ]+', '', text)
    
    # 3. Retirer les scories à la FIN
    text = re.sub(r'[^a-zA-ZÀ-ÿ0-9?!.!)"» ]+$', '', text)
    
    # 4. Normalisation des espaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def main():
    print("💎 PASSE 1.3 — Polissage Chirurgical Final")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Erreur : {INPUT_FILE} introuvable.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"📥 {len(data)} records en cours de polissage...")
    
    for rec in data:
        rec["titre"] = surgical_clean(rec.get("titre", ""))
        rec["contenu"] = surgical_clean(rec.get("contenu", ""))
        
        # Nettoyage optionnel des tags
        if "tags_communs" in rec:
            for tag in rec["tags_communs"]:
                tag["valeur"] = surgical_clean(tag.get("valeur", ""))

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Remplacer le fichier final par la version propre
    os.replace(OUTPUT_FILE, INPUT_FILE)
    
    print(f"✅ Polissage terminé. Fichier mis à jour.")

if __name__ == "__main__":
    main()
