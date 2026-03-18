#!/usr/bin/env python3
"""
fp7_parser.py — Parseur FP7 corrigé pour LiturgiCielauri

Structure réelle découverte par analyse binaire :
  [fin record précédent] → \\]X + CONTENU → \\PX + TITRE → [u1[j1[n1] → YoXXXX → [timestamps]

Le contenu et le titre sont AVANT l'ID, pas après.
Les champs auteur (\\[w) et source (\\[c) peuvent être avant ou après.
"""

import os
import re
import json
from typing import Dict, Any, cast

XOR_VAL = 0x5A
SRC_DIR = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN"

def xor_decode(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    return bytes(b ^ XOR_VAL for b in data)

def decode_mac_roman(b):
    return b.decode('mac_roman', errors='replace')

def clean_field(text):
    if not text: return ""
    # Retirer les caractères de contrôle sauf saut de ligne
    text = ''.join(c for c in text if ord(c) >= 32 or c in '\n\r')  # type: ignore[misc]
    # Padding
    text = re.sub(r'[zZ]{4,}', '', text)
    text = re.sub(r'P{10,}', '', text)
    # FM garbage strings
    fm_garbage = [
        "Celui qui rappelle les fondements",
        "Ne contient aucune donnÈe",
        "PremiËbre utilisation",
        "Ne pas modifier ce champ",
        "Le texte qui figure sur cette page",
    ]
    for g in fm_garbage:
        if g in text: return ""
    # Préfixes FM
    text = re.sub(r'^S[izÕ¿Ã]([A-ZÀ-ÿ(])', r'\1', text)
    text = re.sub(r'^[\u00c3\u00c6]', '', text)
    text = re.sub(r'^[^a-zA-ZÀ-ÿ0-9\'"\«]', '', text)
    # Suffixes FM : ^PXxx, _VXxx, zV⁄_...
    text = re.sub(r'\^P[A-Za-zÀ-ÿ]+$', '', text)
    text = re.sub(r'_V[A-Za-zÀ-ÿ]+$', '', text)
    text = re.sub(r'[zZ]V?[⁄•¶\s_]+.*$', '', text)
    text = re.sub(r'[\s.z•⁄¶¸˚_]+$', '', text)
    # Normaliser
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def parse_titre(raw):
    """
    Les titres FM: 'Temps ordinaire\VMSous-titre de la variante'
    \V[A-Z~|{@] = séparateur entre titre principal et variante
    """
    m = re.search(r'\\V([A-Z~|{@])(.*)', raw, re.DOTALL)
    if m:
        titre_part = raw[:m.start()].strip()
        variante_part = m.group(2).strip()
        variante_part = re.sub(r'\\[A-Z][A-Za-z]*', '', variante_part)
        return clean_field(titre_part), clean_field(variante_part)
    return clean_field(raw), ""

def extract_records(text_data):
    """
    Extrait les enregistrements en cherchant dans la bonne direction :
    - TITRE et CONTENU : dans la fenêtre AVANT le YoXXXX
    - AUTEUR et SOURCE : peuvent être avant ou après (dans les 2 fenêtres)
    """
    id_pattern = re.compile(r'Yo([0-9]{4})')
    matches = list(id_pattern.finditer(text_data))
    db: Dict[str, Dict[str, Any]] = {}

    for i, m in enumerate(matches):
        idx = m.group(1)
        pos = m.start()

        # --- Fenêtre AVANT l'ID (contenu + titre) ---
        prev_id_end = matches[i-1].end() if i > 0 else 0
        # On remonte jusqu'au YoXXXX précédent (ou début du fichier)
        win_before_start = max(prev_id_end, pos - 3000)
        win_before = text_data[win_before_start:pos]

        # --- Fenêtre APRÈS l'ID (timestamps techniques + auteur/source parfois) ---
        next_id_start = matches[i+1].start() if i < len(matches)-1 else len(text_data)
        win_after_end = min(next_id_start, pos + 2000)
        win_after = text_data[pos:win_after_end]

        cand = {"titre": "", "auteur": "", "source": "", "contenu": ""}

        # ----- TITRE : \P[A-Z] avant l'ID -----
        titre_matches = list(re.finditer(r'\\P[A-Z](.*?)(?=\[u1|\[j1|\[n1|Yo[0-9]|\\P[A-Z]|\\]|$)', win_before, re.DOTALL))
        if titre_matches:
            raw_titre = titre_matches[-1].group(1)
            raw_titre = re.sub(r'\[[a-z][0-9]', '', raw_titre)
            titre, variante = parse_titre(raw_titre)
            cand["titre"] = titre
            cand["variante"] = variante

        # ----- CONTENU : \]X avant l'ID -----
        # \] suivi d'un identificateur de champ puis le texte
        contenu_matches = list(re.finditer(r'\\]([a-zA-Z])(.*?)(?=\\P[A-Z]|\\]|\\[|Yo[0-9]|$)', win_before, re.DOTALL))
        if contenu_matches:
            # Le dernier \]X avant l'ID est le contenu de CE record
            raw_contenu = contenu_matches[-1].group(2)
            raw_contenu = re.sub(r'\[[a-z][0-9]', '', raw_contenu)
            cand["contenu"] = clean_field(raw_contenu)

        # ----- AUTEUR : \[w dans les deux fenêtres -----
        for win in [win_before, win_after]:
            m_a = re.search(r'(?:\\\[w|\\SW)(.*?)(?=\\|\[|Yo[0-9]|\x00|$)', win)
            if m_a:
                a = clean_field(m_a.group(1))
                # Strip embedded FM markers
                a = re.sub(r'\^P.*$', '', a).strip()
                a = re.sub(r'[Y¶⁄zr].*$', '', a).strip()
                if len(a) > len(cand["auteur"]):
                    cand["auteur"] = a

        # ----- SOURCE : \[c dans les deux fenêtres -----
        for win in [win_before, win_after]:
            m_s = re.search(r'(?:\\\[c|\\SC)[A-Z]?(.*?)(?=\\|\[|Yo[0-9]|\x00|$)', win)
            if m_s:
                s = clean_field(m_s.group(1))
                if len(s) > len(cand["source"]):
                    cand["source"] = s

        # Enregistrer dans DB (merge si déjà présent)
        if idx not in db:
            db[idx] = dict(cand)
            entry: Dict[str, Any] = cast(Dict[str, Any], db[idx])
            entry["id"] = idx
            entry["variante"] = cand.get("variante", "")
        else:
            entry = cast(Dict[str, Any], db[idx])
            for field in ["titre", "variante", "auteur", "source", "contenu"]:
                cand_val = str(cand.get(field, ""))
                db_val = str(entry.get(field, ""))
                if len(cand_val) > len(db_val):
                    entry[field] = cand_val

    return db

def deduplicate(records):
    seen = {}
    unique = []
    for r in records.values():
        norm = re.sub(r'[^a-z0-9]', '', r["contenu"].lower())
        sig = r["titre"].lower() + "|" + norm
        if not sig.strip("|"): continue
        if sig not in seen:
            seen[sig] = r
            unique.append(r)
        elif len(r["contenu"]) > len(seen[sig]["contenu"]):
            unique.remove(seen[sig])
            unique.append(r)
            seen[sig] = r
    return unique

def main() -> None:
    files = ["Fiches.lit", "Sauvegarde.lit"]
    all_db: Dict[str, Dict[str, Any]] = {}

    for fname in files:
        path = os.path.join(SRC_DIR, fname)
        if not os.path.exists(path):
            print(f"⚠️  Fichier manquant: {fname}")
            continue

        print(f"🔍 Parsing: {fname}...")
        raw = xor_decode(path)
        text = decode_mac_roman(raw)
        db = extract_records(text)
        print(f"   → {len(db)} IDs trouvés")

        for idx, cand in db.items():
            if idx not in all_db:
                all_db[idx] = dict(cand)
            else:
                all_entry: Dict[str, Any] = cast(Dict[str, Any], all_db[idx])
                for field in ["titre", "auteur", "source", "contenu"]:
                    cand_val = str(cand.get(field, ""))
                    db_val = str(all_entry.get(field, ""))
                    if len(cand_val) > len(db_val):
                        all_entry[field] = cand_val

    print(f"\n📊 Total: {len(all_db)} IDs distincts")

    # Filtrer: au moins un titre ou un contenu non vide
    filtered = {k: v for k, v in all_db.items()
                if (v["contenu"] and len(v["contenu"]) > 10)
                or (v["titre"] and len(v["titre"]) > 3)}

    print(f"📋 Après filtrage: {len(filtered)} fiches avec contenu")

    final = deduplicate(filtered)
    print(f"✨ Après dédoublonnage: {len(final)} fiches uniques")

    out = "fiches_fp7.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)
    print(f"💾 Sauvegardé: {out}")

if __name__ == "__main__":
    main()
