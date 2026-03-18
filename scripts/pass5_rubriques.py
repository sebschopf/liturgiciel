#!/usr/bin/env python3
"""
pass5_rubriques.py — PASSE 5 : Mapping Rubriques & Classification
============================================================
Mappe les rubriques FileMaker vers le vocabulaire contrôlé et classifie par TYPE.
Référence : ADR 029 & Implementation Plan V2.2
"""

import json
import os
import re

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE  = os.path.join(BASE_DIR, "liturgi_encoded.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "liturgi_rubriques.json")

# ---------------------------------------------------------------------------
# Vocabulaire contrôlé
# ---------------------------------------------------------------------------

LABEL_TO_TEMPS = {
    'PPentec':    'pentecote',
    'UEpiphanie': 'epiphanie',
    'GEpiphanie': 'epiphanie',
    'LCar':       'careme',
    'GVendredi':  'semaine_sainte',
    'GPaques':    'paques',
    'GNoel':      'noel',
}

VALEUR_TO_TEMPS = [
    (r'\bordin',                'ordinaire'),
    (r'\bpascal',               'paques'),
    (r'\bpaques|p[aâ]ques',     'paques'),
    (r'\bavent',                'avent'),
    (r'\bnoe[ël]',              'noel'),
    (r'\bcar[eê]me',            'careme'),
    (r'\bsemaine\s*sainte',     'semaine_sainte'),
    (r'\bvendredi\s*saint',     'semaine_sainte'),
    (r'\bpentec[oô]te',         'pentecote'),
    (r'\bepiphanie',            'epiphanie'),
    (r'\bascension',            'ascension'),
    (r'\btoussaint',            'toussaint'),
    (r'\btrinit[eé]',           'trinite'),
    (r'\bréformation',          'reformation'),
    (r'\btous\s*temps',         'tous_temps'),
]

VALEUR_TO_OCCASION = [
    (r'\bfun[eè]bre|fun[eè]railles', 'funerailles'),
    (r'\binstallation',          'installation'),
    (r'\bmariage',               'mariage'),
    (r'\bbapteme|bap[tê]me',     'bapteme'),
    (r'\bcommunion|c[eè]ne',     'cene'),
    (r'\bconfirmation',          'confirmation'),
    (r'\bcat[eé]chum[eè]ne',     'catechumene'),
]

VALEUR_TO_PUBLIC = [
    (r'\bfamilles?\b',           'familles'),
    (r'\benfant|éveil\s*\d',     'enfants'),
    (r'\badolesc',               'adolescents'),
    (r'\bjeunesse|jeunes?\b',    'jeunes'),
]

# --- Classification par TYPE (Nouveau V2.2) ---
# Types: prière, texte, prédication, chant, verset, autres
TYPE_KEYWORDS = [
    (r'\bprière|prie\b|intercession|invocation|collecte|pénitence|supplication|louange|adoration|action de grâce', 'prière'),
    (r'\bchant|hymne|psaume|cantique|chœur|chorit?e|vocal|musical', 'chant'),
    (r'\bprédication|sermon|homélie|méditation|message|exhortation', 'prédication'),
    (r'\bverset|répons|acclamation|antienne|salutation|bénédiction', 'verset'),
    (r'\blecture|épître|évangile|récit|biblique|parole', 'texte'),
]

LABEL_TO_TYPE = {
    'QA': 'verset', # Questions/Réponses
    'UE': 'texte',  # Lectures
}

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
    
    # Trop long pour être un tag raisonnable
    if len(text_str) > 60: return True
    
    return False

def identify_type(rec):
    """Identifie le type de fiche basé sur le titre, le contenu et les labels."""
    content = rec.get('contenu', '').lower()
    title = (rec.get('titre') or '').lower()
    all_fields = rec.get('raw_fields', {})
    
    # 1. Check labels
    for label in all_fields:
        if label in LABEL_TO_TYPE:
            return LABEL_TO_TYPE[label]
    
    # 2. Check title (high priority)
    for pattern, ttype in TYPE_KEYWORDS:
        if re.search(pattern, title):
            return ttype
            
    # 3. Check content
    for pattern, ttype in TYPE_KEYWORDS:
        if re.search(pattern, content[:200]): # Limit to start of content
            return ttype
            
    return "autres"

def normalize_record(rec: dict) -> dict:
    temps     = set()
    occasions = set()
    publics   = set()
    tags_communs = []

    all_fields = rec.get('raw_fields', {})

    for label, val in all_fields.items():
        val_str = str(val).strip()
        if not val_str: continue

        mapped = False
        base_label = label[4:] if label.startswith("IDX_") else label
        
        if base_label in LABEL_TO_TEMPS:
            temps.add(LABEL_TO_TEMPS[base_label])
            mapped = True
        if base_label in [l for l in LABEL_TO_TEMPS if l in ['zInstallation', 'GMariage', 'DFuner', 'zBapteme', 'DCene']]: # Simplified for demo
            pass # See LABEL_TO_OCCASION logic below

        # Simplified mapping logic for V2.2 clean export
        val_lower = val_str.lower()
        for p, t in VALEUR_TO_TEMPS:
            if re.search(p, val_lower): temps.add(t); mapped = True
        for p, o in VALEUR_TO_OCCASION:
            if re.search(p, val_lower): occasions.add(o); mapped = True
        for p, pub in VALEUR_TO_PUBLIC:
            if re.search(p, val_lower): publics.add(pub); mapped = True

        if not mapped and len(val_str) > 2 and len(label) < 6:
            if not is_garbage(val_str):
                tags_communs.append(val_str[:50].strip())

    rec['temps_liturgiques']  = sorted(list(temps))
    # Fusion occasions -> tags_communs as requested
    filtered_occasions = [o for o in occasions if not is_garbage(o)]
    rec['tags_communs']       = sorted(list(set(tags_communs + filtered_occasions)))
    rec['publics']            = sorted(list(publics))
    rec['types']              = identify_type(rec)
    rec['tags_personnels']    = []
    rec['id_utilisateur']     = "system" # Default for now
    
    return rec

def main():
    print("🗂️  Passe 5 — Refinement V2.2")
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Erreur: {INPUT_FILE} introuvable.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    result = [normalize_record(rec) for rec in data]

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ Passe 5 terminée — {len(result)} records. Types identifiés.")

if __name__ == '__main__':
    main()
