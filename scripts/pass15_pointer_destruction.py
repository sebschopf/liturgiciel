#!/usr/bin/env python3
"""
pass15_pointer_destruction.py — PASSE 1.5 : Destruction de Pointeurs et Squelettes (Phase 3)
================================================================================
Élimine les résidus binaires complexes, les pointeurs record-to-record
et les squelettes de métadonnées injectés dans le contenu, auteur et source.
"""

import json
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "liturgi_final_surrealdb.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "liturgi_final_surrealdb_purified.json")

# Liste des patterns réguliers pour la destruction chirurgicale
DESTRUCTION_PATTERNS = [
    # 1. Pointeurs record-to-record FileMaker (type [u1[j1[n1Yo2017)
    re.compile(r'\[u\d+\[j\d+\[n\d+Yo\d{4}'),
    
    # 2. Squelettes de dates et offsets (type 24.11.2002 ou 1.48.2001)
    re.compile(r'\\?\s?[SP]\d{1,2}\.\d{1,2}\.\d{4}'),
    
    # 3. Marqueurs d'ID et offset techniques (type 8T...T <]...)
    re.compile(r'8T\d{10,14}T?'),
    re.compile(r'T\s?<\s?\]\d+'),
    
    # 4. Trailing timestamps et IDs à crochets (type [Y1 0391840000001)
    re.compile(r'\[Y\d[\s]?\d{10,14}X?'),
    
    # 5. Codes de navigation et résidus X (Surgical: 3+ caps to avoid "Il", "Le")
    re.compile(r'\bX[A-ZÀ-ÿ\d]{3,}(?:ZZ[A-ZÀ-ÿ\d]+)?'),
    
    # 6. Résidus de crochets et ZZ restants (blobs complexes)
    re.compile(r'ZZ\[.*?\]'),
    re.compile(r'\[à?ZZ\[é?ZZ\^.*?\]'),
    re.compile(r'\[r\s+!.*?\]'), 
    
    # 7. Séquences binaires spécifiques observées
    re.compile(r'r\s+\^z_jõ[^\s]*'),
    re.compile(r'jõ[^\s]*'),
    
    # 8. Marqueurs de tabulations et sauts techniques (type P Tab ou \P)
    re.compile(r'\\?[PW]\s+Tab\b'),
    re.compile(r'\\P\b'),
    
    # 9. Offsets restants avec chevrons (type <]6207298)
    re.compile(r'<\s?\]\d+'),
    
    # 10. Abréviations de champs FileMaker injectées (type \\PK, \\VS, \\SW, \\VJ)
    re.compile(r'\\{1,2}(?:PK|VS|SW|VJ|VO|VU|VJ|SA|PT|VK|PW|XZ|ZL|ZJ|RZ|VV|VQ|SO|WS|W|VL|PS|VP|PF|RS|SS|S|P_|TxtPage)\b'),
    
    # 11. Nouveaux patterns Phase 2/3 (Offsets WT et isolated U)
    re.compile(r'WT\s?\d{10,14}'),
    re.compile(r'\bU\b'),
    
    # 12. Clusters binaires, tails et préfixes techniques Phase 3
    re.compile(r'^[A-Z]\s?:\s?'), # Préfixe Z : ou P :
    re.compile(r'^X[a-z]{1,2}ZZX[a-z]\s?X[a-z]\s?'), # Préfixe XtZZXq Xt
    re.compile(r'^X[a-z]\s?'), # Préfixe Xt
    re.compile(r'z]⁄\ZV.*?'),
    re.compile(r'\(\s?~R'),
    re.compile(r'z•⁄\\\[.*?'),
    re.compile(r'6207298\d*'),
    
    # 13. Slashs isolés en début ou fin de ligne/mot suite aux suppressions
    re.compile(r'\\{2,}'),

    # 14. Trailing numeric scories (timestamps/IDs sans crochets)
    re.compile(r'\s\d{10,15}\.?\s*$'),
]

# Table de secours pour les caractères mal encodés persistants
EXTRA_CLEAN_MAP = [
    (re.compile(r'gr[^\w\s]?ce', re.I), 'grâce'),
    (re.compile(r'No[^\w\s]?l', re.I), 'Noël'),
    (re.compile(r'P[^\w\s]?ques', re.I), 'Pâques'),
    (re.compile(r'bapt[^\w\s]?me', re.I), 'baptême'),
    (re.compile(r'm[^\w\s]?moire', re.I), 'mémoire'),
    (re.compile(r'\bc[\'|\s]?Sur', re.I), 'cœur'),
    (re.compile(r'\bveille\b'), 'éveille'),
    (re.compile(r'\bcouté[s]?\b'), 'écouté'),
    (re.compile(r'\bJus\b'), 'Jésus'),
    (re.compile(r'\bPque\b'), 'Pâque'),
]

def surgical_clean(text):
    if not text or not isinstance(text, str): 
        return text
    
    # 1. Patterns de destruction
    for pattern in DESTRUCTION_PATTERNS:
        text = pattern.sub('', text)
    
    # 2. Restauration des caractères français cassés
    for pattern, replacement in EXTRA_CLEAN_MAP:
        text = pattern.sub(replacement, text)

    # 3. Nettoyage final des résidus binaires non-imprimables
    text = re.sub(r'[^\x20-\x7E\sÀ-ÿœŒ]', '', text)
    
    # 4. Nettoyage des résidus "â â" ou "l l" en début de titre ou contenu
    text = re.sub(r'^[âli]\s[âli]\s?', '', text)
    
    # 5. Nettoyage des espaces multiples et trim
    text = re.sub(r' {2,}', ' ', text).strip()
    
    return text

def main():
    print("🧨 PASSE 1.5 — Destruction de Pointeurs et Squelettes (Phase 3)")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Erreur : {INPUT_FILE} introuvable.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"📥 {len(data)} records en cours de traitement...")
    
    clean_count = 0
    for rec in data:
        # Nettoyage de TOUS les champs textuels
        for field in ("titre", "contenu", "auteur", "source"):
            val = rec.get(field)
            if isinstance(val, str):
                old_val = val
                rec[field] = surgical_clean(val)
                if old_val != rec[field]:
                    clean_count += 1
            
        # Nettoyage des tags
        if "tags_communs" in rec and isinstance(rec["tags_communs"], list):
            for tag in rec["tags_communs"]:
                val = tag.get("valeur")
                if isinstance(val, str):
                    tag["valeur"] = surgical_clean(val)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    os.replace(OUTPUT_FILE, INPUT_FILE)
    
    print(f"✅ Destruction terminée. {clean_count} champs modifiés.")

if __name__ == "__main__":
    main()
