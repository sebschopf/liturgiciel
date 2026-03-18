#!/usr/bin/env python3
"""
parse_echanges.py — Extrait toutes les fiches depuis Echanges.lit
Le format Echanges est plus structuré que Fiches.lit : le texte complet
des prières est stocké en clair (après XOR 0x5A) dans des blocs contigus.
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

def clean(text):
    if not text: return ""
    text = "".join(c for c in text if ord(c) >= 32 or c in '\n\r')  # type: ignore[misc]
    text = re.sub(r'[zZ]{4,}', '', text)
    text = re.sub(r'[\s.z•⁄¶¸˚_⁄]+$', '', text)
    text = re.sub(r'\s{3,}', '\n', text)
    return text.strip()

def main():
    print(f"🔍 Parsing {os.path.basename(SRC)} ({os.path.getsize(SRC)//1024} Ko)...")
    raw = xor_decode(SRC)
    text = raw.decode('mac_roman', errors='replace')

    # Remplacer les caractères non-printables par des délimiteurs
    clean_text = ''.join(c if ord(c) >= 32 or c in '\n\r' else '\x00' for c in text)

    # Trouver les blocs de texte continus (séquences de char lisibles)
    # Un bloc de texte d'échange FM est délimité par des zones binaires
    # Chercher des séquences de texte de plus de 50 caractères
    text_blocks = re.findall(r'[^\x00]{50,}', clean_text)
    print(f"   → {len(text_blocks)} blocs de texte trouvés")

    # Extraire les fiches en cherchant les marqueurs de structure
    # Dans Echanges.lit, les fiches ont souvent ce pattern :
    # - Un titre en première ligne
    # - Suivi du texte de la prière
    # - Délimités par des zones binaires

    fiches = []
    fiche_id = 1

    # Approche 1 : chercher les IDs Yo
    yo_pattern = re.compile(r'Yo([0-9]{4})')
    yo_matches = list(yo_pattern.finditer(text))
    print(f"   → IDs Yo trouvés: {len(yo_matches)}")

    if yo_matches:
        # Même logique que fp7_parser : contenu AVANT le YoXXXX
        for i, m in enumerate(yo_matches):
            idx = m.group(1)
            pos = m.start()

            prev_end = yo_matches[i-1].end() if i > 0 else 0
            next_start = yo_matches[i+1].start() if i < len(yo_matches)-1 else len(text)

            win_before = text[max(prev_end, pos-4000):pos]  # type: ignore[index]
            win_after = text[pos:min(next_start, pos+500)]  # type: ignore[index]

            # Chercher le texte long dans la fenêtre avant
            # Dans Echanges.lit, le texte est moins fragmenté
            # Extraire toutes les séquences lisibles > 20 chars
            readable = re.findall(r'[^\x00\x01-\x1f]{20,}', win_before)
            readable = [s.strip() for s in readable if len(s.strip()) > 20]

            # Le texte principal = la séquence la plus longue
            long_texts = sorted(readable, key=len, reverse=True)
            contenu = ""
            titre = ""
            auteur = ""
            source = ""

            for t in long_texts:
                t_clean = clean(t)
                # Filtrer les chaînes techniques
                if re.search(r'T[0-9]{10}', t): continue
                if re.search(r'^[A-Z0-9]{15,}$', t): continue

                # FM field markers
                m_titre = re.search(r'\\P[A-Z](.*?)(?:\\V|\\P|$)', t, re.DOTALL)
                if m_titre and not titre:
                    titre = clean(m_titre.group(1))
                    variante_m = re.search(r'\\V[A-Z~](.*?)(?:\\|$)', t, re.DOTALL)
                    if variante_m:
                        titre += " — " + clean(variante_m.group(1))

                m_auteur = re.search(r'\\[w(.*?)(?:\\|\[|$)', t, re.DOTALL)
                if m_auteur and not auteur:
                    auteur = clean(m_auteur.group(1))[:80]  # type: ignore[index]

                m_source = re.search(r'\\[c[A-Z]?(.*?)(?:\\|\[|$)', t, re.DOTALL)
                if m_source and not source:
                    source = clean(m_source.group(1))[:120]  # type: ignore[index]

                # Si c'est du texte pur (pas de marqueurs), c'est le contenu
                if len(t_clean) > 50 and not contenu:
                    # Vérifier que c'est du texte français (au moins quelques mots)
                    words = len(t_clean.split())
                    if words >= 5:
                        contenu = t_clean

            if contenu or titre:
                fiches.append({
                    "id": f"E{idx}",
                    "titre": titre,
                    "auteur": auteur,
                    "source": source,
                    "contenu": contenu,
                })

    else:
        # Approche 2 : si pas d'IDs Yo, extraire les blocs de texte directement
        print("   → Pas d'IDs Yo, extraction par blocs de texte...")
        for i, bloc in enumerate(text_blocks):
            bloc_clean = clean(bloc)
            if len(bloc_clean) > 80:
                lines = [l.strip() for l in bloc_clean.split('\n') if l.strip()]
                if lines:
                    fiches.append({
                        "id": f"E{fiche_id:04d}",
                        "titre": lines[0][:100] if lines else "",  # type: ignore[index]
                        "auteur": "",
                        "source": "",
                        "contenu": '\n'.join(lines[1:]) if len(lines) > 1 else bloc_clean,  # type: ignore[index,misc]
                    })
                    fiche_id = int(fiche_id) + 1  # type: ignore[arg-type]

    print(f"\n📊 {len(fiches)} fiches extraites")

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(fiches, f, indent=2, ensure_ascii=False)
    print(f"💾 Sauvegardé: {OUT}")

    # Aperçu des 5 premières
    print("\n--- Aperçu ---")
    for r in fiches[:5]:  # type: ignore[index]
        print(f"[{r['id']}] {r['titre'][:60]}")  # type: ignore[index]
        print(f"  {r['contenu'][:120]}")  # type: ignore[index]
        print()

if __name__ == "__main__":
    main()
