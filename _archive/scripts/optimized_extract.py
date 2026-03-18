#!/usr/bin/env python3
"""
optimized_extract.py — Unified and robust extractor for LiturgiCielauri.
Optimized field boundary detection and advanced sanitization.
"""

import os
import re
import json
import hashlib
from typing import Dict, Any, Optional, cast

XOR_VAL = 0x5A

def decode_mac_roman(b_data):
    return b_data.decode('mac_roman', errors='replace')

def decode_xor(in_path, xor_val=XOR_VAL):
    if not os.path.exists(in_path): return None
    with open(in_path, 'rb') as f:
        data = f.read()
    return bytes(b ^ xor_val for b in data)

def clean_text(text):
    if not text: return ""
    # Remove technical sequences like [a1, [b2, etc.
    text = re.sub(r'\[[a-z][0-9]', ' ', text)
    text = re.sub(r'Z{2,}', ' ', text)
    # Remove FileMaker markers (\ú, \í, Lõ, etc.)
    text = re.sub(r'[\\/][úíëìêñóäãâ…˘¸˛’‘ˇ–—•†]|Lõ|Jõ|Iõ|Oõ|Nõ|Mõ', ' ', text)
    # Technical hex-like codes often found in FM binary text blocks
    text = re.sub(r'_[A-Z0-9]{8,}', ' ', text)
    # Remove the specific garbage pattern [ [... [í...
    text = re.sub(r'\[\s?.[j][öõ].{2,}', ' ', text)
    
    # Remove structural padding strings (z, Z, P, *, .)
    text = re.sub(r'[zZ]{4,}', ' ', text)
    text = re.sub(r'[P]{10,}', ' ', text)
    text = re.sub(r'[\*]{5,}', ' ', text)
    text = re.sub(r'[\.]{10,}', ' ', text)

    # Filter out internal FileMaker help/technical strings
    fm_garbage = [
        "NumÈro identifiant la fiche",
        "unique mÍme si la fiche est transmise",
        "Construit avec le numÈro de l'utilisateur",
        "Champ technique pour la gestion",
        "Ne pas modifier ce champ",
        "NumÈrotation de la fiche",
        "valeurs de 1 ‡ 999",
        "fiches Eglsie",
        "fiches Club",
        "fiches personnelles",
        "Celui qui rappelle les fondements bibliques",
        "Le texte qui figure sur cette page de la fiche semble",
        "Ne contient aucune donnÈe. Ne sert que dans le script",
        "PremiËre utilisation :",
    ]
    for junk in fm_garbage:
        if junk in text:
            return ""

    # Keep printable chars + common whitespace
    text = "".join(c for c in text if ord(c) >= 32 or c in '\n\r\t')
    
    # Normalize whitespace
    text = re.sub(r'\s{2,}', ' ', text)
    
    # Remove IDs accidentally captured in content
    text = re.sub(r'Yo[0-9]{4}', ' ', text)
    
    # Remove specific prefixes often found in FM text blocks
    # Si, Sz, SÕ, S¿ followed by a capital letter or parenthesis
    text = re.sub(r'^S[izÕ¿Ã](\(|[A-ZÀ-ÿ])', r'\1', text)
    
    # Remove long technical numeric strings (T followed by many digits)
    text = re.sub(r'T\d{10,}[^\s]*', ' ', text)
    
    # Remove trailing FM internal markers: ^PXxx, ^VXxx, _VXxx
    text = re.sub(r'[\^_]?[VP][A-Za-z\s]+$', '', text)
    # zV⁄_ pattern and its variants
    text = re.sub(r'[zZ]V?[⁄•¶\s_]+.*$', '', text)
    # _V... at end of string (FM internal variant tag)
    text = re.sub(r'_V[A-Za-zÀ-ÿ]+$', '', text)
    
    # Remove trailing junk symbols
    text = re.sub(r'[\s\.z•⁄¶¸˚_⁄]+$', '', text)
    
    # Remove the Ã prefix (FileMaker field display prefix)
    text = re.sub(r'^Ã', '', text)
    text = re.sub(r'^Æ', '', text)
    
    # Remove leading technical symbols/junk characters
    # Removes everything at the start that isn't a letter, space, or basic quote
    text = re.sub(r'^[^a-zA-ZÀ-ÿ\s\'\"]+', '', text)
    
    # Normalize again after all cleanup
    text = re.sub(r'\s{2,}', ' ', text)
    
    return text.strip()

def get_content_density(text_chunk):
    """Detects the most likely liturgical content block based on keywords and density."""
    parts = re.split(r'[\x00-\x1f\x7f-\x9f\\]{1,}', text_chunk)
    valid_blocks = []
    keywords = ["dieu", "seigneur", "père", "christ", "amen", "nous", "vous", "esprit", "saint", "prière", "fête", "temps"]
    
    for p in parts:
        cleaned = clean_text(p)
        if len(cleaned) > 25:
            # Check for keyword density
            hits = sum(1 for kw in keywords if kw in cleaned.lower())
            
            # Reject blocks with too many "X [ ?" patterns (high ratio of bracket/symbol pairs)
            junk_marks = len(re.findall(r'[\[\]\(\)\{\}\?\!\*\#\%]', cleaned))
            if len(cleaned) > 0 and junk_marks / len(cleaned) > 0.15: # Threshold for junk
                continue

            # A block is valid if it has low non-alphanumeric ratio
            non_alnum = sum(1 for c in cleaned if not c.isalnum() and not c.isspace())
            if len(cleaned) > 0 and (non_alnum / len(cleaned)) < 0.25:
                if hits >= 1 or len(cleaned) > 60:
                    valid_blocks.append(cleaned)
                
    if valid_blocks:
        return max(valid_blocks, key=len)
    return ""

