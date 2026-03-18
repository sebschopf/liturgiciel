#!/usr/bin/env python3
"""
convert.py — Extracteur haute-fidélité pour LiturgiCielauri (ADR 027)
Version 6 : Scan complet et exhaustif par ID Yo.
"""

import os
import re
import json

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
    text = re.sub(r'\[[a-z][0-9]', ' ', text)
    text = re.sub(r'Z{2,}', ' ', text)
    text = "".join(c for c in text if ord(c) >= 32 or c in '\n\r\t')
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def extract_all(data, out_dict):
    """Scan tout le fichier et capture chaque YoXXXX."""
    pattern = re.compile(br'Yo([0-9]{4})')
    for m in pattern.finditer(data):
        idx = m.group(1).decode('ascii')
        if idx not in out_dict:
            out_dict[idx] = {"id": idx, "titre": "", "auteur": "", "source": "", "contenu": ""}
        
        # On capture les strings dans un voisinage de 2000 octets
        chunk = data[max(0, m.start()-500):m.start()+2000]
        text = decode_mac_roman(chunk)
        
        # Métadonnées
        m_a = re.search(r'\\\[w(.*?)(?:\x1e|\\|\[|$)', text)
        if m_a: 
            v = clean_text(m_a.group(1))
            if len(v) > len(out_dict[idx]["auteur"]): out_dict[idx]["auteur"] = v
        
        m_s = re.search(r'\\\[c(.*?)(?:\x1e|\\|\[|$)', text)
        if m_s:
            v = clean_text(m_s.group(1))
            if len(v) > len(out_dict[idx]["source"]): out_dict[idx]["source"] = v

        m_t = re.search(r'\\P[FSQ](.*?)(?:\x1e|\\|\[|$)', text)
        if m_t:
            v = clean_text(m_t.group(1))
            if len(v) > len(out_dict[idx]["titre"]): out_dict[idx]["titre"] = v
            
        # Contenu brute
        parts = re.split(r'[\x00-\x1f\\\[\]]', text)
        cands = [p for p in parts if len(p) > 30]
        if cands:
             best = max(cands, key=len)
             if len(best) > len(out_dict[idx]["contenu"]):
                 out_dict[idx]["contenu"] = clean_text(best)

def main():
    source_dir = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN"
    target_file = "fiches_exhaustive.json"
    
    db = {}
    for fname in ["Fiches.lit", "Sauvegarde.lit"]:
        path = os.path.join(source_dir, fname)
        print(f"📖 Traitement de {fname}...")
        data = decode_xor(path)
        if data: extract_all(data, db)
        
    results = list(db.values())
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(f"✨ Succès : {len(results)} fiches extraites dans {target_file}")

if __name__ == "__main__":
    main()
