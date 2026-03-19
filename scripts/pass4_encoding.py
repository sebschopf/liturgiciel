#!/usr/bin/env python3
"""
pass4_encoding.py — PASSE 4 : Correction d'Encodage
===============================================
Corrige les artefacts d'encodage mac_roman/cp1252 dans les données extraites.
Référence : ADR 028 §Problème 2, ADR 029 §Encodage
"""

import json
import os
import re

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE  = os.path.join(BASE_DIR, "liturgi_pruned.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "liturgi_encoded.json")

# Table de correction systématique mac_roman → UTF-8 correct
CHAR_MAP = {
    'È': 'é',
    'Ë': 'è',
    'Ù': 'ô',
    'Í': 'ê',
    'Ó': 'î',
    'Ô': 'ï',
    'Ú': 'û',
    'À': 'à',
    '‡': 'à',
    '†': '!',
    '°': '°',
    'Î': 'î',
    'ı': 'î',
    '…': '...',
    'œ': 'oe',
    'ﬁ': 'fi',
    '‹': '<',
    '”': '"',
    '’': "'",
    '◊': '',
    '¿': '',
    '~': '',
    '': '',
    'ã': 'à',
    'õ': 'ô',
    '¢': '',
    '£': '',
    '§': '',
    '¶': '',
    'ß': '',
    '®': '',
    '©': '',
    '™': '',
    '´': "'",
    '¨': '"',
    '≠': '',
    'Æ': 'AE',
    'Ø': 'O',
    '∞': '',
    '±': '',
    '≤': '',
    '≥': '',
    '¥': '',
    'µ': '',
    '∂': '',
    '∑': '',
    '∏': '',
    'π': '',
    '∫': '',
    'ª': '',
    'º': '',
    'Ω': '',
    'æ': 'ae',
    'ø': 'o',
    '¡': '',
    '¬': '',
    '√': '',
    'ƒ': '',
    '≈': '',
    '∆': '',
    '«': '"',
    '»': '"',
    '  ': ' ',
    '   ': ' ',
    '    ': ' ',
    '     ': ' ',
    '      ': ' ',
    '       ': ' ',
}



# Patterns parasites à supprimer ou remplacer
NOISE_PATTERNS = [
    (r'ß',              ''),      # caractère parasite
    (r'Z{5,}',          ''),      # padding binaire brut
    (r'(?:\bK\b\s*){4,}', ' '),   # padding K K K K
    (r'[JZ]öW\b',       ''),      # résidus binaires
    (r'\bZ[QX]\b',      ''),
    (r'\bZZX\b',        ''),
    (r'[\[\]]{2,}',     ' '),     # Crochets multiples [[]]
    (r'\s{2,}',         ' '),     # espaces multiples
]


def fix_chars(text: str, normalize_space=True) -> str:
    """Applique les corrections de caractères et retire les bruits."""
    if not text:
        return text

    # Correction des glyphes mac_roman/cp1252
    for wrong, correct in CHAR_MAP.items():
        text = text.replace(wrong, correct)

    # Suppression des patterns parasites
    for pattern, replacement in NOISE_PATTERNS:
        if pattern == r'\s{2,}' and not normalize_space:
            # On ne normalise pas les espaces si on veut garder la structure
            text = re.sub(r'[ \t]{2,}', ' ', text)
            continue
        text = re.sub(pattern, replacement, text)

    return text.strip()


def fix_record(rec: dict) -> dict:
    """Corrige l'encodage dans tous les champs textuels d'un record."""
    # Champs standards (structure préservée pour titre et contenu)
    for field in ('titre', 'contenu'):
        if field in rec and rec[field]:
            rec[field] = fix_chars(rec[field], normalize_space=False)
            
    for field in ('auteur', 'source'):
        if field in rec and rec[field]:
            rec[field] = fix_chars(rec[field], normalize_space=True)

    # Corriger les valeurs de raw_fields
    if 'raw_fields' in rec:
        rec['raw_fields'] = {
            label: fix_chars(str(val), normalize_space=True)
            for label, val in rec['raw_fields'].items()
        }

    return rec


def main():
    print("🔤 Passe 4 — Correction d'encodage")
    print(f"📥 Lecture de {INPUT_FILE}...")

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"   {len(data)} records chargés.")

    fixed = [fix_record(rec) for rec in data]

    # Stats
    nb_raw = sum(1 for r in fixed if r.get('raw_fields'))
    print(f"✅ {nb_raw} records avec raw_fields préservés")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(fixed, f, ensure_ascii=False, indent=2)

    print(f"💾 Sortie → {OUTPUT_FILE}")
    print(f"✅ Passe 4 terminée — {len(fixed)} records.")


if __name__ == '__main__':
    main()
