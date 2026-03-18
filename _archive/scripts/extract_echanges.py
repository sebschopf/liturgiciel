#!/usr/bin/env python3
"""
extract_echanges.py — Extracteur complet pour Echanges.lit
Structure découverte :
  - Fiches : r¿/r¡X⁄^[NN.NNN + \_source + \]titre + \H page_ref
  - TxtPage : jö\X⁄\[T62072980000NNN + texte long
  - Encodage : [05][25] = apostrophe, [0d] = newline, ZZZ...= null padding
"""

import re
import json
import os

XOR = 0x5A
SRC = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN/Echanges.lit"
OUT = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN/LiturgiCielauri/fiches_echanges.json"

def xor_decode(path):
    with open(path, 'rb') as f:
        raw = f.read()
    return bytes(b ^ XOR for b in raw)

def decode_fm_text(text):
    """Convertit le texte FileMaker interne en texte lisible."""
    # Apostrophes FM
    text = text.replace('\x05\x19', "'")
    text = text.replace('\x05\x18', '\u2018')
    text = text.replace('\x05\x1a', '\u2019')
    text = text.replace('\x05\x11', '\u00ab')
    text = text.replace('\x05\x12', '\u00bb')
    text = text.replace('\x05\x13', '\u2013')
    text = text.replace('\x05\x14', '\u2014')
    # Caract\u00e8res FM sp\u00e9ciaux
    text = text.replace('\u2021', '')  # \u2021 double dagger = s\u00e9parateur FM
    text = text.replace('\u2020', '')  # \u2020 dagger = s\u00e9parateur FM
    text = text.replace('\u2030', '')  # \u2030 per mille = marqueur FM
    text = text.replace('\u0087', '\u00e0')  # \u0087 -> \u00e0 (Mac Roman \u00e0 mal d\u00e9cod\u00e9)
    # Retour \u00e0 la ligne
    text = text.replace('\r', '\n')
    # Caract\u00e8res de contr\u00f4le
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', text)
    # Padding FM (ZZZ = null bytes XOR'd)
    text = re.sub(r'[zZ]{3,}', '', text)
    text = text.strip()
    return text

def clean_title(text):
    """Nettoie un titre FileMaker : retire les codes variantes XVBA et autres."""
    text = decode_fm_text(text)
    # Supprimer les codes variantes FM : XV[Aa-Zz]+ ou [V[A-Z] ou XV[AB]
    text = re.sub(r'XV[A-Za-z]{1,4}$', '', text)
    text = re.sub(r'\[V[A-Za-z]$', '', text)
    text = re.sub(r'[A-Z]{2,4}$', '', text)  # trailing variant codes
    text = text.strip()
    return text

def clean_source(text):
    """Nettoie une source FM : retire le ] initial et autres artefacts."""
    text = decode_fm_text(text)
    text = re.sub(r'^[\]\[\\]+', '', text)  # ] ou [ en debut
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def clean_contenu(text):
    """Nettoie le texte long d'une fiche : retire le header blob FM."""
    text = decode_fm_text(text)
    # Retirer header blob : s\u00e9quence de majuscules+crochets avant le vrai texte
    text = re.sub(r'^[A-Z\[\]]{5,20}', '', text)
    # Normaliser les sauts de ligne
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def clean(text):
    text = decode_fm_text(text)
    text = re.sub(r'\s{3,}', '\n', text)
    return text.strip()

def extract_field(text, start_pos, max_len=500):
    """Extrait un champ FM à partir d'une position."""
    end = min(start_pos + max_len, len(text))
    chunk = text[start_pos:end]
    # Stopper au prochain marqueur FM ou null
    stop = re.search(r'\\[A-Za-z\[\]]|\x00{3}|ZZZ|X¶|\[V[A-Z]|\[T[0-9]', chunk)
    if stop:
        chunk = chunk[:stop.start()]
    return chunk.strip()

