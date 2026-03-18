#!/usr/bin/env python3
"""
import_to_surreal.py — Version finale avec détection de paragraphes haute-densité.
Fusionne Fiches.lit et Sauvegarde.lit pour extraire le patrimoine liturgique propre.
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
    # Nettoyage des séquences techniques localisées
    text = re.sub(r'\[[a-z][0-9]', ' ', text)
    text = re.sub(r'Z{2,}', ' ', text)
    # Suppression des marqueurs FileMaker identifiés (\ú, \í, Lõ, etc.)
    text = re.sub(r'[\\/][úíëìêñóäãâ…˘¸˛’‘ˇ–—•†]|Lõ|Jõ|Iõ|Oõ|Nõ|Mõ', ' ', text)
    # Garde les caractères imprimables
    text = "".join(c for c in text if ord(c) >= 32 or c in '\n\r\t')
    # Normalisation des espaces
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def get_real_content(text_chunk):
    """Extrait le paragraphe le plus 'humain' (français) du chunk."""
    # On découpe par les caractères qui semblent délimiter les champs techniques
    parts = re.split(r'[\x00-\x1f\x7f-\x9f\\\[\]\x1e]{1,}', text_chunk)
    
    # On cherche des blocs avec une haute densité de lettres et de ponctuation française
    valid_blocks = []
    for p in parts:
        c = clean_text(p)
        # Un vrai bloc liturgique a des articles, des majuscules, de la ponctuation.
        if len(c) > 60:
            if any(word in c.lower() for word in ["dieu", "seigneur", "père", " christ", "amen", "nous", "vous"]):
                valid_blocks.append(c)
                
    if valid_blocks:
        return max(valid_blocks, key=len)
    return ""

def extract_from_file(data, db):
    pattern = re.compile(br'Yo([0-9]{4})')
    for m in pattern.finditer(data):
        idx = m.group(1).decode('ascii')
        if idx not in db:
            db[idx] = {"id": idx, "titre": "", "auteur": "", "source": "", "contenu": ""}
        
        # Fenêtre large pour capturer le texte
        chunk = data[max(0, m.start()-1000):m.start()+6000]
        text = decode_mac_roman(chunk)
        
        # Titre
        m_t = re.search(r'\\P[FSQE](.*?)(?:\x1e|\\|\[|$)', text)
        if m_t:
            t = clean_text(m_t.group(1))
            if len(t) > len(db[idx]["titre"]): db[idx]["titre"] = t
            
        # Auteur/Source
        m_a = re.search(r'(?:\\S[WF]|\\\[w)(.*?)(?:\x1e|\\|\[|$)', text)
        if m_a:
            a = clean_text(m_a.group(1))
            if len(a) > len(db[idx]["auteur"]): db[idx]["auteur"] = a
            
        # Contenu
        content = get_real_content(text)
        if len(content) > len(db[idx]["contenu"]):
            db[idx]["contenu"] = content

def main():
    source_dir = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN"
    target_file = "fiches_pour_surreal.json"
    
    db = {}
    for f in ["Fiches.lit", "Sauvegarde.lit"]:
        print(f"🔄 Scan de {f}...")
        data = decode_xor(os.path.join(source_dir, f))
        if data: extract_from_file(data, db)
        
    # Filtrage final
    final = [f for f in db.values() if f["titre"] or len(f["contenu"]) > 40]
    
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)
        
    print(f"✨ Extraction consolidée : {len(final)} fiches validées.")

if __name__ == "__main__":
    main()
