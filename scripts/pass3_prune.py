#!/usr/bin/env python3
"""
pass3_prune.py — PASSE 3 : Élagage des Artefacts Structurels
==============================================================
Nettoie en profondeur les champs content et all_fields.
"""

import json
import os
import re

_SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_SCRIPT_DIR)

INPUT_FILE  = os.path.join(_PROJECT_DIR, "liturgi_merged.json")
OUTPUT_FILE = os.path.join(_PROJECT_DIR, "liturgi_pruned.json")

# Patterns d'artefacts structurels FileMaker
PRUNE_PATTERNS = [
    # Patterns de navigation index (Echanges) : ZV X X _
    (r'ZV\s+[A-Z]\s+[A-Z]\s+_.{1,200}?[zZ]', ' '),
    # Patterns de marqueurs ZZ[...] et résidus associés
    (r'ZZ\[.*?\]', ' '),
    (r'\[[àéèîïôûœA-Z0-9\\]\]', ' '),
    (r'ZZ\^[àéèîïôûœA-Z0-9\\]', ' '),
    # Patterns de marqueurs WT : \\WT...\\U ou ]...WT...[...
    (r'\\?WT\d{14}(\[T\d\])?(\\+U)?', ' '),
    (r'\][^\]]{1,50}?WT\d{14}[^\]]{1,50}?\[\w{2}', ' '),
    # Résidus structurels de Sauvegarde : [Y1X, [T...], [Vb, [B..., X¶[[
    (r'\[Y[12\\]X¶?\[{0,2}', ' '),
    (r'\[T\d{14}\]', ' '),
    (r'\[Vb\]', ' '),
    (r'\[[A-Z][a-z0-9]\]', ' '),
    (r'X¶\[{1,2}', ' '),
    (r'\[[a-z]\d+', ' '), # Catch [u1 [j1 etc.
    (r'\\+[A-Z\d ]+', ' '), # Catch \8T \VQ etc
    (r'\[é\[ï\s*\[\]\[\[é', ' '),
    # Patterns techniques types X_Z, _X, Xã, X_, zX_Z
    (r'z?[A-Z]_[A-Z]', ' '),
    (r'\b_?[A-Z]\b', ' '),
    (r'\b[A-Z]_', ' '),
    (r'XZZX', ' '),
    (r'ZZXT', ' '),
    (r'ZZXP', ' '),
    (r'ZZXJ', ' '),
    (r'z[A-Z][a-z0-9]?', ' '), # Catch zX, zX1 type markers
    # Padding binaire décodé (K K K, ZZZZZ, Jõ)
    (r'(?:\bK\b\s*){3,}', ' '),
    (r'Z{3,}', ' '),
    (r'[Jö]\õ', ' '),
    # Marqueurs de ponctuation binaire isolés
    (r'[\\[\]\\{\\}|]{2,}', ' '),
    # Glyphes isolés et codes de contrôle résiduels
    (r'[⁄˙Åˇ•⁄†‡°ı\x80-\xff≤≥]', ' '),
    (r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' '),
    # IDs techniques isolés (14 digits)
    (r'\d{14}', ' '),
    # Longues chaînes sans espaces ( junk binaire)
    (r'[^\s]{40,}', ' '),
]

def prune_text(text, normalize_space=True):
    if not text:
        return ""
    
    # academic whitelisting before pruning
    text = re.sub(r'[^a-zA-ZÀ-ÿ0-9\s.,\'?!:;()\-—«»"\/<>]', '', str(text))

    # Appliquer les patterns d'élagage
    for pattern, replacement in PRUNE_PATTERNS:
        text = re.sub(pattern, replacement, text)
    
    # Normaliser les espaces (sauf si on veut garder les sauts de ligne)
    if normalize_space:
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
    else:
        # On normalise quand même les espaces horizontaux multiples
        text = re.sub(r'[ \t]+', ' ', text)
        # On retire les lignes vides excessives
        text = re.sub(r'\n\s*\n', '\n', text)
        
    return text.strip()

def is_garbage(text):
    """Detect if a string is likely technical debris using academic heuristics."""
    if not text: return True
    text_str = str(text).strip()
    if len(text_str) < 2: return True
    
    # 1. Natural Language Proof (Glue Words)
    GLUE_WORDS = {'de', 'le', 'la', 'et', 'que', 'en', 'un', 'une', 'des', 'les', 'pour', 'dans', 'par', 'sur', 'ce', 'au'}
    words = re.findall(r'\b[a-zA-ZÀ-ÿ]{2,}\b', text_str.lower())
    if not words: return True
    
    glue_count = sum(1 for w in words if w in GLUE_WORDS)
    if len(text_str) > 30 and glue_count == 0: return True
    
    glue_ratio = glue_count / len(words)
    if len(words) > 5 and glue_ratio < 0.10: return True

    # 2. Character Density & Diversity
    clean_text = re.sub(r'\s', '', text_str)
    letters = re.sub(r'[^a-zA-ZÀ-ÿ]', '', clean_text)
    if not letters: return True
    
    density_ratio = len(letters) / len(clean_text)
    unique_chars = len(set(letters.lower()))
    diversity_ratio = unique_chars / len(letters) if letters else 0
    if len(letters) > 30 and diversity_ratio < 0.20: return True 
    
    # 3. Vowel Density
    vowels = re.sub(r'[^aeiouyàâéèêëîïôûù]', '', letters.lower())
    vowel_ratio = len(vowels) / len(letters)
    if len(letters) > 10 and (vowel_ratio < 0.20 or vowel_ratio > 0.60): return True
    
    # 4. Uppercase explosion
    uppers = re.sub(r'[^A-Z]', '', clean_text)
    if len(uppers) / len(clean_text) > 0.70 and len(clean_text) > 8: return True

    return False

def main():
    print("✂️  Passe 3 — Élagage des Artefacts")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Erreur : {INPUT_FILE} introuvable.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"📥 {len(data)} records chargés.")

    pruned_data = []
    removed_count = 0

    for rec in data:
        # Élaguer le titre et contenu (on garde la structure)
        rec["titre"] = prune_text(rec.get("titre", ""), normalize_space=False)
        rec["contenu"] = prune_text(rec.get("contenu", ""), normalize_space=False)
        
        # Élaguer raw_fields (on peut normaliser ici)
        new_fields = {}
        for k, v in rec.get("raw_fields", {}).items():
            pruned_val = prune_text(str(v), normalize_space=True)
            if pruned_val and not is_garbage(pruned_val):
                new_fields[k] = pruned_val
        rec["raw_fields"] = new_fields
        
        # Si après élagage le record est vide ou n'est que du garbage
        if not rec.get("contenu") and not rec.get("titre") and not rec.get("raw_fields"):
            removed_count += 1
            continue
            
        pruned_data.append(rec)

    print(f"   → {removed_count} records purement structurels supprimés.")
    print(f"   → {len(pruned_data)} records restants.")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(pruned_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Export → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