def extract_records(data: bytes, db: Dict[str, Dict[str, Any]]) -> int:
    """Scans for YoXXXX and extracts surrounding metadata/content."""
    pattern = re.compile(br'Yo([0-9]{4})')
    count = 0
    
    matches = list(pattern.finditer(data))
    for i, m in enumerate(matches):
        idx = m.group(1).decode('ascii')
        pos = m.start()
        
        # Window specifically for this ID to avoid overlap
        if i > 0:
            start = max(pos - 1500, matches[i-1].end())
        else:
            start = max(0, pos - 1500)
            
        if i < len(matches) - 1:
            end = min(pos + 5000, matches[i+1].start())
        else:
            end = min(len(data), pos + 5000)
            
        if end - start < 500:
            start = max(0, pos - 200)
            end = min(len(data), pos + 2000)

        chunk: bytes = bytes(data[start:end])  # type: ignore[index]
        text = decode_mac_roman(chunk)
        
        cand: dict[str, str] = {"titre": "", "auteur": "", "source": "", "contenu": ""}  # type: ignore[type-arg]
        
        m_t = re.search(r'\\P[FSQE](.*?)(?:\x1e|\\|\[|\x00|$)', text)
        if m_t:
            t = clean_text(m_t.group(1))
            # Discard titles that look truncated (ends mid-word less than 8 chars after last space)
            if len(t) > 4 or ' ' in t:
                # Also remove trailing FM variable tag appended to title (e.g. zV⁄_ R])
                t = re.sub(r'[zZ]V?[⁄•¶\s_]+.*$', '', t).strip()
                t = re.sub(r'_V[A-Za-zÀ-ÿ]+$', '', t).strip()
                cand["titre"] = t
            
        m_a = re.search(r'(?:\\\[w|\\SW)(.*?)(?:\x1e|\\|\[|\x00|$)', text)
        if m_a:
            a = clean_text(m_a.group(1))
            # Strip embedded title markers from auteur (^P means paragraph/title in FM)
            a = re.sub(r'\^P.*$', '', a).strip()
            # Strip technical codes (Y¶ ..., jõ...)
            a = re.sub(r'[Y¶⁄z⁄r].*$', '', a).strip()
            cand["auteur"] = a
            
        m_c = re.search(r'(?:\\\[c|\\SC)(.*?)(?:\x1e|\\|\[|\x00|$)', text)
        if m_c: cand["source"] = clean_text(m_c.group(1))
            
        content_marker = re.search(r'\\TxtPage(.*?)(?:\x1e|\\|\[|\x00|$)', text)
        if content_marker:
            cand["contenu"] = clean_text(content_marker.group(1))
        
        if len(cand["contenu"]) < 40:
            best_guess = get_content_density(text)
            if len(best_guess) > len(cand["contenu"]):
                cand["contenu"] = str(best_guess)
        
        if idx not in db:
            db[idx] = dict(cand)
            entry: Dict[str, Any] = cast(Dict[str, Any], db[idx])
            entry["id"] = idx
        else:
            entry = cast(Dict[str, Any], db[idx])
            for field in ["titre", "auteur", "source", "contenu"]:
                cand_val: str = str(cand.get(field, ""))
                db_val: str = str(entry.get(field, ""))
                if len(cand_val) > len(db_val):
                    entry[field] = cand_val
        
        count += 1
    return count

def deduplicate(records):
    """Removes duplicates based on content hash."""
    seen_hashes = {}
    unique_records = []
    
    for r in records:
        norm_content = re.sub(r'[^a-z0-9]', '', r["contenu"].lower())
        sig_data = (r["titre"].lower() + "|" + norm_content).strip()
        if not sig_data: continue
        
        if sig_data not in seen_hashes:
            seen_hashes[sig_data] = r
            unique_records.append(r)
        else:
            existing = seen_hashes[sig_data]
            if len(r["contenu"]) > len(existing["contenu"]):
                unique_records.remove(existing)
                unique_records.append(r)
                seen_hashes[sig_data] = r
                
    return unique_records

def main():
    source_dir = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN"
    target_file = "fiches_final_v3.json"
    
    db: Dict[str, Dict[str, Any]] = {}
    files = ["Fiches.lit", "Sauvegarde.lit"]
    
    for f_name in files:
        path = os.path.join(source_dir, f_name)
        if not os.path.exists(path):
            print(f"⚠️ Fichier manquant: {f_name}")
            continue
            
        print(f"🔄 Décodage et scan de {f_name}...")
        data = decode_xor(path)
        if data:
            count = extract_records(data, db)
            print(f"  -> {count} occurrences d'IDs traitées.")

    results = list(db.values())
    print(f"📊 Total IDs trouvés : {len(results)}.")
    
    refined = [r for r in results if len(r["contenu"]) > 30]
    final = deduplicate(refined)
    
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)
        
    print(f"✨ Succès : {len(final)} fiches uniques sauvegardées dans {target_file}")

if __name__ == "__main__":
    main()
