#!/usr/bin/env python3
"""
pass7_purity.py — PASSE 7 : Pureté Absolue V2.2 (Heuristique & NLP)
Applique un nettoyage par mots basé sur des heuristiques (densité de
caractères spéciaux, restes de tags FileMaker, séquences aberrantes).
"""

import json
import os
import re

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE  = os.path.join(BASE_DIR, "liturgi_final_surrealdb.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "liturgi_final_surrealdb.json")

def is_garbage(word):
    """Détermine si un mot est un déchet binaire (Heuristique)."""
    if not word: return False
    
    # 1. Caractères purement binaires ou techniques
    if any(c in "[]{}\\^<>" for c in word): return True
    if any(c in "¶⁄◊õ∑™$" for c in word): return True
    
    # 2. Séquences typiques de bruit binaire (FileMaker)
    if "WT" in word and any(c.isdigit() for c in word): return True
    if re.search(r'(XX|ZZ|XT|xT|XK|Xq)', word): return True
    
    # 3. Ratio de caractères non-alphanumériques (Heuristique Académique)
    non_alpha = len(re.findall(r'[^a-zA-ZÀ-ÿ0-9.,!?\'"\s\-]', word))
    if len(word) > 2 and (non_alpha / len(word)) > 0.20:
        return True
            
    # 4. Explosion de majuscules (IDs ou Codes techniques)
    # On autorise les sigles courts (SFP, etc.) mais pas le mélange CaméCase abusif
    uppers = sum(1 for c in word[1:] if c.isupper() and c.isalpha())
    if len(word) > 4 and uppers > len(word)/3 and not word.isupper():
        return True
        
    return False

def clean_text_nlp(text):
    """Nettoyage "Scalpel" basé sur la structure et non sur une liste de mots."""
    if not text: return text
    
    # 1. Troncature structurelle (Le Scalpel)
    # On cherche les codes de type "Label + ID" souvent à la fin des fiches
    # Ex: "Culte familles T1 6207298" -> on garde "Culte familles"
    text = re.sub(r'\s+[A-Z]\d\s+\d{7,14}\s*$', '', text)
    
    # 2. Suppression des marqueurs techniques isolés
    text = re.sub(r'X\}ZZXy|ZZ8r\^z_jQ|\}T|XjöJ|\[Y1X|abT', ' ', text)
    text = re.sub(r'\]\d{7,10}', ' ', text)
    
    # 3. Nettoyage par mot (Heuristique seulement)
    words = re.split(r'(\s+)', text)
    cleaned_words = []
    
    for w in words:
        if not w.strip():
            cleaned_words.append(w)
            continue
        # On ne supprime que si on est SUR que c'est du bruit
        if not is_garbage(w):
            cleaned_words.append(w)
    
    result = "".join(cleaned_words)
    
    # 4. Post-traitement de surface
    result = re.sub(r'^[^a-zA-ZÀ-ÿ0-9]+', '', result) 
    result = re.sub(r' +', ' ', result)
    
    return result.strip()

def main():
    print("✨ Passe 7 — Pureté Absolue V2.2 (Heuristique)")
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Erreur: {INPUT_FILE} introuvable.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cleaned_count = 0
    for rec in data:
        modified = False
        for key in ['titre', 'contenu', 'auteur', 'source']:
            if rec.get(key):
                original = rec[key]
                cleaned = clean_text_nlp(rec[key])
                rec[key] = cleaned
                if original != cleaned: modified = True
                
        if rec.get('tags_communs'):
            cleaned_tags = []
            for tag in rec['tags_communs']:
                clean_tag = clean_text_nlp(tag)
                if clean_tag and len(clean_tag) > 2:
                    cleaned_tags.append(clean_tag)
            
            if set(cleaned_tags) != set(rec['tags_communs']):
                modified = True
            rec['tags_communs'] = cleaned_tags
            
        if modified: cleaned_count += 1

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Passe 7 terminée — {cleaned_count} records purifiés.")

if __name__ == '__main__':
    main()