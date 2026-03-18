#!/usr/bin/env python3
"""
pass1_extract.py — PASSE 1 : Extraction Zero-Fragmentation (V8 - The One)
==========================================================================
"""

import json
import os
import re
from collections import defaultdict
import string

_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(_PROJECT_DIR, "liturgi_raw.json")
SOURCE_DIR = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN"

XOR_VAL = 0x5A

# Whitelist exhaustive basée sur pass5, ADR et l'analyse binaire
TECH_LABELS = {
    'RY', 'WT', 'HT', 'NT', 'IP', 'LP', 'yP', 'FB', 'JP', '8T', 'PF', 
    'SE', 'SF', 'SG', 'PP', 'GV', 'GP', 'GN', 'LC', 'UE', 'GE', 'QA',
    'TT', 'XT', 'ZV', 'VN', 'VN30', 'TxtPage', 'JTemps', 'DTemps', 'CTemps', 
    'ITemps', 'zInstallation', 'CInstallation', 'GMariage', 'zMariage', 
    'DFuner', 'zFuner', 'zBapteme', 'DCene', 'QAdolescence', 'QEnfants', 
    'QJeunes', 'DTous', 'vTous', '_T', '_Y', '_No', 'PK', 'PJ', 'SJ', 
    'VJ', 'VO', 'SW', 'GNoel', 'GPaques', 'GEpiphanie', 'LCar',
    'PPentec', 'GVendredi', 'UEpiphanie', 'CEnfants', 'CJeunes'
}
# On ajoute TOUTES les lettres simples majuscules à la whitelist pour sécurité totale
for c in string.ascii_uppercase:
    TECH_LABELS.add(c)

def decode_xor(in_path):
    with open(in_path, 'rb') as f:
        data = f.read()
    ba = bytearray(data)
    for i in range(len(ba)): ba[i] ^= XOR_VAL
    return bytes(ba)

def extract_fields_from_text(text):
    """Extrait les rubriques FileMaker \\LabelValue."""
    fields = {}
    if '\\' not in text:
        return fields
        
    parts = text.split('\\')
    for p in parts[1:]:
        if not p: continue
        
        # 1. Trouver le plus long label de la whitelist qui matche le début de p
        found_label = None
        # On trie par longueur décroissante pour matcher JTemps avant J.
        for label in sorted(TECH_LABELS, key=len, reverse=True):
            if p.startswith(label):
                found_label = label
                break
        
        if found_label:
            val = p[len(found_label):]
            # Si le label est court (1-2 chars) et est suivi immédiatement d'une majuscule,
            # et que ce label N'EST PAS une known tech label de 2 chars, 
            # on soupçonne que la majuscule suivante appartient au mot.
            # EXCEPTION: Si c'est PK ou QA, on fait confiance.
            tech_2 = {'RY', 'WT', 'HT', 'NT', 'IP', 'LP', 'FB', 'JP', '8T', 'PF', 'SE', 'SF', 'SG', 'PK', 'QA'}
            if len(found_label) == 2 and found_label not in tech_2:
                if len(p) > 2 and p[2].isupper():
                    # On réduit à 1 char
                    found_label = found_label[0]
                    val = p[1:]
            
            val = val.strip()
            if found_label in fields:
                fields[found_label] += " " + val
            else:
                fields[found_label] = val
        else:
            # Fallback passif si rien ne matche du tout
            pass
                
    return fields

def main():
    print("🚀 PASSE 1 — Extraction V8 (The One Fix)")
    
    id_groups = defaultdict(list)
    targets = [
        ("Fiches.lit",     "Fiches.lit"),
        ("Echanges.lit",   "Echanges.lit"),
        ("Sauvegarde.lit", "Sauvegarde.lit")
    ]

    sep_pattern = re.compile(rb'\x1aj\x9b|\[J[A-Z0-9]{2}K[0-9]{4}')

    for label, filename in targets:
        path = os.path.join(SOURCE_DIR, filename)
        if not os.path.exists(path):
            print(f"   ⚠️  {label} introuvable.")
            continue
            
        print(f"   📥 Lecture de {label}...")
        data = decode_xor(path)
        chunks = sep_pattern.split(data)
        
        for k, chunk in enumerate(chunks):
            id_match = re.search(rb'\d{14}', chunk)
            if id_match:
                iid = id_match.group(0).decode('ascii')
                id_groups[iid].append({
                    "src": label,
                    "data": chunk
                })

    print(f"✅ {len(id_groups)} IDs uniques identifiés.")

    records = []
    re_sauvegarde_content = re.compile(rb'\[T\d{14}\](?:XX|X\[|X\]|XY\d|X\w|\]X|\[X|\\X).([\s\S]*)')

    for i, (iid, fragments) in enumerate(id_groups.items()):
        all_fields = {}
        merged_content = ""
        title = ""
        author = ""
        sources = set()

        fragments.sort(key=lambda x: (0 if x['src'] == 'Sauvegarde.lit' else 1))

        for frag in fragments:
            sources.add(frag['src'])
            label_src = frag['src']
            text = frag['data'].decode('mac_roman', errors='replace')
            frag_fields = extract_fields_from_text(text)
            all_fields.update(frag_fields)

            if label_src == "Sauvegarde.lit":
                c_match = re_sauvegarde_content.search(frag['data'])
                if c_match:
                    merged_content += c_match.group(1).decode('mac_roman', errors='replace') + "\n"
                else:
                    idx = frag['data'].find(iid.encode('ascii'))
                    if idx != -1:
                        merged_content += frag['data'][idx+18:].decode('mac_roman', errors='replace') + "\n"
            
            if label_src in ("Fiches.lit", "Echanges.lit"):
                title = frag_fields.get('PF', title)
                author = frag_fields.get('SE', frag_fields.get('SF', frag_fields.get('SG', author)))
                for k, v in frag_fields.items():
                    if k in ('ZV', 'XT', 'TxtPage') or len(str(v)) > 200:
                        if v and str(v).strip() not in merged_content:
                            merged_content += str(v).strip() + "\n"

        records.append({
            "internal_id": iid,
            "title": title.strip(),
            "content": merged_content.strip(),
            "author": author.strip(),
            "all_fields": all_fields,
            "source_files": list(sources)
        })

    records.sort(key=lambda x: x['internal_id'])

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Export : {len(records)} records consolidés.")

if __name__ == "__main__":
    main()
