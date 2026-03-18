#!/usr/bin/env python3
"""
pass11_extract_refined.py — PASSE 1.1 : Raffinement de l'Extraction
==================================================================
S'exécute APRÈS pass1_extract.py pour récupérer chirurgicalement le texte
trappé dans des champs non-standards (ZV, etc.) et nettoyer les scories binaires
directement à la source du JSON brut.
"""

import json
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "liturgi_raw.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "liturgi_raw_refined.json")

# Correction d'encodage Mac Roman → UTF-8 (complémentaire)
MAC_ROMAN_MAP = {
    'È': 'é', 'Ë': 'è', 'Ù': 'ô', 'Í': 'ê', 'Ó': 'î', 'Ô': 'ï', 'Ú': 'û',
    'À': 'à', '‡': 'à', '†': ' !', '°': 'è', 'Î': 'î', 'ı': 'î', 'Œ': 'œ',
    '«': '«', '»': '»', '‡': 'à', 'Â': 'â', 'Ê': 'ê', '…': '...', '‡': 'à',
    '—': '—', '’': "'", '‘': "'", 'ç': 'ç', 'Ç': 'Ç', 'Â': 'â'
}

# Patterns de nettoyage binaire chirurgicaux
SCRUB_PATTERNS = [
    (r'\[Y[12\\]X¶?\[{0,2}', ' '),
    (r'X¶\[{1,2}', ' '),
    (r'\[T\d{14}\]', ' '),
    (r'ZV\s+[A-Z]\s+[A-Z]\s+_.*?[zZ]', ' '),
    (r'\][^\]]*?WT\d{14}[^\]]*?\[\w{2}', ' '),
    (r'\[é\[ï\s*\[\]\[\[é', ' '),
    (r'ZZ\[ÉZZ\[â', ' '),
    (r'\[\[\s*É', ' '),
    (r'\[\[', ' '),
    (r'\]\]', ' '),
    (r'z\s+\]\[\[\s*\{', ' '),
    (r'XZZ\[[A-Z0-9]', ' '),
    (r'Z{3,}', ' '),
    (r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' '),
]

def scrub_text(text):
    if not text: return ""
    # Fix characters
    for k, v in MAC_ROMAN_MAP.items():
        text = text.replace(k, v)
    
    # Scrub binary scories
    for pattern, replacement in SCRUB_PATTERNS:
        text = re.sub(pattern, replacement, text)
    
    # Final cleanup
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def main():
    print("🔬 PASSE 1.1 — Raffinement et Nettoyage Chirurgical")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Erreur : {INPUT_FILE} introuvable.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"📥 Traitement de {len(data)} records...")
    
    for rec in data:
        # 1. Récupérer le contenu trappé dans all_fields
        extra_content = []
        all_fields = rec.get("all_fields", {})
        
        # Champs prioritaires pour le contenu liturgique trappé
        for key in ("ZV", "XT", "TxtPage", "RY"):
            if key in all_fields:
                val = str(all_fields[key]).strip()
                if val and len(val) > 20: # On évite les codes techniques courts
                    extra_content.append(scrub_text(val))
        
        # Si le contenu principal est vide ou court, on cherche le plus long champ
        if len(rec.get("content", "")) < 50:
            candidates = [scrub_text(str(v)) for k, v in all_fields.items() if len(str(v)) > 100]
            if candidates:
                best = max(candidates, key=len)
                if len(best) > len(rec.get("content", "")):
                    rec["content"] = best

        # 2. Nettoyer le contenu existant
        rec["content"] = scrub_text(rec["content"])
        
        # Append extra content if not already there
        for extra in extra_content:
            if extra and extra not in rec["content"]:
                rec["content"] = (rec["content"] + "\n\n" + extra).strip()

        # 3. Nettoyer le titre
        rec["title"] = scrub_text(rec.get("title", ""))
        
        # 4. Nettoyer all_fields (prévisualisation propre)
        cleaned_fields = {}
        for k, v in all_fields.items():
            cleaned_v = scrub_text(str(v))
            if cleaned_v and len(cleaned_v) > 1:
                cleaned_fields[k] = cleaned_v
        rec["all_fields"] = cleaned_fields

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Export raffiné → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