def main():
    print(f"🔍 Parsing Echanges.lit ({os.path.getsize(SRC)//1024} Ko)...")
    raw_data = xor_decode(SRC)
    text = raw_data.decode('mac_roman', errors='replace')

    fiches: dict[str, dict] = {}    # ID → fiche data
    txt_pages: dict[int, str] = {}    # page_num → text content

    # 1. Extraire toutes les fiches via ^[NN.NNN
    fiche_pattern = re.compile(r'\^\[([0-9]{1,2}\.[0-9]{1,3}(?:xx)?)')
    for m in fiche_pattern.finditer(text):
        fid = m.group(1)
        pos = m.start()
        # Fenêtre après l'ID pour trouver les champs
        window: str = text[pos:pos + 600]  # type: ignore[index]

        titre = ""
        source = ""
        categories = []
        page_refs = []

        # Titre : \\]X TEXTE
        m_titre = re.search(r'\\]([A-Z~|a-z])([^\\\[\x00\r]{3,80})', window)
        if m_titre:
            titre = clean_title(m_titre.group(2))

        # Source
        m_src = re.search(r'\\_([^\\\[\x00\r]{3,120})', window)
        if m_src:
            source = clean_source(m_src.group(1))

        # Catégories FM dans blob z]⁄...\\[K
        m_blob_title = re.search(r'\\\[([A-Z])([^\\\[\x00\r\x1a]{3,80})', window)
        if m_blob_title:
            blob_t = clean(m_blob_title.group(2))
            if blob_t and not titre:
                titre = blob_t

        # Ref pages : \\HT62072980000NNN
        for pm in re.finditer(r'\\HT6207298000([0-9]{4})', window):
            page_refs.append(int(pm.group(1)))
        for pm in re.finditer(r'\\NT6207298000([0-9]{4})', window):
            page_refs.append(int(pm.group(1)))

        # Catégories des temps liturgiques (après \\W, juste avant les timestamps)
        m_cat = re.search(r'\\\\([A-Z])([^\\W\[\x00\r]{3,60})', window)
        if m_cat:
            cat_raw = clean(m_cat.group(2))
            if cat_raw:
                categories = [c.strip() for c in re.split(r'[·\r\n]+', cat_raw) if c.strip()]

        if titre or source:
            fiches[fid] = {
                "id": fid,
                "titre": titre,
                "source": source,
                "categories": categories,
                "page_refs": page_refs,
                "contenu": ""
            }

    print(f"   → {len(fiches)} fiches trouvées (^[NN.NNN)")

    # 2. Extraire les TxtPage (textes longs des prières)
    # Pattern : jö\X⁄\[T62072980000NNNN suivi du text
    txtpage_pattern = re.compile(r'j\xf6..{0,8}T6207298000([0-9]{4})')
    for m in txtpage_pattern.finditer(text):
        page_num = int(m.group(1))
        pos = m.end()

        # Chercher le début du texte (après les headers blob)
        window: str = text[pos:pos + 8000]  # type: ignore[index]

        # Le texte commence après un marqueur ...][[X ou ][[...
        # On cherche la séquence de fin du header FM blob
        txt_start = re.search(r'([A-Z]{2}|\[\[)[A-Z]([A-Za-z\u00c0-\u00ff])', window)
        if txt_start:
            # Prendre à partir de là
            raw_txt = window[txt_start.end()-1:]
        else:
            raw_txt = window

        # Stopper à la fin du record (null padding ou prochain record)
        end_match = re.search(r'ZZZ{10,}|jö\\|r¿|r¡', raw_txt)
        if end_match:
            raw_txt = raw_txt[:end_match.start()]

        page_text = clean_contenu(raw_txt)
        if len(page_text) > 30:
            txt_pages[page_num] = page_text

    print(f"   → {len(txt_pages)} TxtPages extraites")

    # 3. Associer les textes aux fiches
    for fid, fiche in fiches.items():
        for pref in fiche["page_refs"]:
            if pref in txt_pages:
                existing: str = fiche["contenu"]
                new_text: str = txt_pages[int(pref)]  # type: ignore[arg-type]
                if len(new_text) > len(existing):
                    fiche["contenu"] = new_text

    # 4. Pour les fiches sans contenu, chercher par proximité dans le fichier
    # (le texte peut être stocké directement dans le record via \\])
    with_content = sum(1 for f in fiches.values() if f["contenu"])
    print(f"   → {with_content} fiches avec texte long associé")

    # 5. Filtrer et dédupliquer
    final = [f for f in fiches.values() if f["titre"] or f["contenu"]]

    # Trier par ID
    def sort_key(f):
        parts = f["id"].split(".")
        try:
            return (int(parts[0]), int(parts[1]))
        except:
            return (999, 999)
    final.sort(key=sort_key)

    # Retirer page_refs des données finales
    for f in final:
        f.pop("page_refs", None)

    print(f"\n✨ {len(final)} fiches uniques")

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(final, f, indent=2, ensure_ascii=False)
    print(f"💾 Sauvegardé: {OUT}")

    # Aperçu
    print("\n--- Aperçu (5 premières avec contenu) ---")
    _with_content: list = [x for x in final if x["contenu"]]
    for f in _with_content[:5]:  # type: ignore[index]
        titre_str: str = str(f['titre'])
        source_str: str = str(f['source'])
        contenu_str: str = str(f['contenu'])
        print(f"\n[{f['id']}] {titre_str}")
        print(f"  Source: {source_str[:60]}")  # type: ignore[index]
        print(f"  Texte: {contenu_str[:200]}")  # type: ignore[index]

if __name__ == "__main__":
    main()
