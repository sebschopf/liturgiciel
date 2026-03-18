#!/usr/bin/env python3
"""
pass17_gibberish_detector.py — PASSE 1.7 : Filtrage du Gibberish et Tags Techniques
==================================================================================
Nettoie les tags_communs en supprimant les labels techniques (RY, U, etc.)
et les valeurs ne contenant pas de texte français intelligible (gibberish binaire).
"""

import json
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "liturgi_final_surrealdb.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "liturgi_final_surrealdb_scrubbed.json")

# Labels techniques FileMaker identifiés comme sans valeur liturgique
TECHNICAL_LABELS = {
    'RY', 'U', '8T', 'WT', 'HT', 'IP', 'LP', 'NT', 'yP', 'FB', 'JP', '_No'
}

# Labels Z-prefixés qui sont souvent du bruit binaire s'ils ne sont pas explicitement français
Z_LABELS = {'ZZ', 'XZ', 'ZL', 'ZJ', 'Z', 'X'}

def is_gibberish(text):
    if not text: return True
    text = text.strip()
    if len(text) < 2: return True
    
    # 1. Ratio Alphanumérique / Total
    # Si le texte contient trop de symboles bizarres, c'est du gibberish
    alphanum = len(re.findall(r'[a-zA-ZÀ-ÿ0-9]', text))
    ratio = alphanum / len(text)
    if ratio < 0.6 and len(text) > 4:
        return True
    
    # 2. Pattern de bruit binaire type FileMaker
    if re.search(r'[õ|◊|π|∑|Á|ø|ï|≠|Ro|ER|SR|\[|\]|G|W|Z]', text):
        # Si on a bcp de ces caractères, c'est du bruit
        noise_chars = len(re.findall(r'[õ◊π∑Áøï≠\[\]\^RGZW]', text))
        if noise_chars / len(text) > 0.25:
            return True
            
    # 3. Mots trop courts répétés (type Z ZZZ ZZZZ)
    if re.match(r'^([Z\s]{3,}|[X\s]{3,})$', text, re.I):
        return True

    return False

def is_intelligible_french(text):
    # Liste de mots communs ou racines françaises pour sauver les tags limites
    french_hints = [
        "prière", "chant", "psaume", "lecture", "bible", "dieu", "seigneur", "christ",
        "baptême", "mariage", "cene", "culte", "liturgie", "préface", "intercession",
        "accueil", "grâce", "pénitence", "louange", "confession", "foi", "envoi", "bénédiction"
    ]
    text_lower = text.lower()
    return any(hint in text_lower for hint in french_hints)

def main():
    print("🧹 PASSE 1.7 — Filtrage du Gibberish et Tags Techniques")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Erreur : {INPUT_FILE} introuvable.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"📥 {len(data)} records en cours de filtrage des tags...")
    
    stats = {"total": 0, "removed": 0}
    
    for rec in data:
        if "tags_communs" not in rec: continue
        
        original_tags = rec["tags_communs"]
        stats["total"] += len(original_tags)
        
        filtered_tags = []
        for tag in original_tags:
            label = tag.get("label", "")
            valeur = tag.get("valeur", "")
            
            # RÈGLES DE FILTRAGE
            # 1. Labels techniques interdits
            if label in TECHNICAL_LABELS:
                continue
                
            # 2. Labels Z/X prefixes : on ne les garde que si la valeur est intelligible
            if label in Z_LABELS:
                if is_gibberish(valeur) and not is_intelligible_french(valeur):
                    continue
            
            # 3. Valeurs gibberish générales
            if is_gibberish(valeur) and not is_intelligible_french(valeur):
                continue
                
            filtered_tags.append(tag)
            
        rec["tags_communs"] = filtered_tags
        stats["removed"] += (len(original_tags) - len(filtered_tags))

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    os.replace(OUTPUT_FILE, INPUT_FILE)
    
    print(f"✅ Filtrage terminé.")
    print(f"📊 Tags analysés : {stats['total']}")
    print(f"🗑️  Tags supprimés : {stats['removed']}")
    print(f"✨ Tags restants  : {stats['total'] - stats['removed']}")

if __name__ == "__main__":
    main()
