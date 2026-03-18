#!/usr/bin/env python3
"""
full_extract.py — Extracteur complet de Sauvegarde.lit v3
Stratégie : jõ (0x6A 0xF6 après XOR) est le délimiteur universelde chaque record.
On extrait de chaque bloc :
  - ID interne : XoNN ou YoNNNN
  - ID échange : ^[lettre]NN.NNN (si présent)
  - Titre : \P[A-Z]
  - Variante : \V[A-Z]
  - Contenu : \]X
  - Auteur : \[w
  - Source : \[c
"""

import re
import json
import os

XOR = 0x5A
SRC = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN/Sauvegarde.lit"
OUT = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN/LiturgiCielauri/fiches_sauvegarde.json"


def xor_decode(path: str) -> bytes:
    with open(path, 'rb') as f:
        raw = f.read()
    return bytes(b ^ XOR for b in raw)


def clean_fm(text: str) -> str:
    if not text:
        return ""
    text = text.replace('\x05\x19', "'")
    text = text.replace('\x05\x18', '\u2018')
    text = text.replace('\x05\x1a', '\u2019')
    text = text.replace('\x05\x11', '\u00ab')
    text = text.replace('\x05\x12', '\u00bb')
    text = text.replace('\x05\x13', '\u2013')
    text = text.replace('\x05\x14', '\u2014')
    text = text.replace('\r', '\n')
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', text)
    text = re.sub(r'[zZ]{3,}', '', text)
    text = re.sub(r'\[u[0-9]+|\[j[0-9]+|\[n[0-9]+', '', text)
    text = re.sub(r'[zZ]V?[⁄•¶\s_]+.*$', '', text)
    text = re.sub(r'_V[A-Za-zÀ-ÿ]+$', '', text)
    text = re.sub(r'XV[A-Za-z]{1,4}$', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


def get_until_marker(text: str, max_len: int = 500) -> str:
    """Extrait jusqu'au prochain marqueur FM ou délimiteur."""
    stop = re.search(
        r'\\[A-Za-z\[\]_^8]|'
        r'\[u[0-9]|\[j[0-9]|\[n[0-9]|'
        r'j\xf6|\x00{3}|ZZZ{5,}',
        text[:max_len]
    )
    return text[:stop.start()].strip() if stop else text[:max_len].strip()


def main() -> None:
    print(f"🔍 Décodage {os.path.basename(SRC)} ({os.path.getsize(SRC)//1024} Ko)...")
    data = xor_decode(SRC)
    text: str = data.decode('mac_roman', errors='replace')

    # Délimiter par jõ (= j + \xf6 en mac_roman après XOR)
    jou_pat = re.compile(r'j\xf6')
    positions = [m.start() for m in jou_pat.finditer(text)]
    positions.append(len(text))
    print(f"   → {len(positions)-1} blocs jõ")

    # Patterns FM
    p_id_int  = re.compile(r'(?:Xo|Yo)([0-9]{1,4})')          # ID interne
    p_id_exch = re.compile(r'\^[A-Za-z\[]([0-9]{1,2}\.[0-9]{1,3}(?:xx)?)') # ID échange
    p_titre   = re.compile(r'\\P([A-Z])')
    p_var     = re.compile(r'\\V([A-Z~|{@])')
    p_contenu = re.compile(r'\\]([a-zA-Z])')
    p_auteur  = re.compile(r'\\(?:\[w|SW)')
    p_source  = re.compile(r'\\(?:\[c|SC)[A-Z]?')

    fiches: dict = {}
    skipped_empty = 0

    for i in range(len(positions) - 1):
        bloc = text[positions[i]:positions[i+1]]

        # ID interne (clé primaire du record)
        m_int = p_id_int.search(bloc)
        if not m_int:
            skipped_empty = skipped_empty + 1
            continue

        prefix = "Xo" if bloc[m_int.start():m_int.start()+2] == "Xo" else "Yo"
        fid = f"{prefix}{m_int.group(1).zfill(4)}"

        # ID échange (optionnel)
        exch_id = ""
        m_exch = p_id_exch.search(bloc)
        if m_exch:
            exch_id = m_exch.group(1)

        # Titre
        titre = ""
        m_t = p_titre.search(bloc)
        if m_t:
            raw = bloc[m_t.end():]
            titre = clean_fm(get_until_marker(raw, 200))

        # Variante
        variante = ""
        m_v = p_var.search(bloc)
        if m_v:
            raw = bloc[m_v.end():]
            variante = clean_fm(get_until_marker(raw, 150))

        # Contenu \]X
        contenu = ""
        m_c = p_contenu.search(bloc)
        if m_c:
            raw = bloc[m_c.end(): m_c.end() + 3000]
            # S'arrêter à \P ou autre fiche
            stop_c = re.search(r'\\P[A-Z]|j\xf6|\[u1', raw)
            contenu = clean_fm(raw[:stop_c.start()] if stop_c else raw[:2000])

        # Auteur
        auteur = ""
        m_a = p_auteur.search(bloc)
        if m_a:
            raw = bloc[m_a.end():]
            auteur = clean_fm(get_until_marker(raw, 120))
            auteur = re.sub(r'\^P.*$', '', auteur).strip()

        # Source
        source = ""
        m_s = p_source.search(bloc)
        if m_s:
            raw = bloc[m_s.end():]
            source = clean_fm(get_until_marker(raw, 150))

        # Est-ce un record utile ?
        if not titre and not contenu and not exch_id:
            skipped_empty = skipped_empty + 1
            continue

        # Merge si déja vu
        if fid not in fiches:
            fiches[fid] = {
                "id": fid,
                "id_echange": exch_id,
                "titre": titre,
                "variante": variante,
                "auteur": auteur,
                "source": source,
                "contenu": contenu,
            }
        else:
            e = fiches[fid]
            if exch_id and not e["id_echange"]: e["id_echange"] = exch_id
            if len(titre) > len(e["titre"]): e["titre"] = titre
            if len(variante) > len(e["variante"]): e["variante"] = variante
            if len(contenu) > len(e["contenu"]): e["contenu"] = contenu
            if len(auteur) > len(e["auteur"]): e["auteur"] = auteur
            if len(source) > len(e["source"]): e["source"] = source

    print(f"   → {len(fiches)} fiches utiles")
    print(f"   → {skipped_empty} blocs sans donnée ignorés")

    xo = sum(1 for k in fiches if k.startswith("Xo"))
    yo = sum(1 for k in fiches if k.startswith("Yo"))
    with_title = sum(1 for f in fiches.values() if f["titre"])
    with_content = sum(1 for f in fiches.values() if f["contenu"])
    with_exch = sum(1 for f in fiches.values() if f["id_echange"])
    print(f"   → Xo: {xo}, Yo: {yo}")
    print(f"   → Avec titre: {with_title}, Avec contenu: {with_content}, Avec ID échange: {with_exch}")

    # Trier : Xo d'abord (anciens), puis Yo (nouveaux)
    def sort_key(fid: str) -> tuple:
        return (0 if fid.startswith("Xo") else 1, int(fid[2:]))

    final = sorted(fiches.values(), key=lambda f: sort_key(f["id"]))

    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(final, fh, indent=2, ensure_ascii=False)
    print(f"💾 Sauvegardé: {OUT}")

    # Aperçu
    print("\n--- Aperçu (5 premiers avec titre) ---")
    shown = 0
    for f in final:
        if f["titre"] and shown < 5:
            exch_str = f" [{f['id_echange']}]" if f["id_echange"] else ""
            print(f"\n[{f['id']}]{exch_str} {f['titre'][:60]}")
            if f["variante"]: print(f"  Var: {f['variante'][:50]}")
            if f["auteur"]:   print(f"  Aut: {f['auteur'][:50]}")
            if f["source"]:   print(f"  Src: {f['source'][:50]}")
            if f["contenu"]:  print(f"  Txt: {f['contenu'][:120]}")
            shown = shown + 1


if __name__ == "__main__":
    main()
