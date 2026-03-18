#!/usr/bin/env python3
"""
explore_secondary_lit.py — PASSE 1b : Exploration des fichiers .lit secondaires
=================================================================================
Sonde les fichiers .lit non encore traités pour détecter leur format binaire
et extraire leurs données brutes exploitables.

Fichiers cibles :
  Dossiers.lit       → structure hiérarchique des dossiers
  Temps.lit          → vocabulaire des temps liturgiques
  Catalogues.lit     → organisation des catalogues
  Liens.lit          → relations entre fiches
  Transfert/Transfert.lit → fichier d'export/transfert

Sortie : liturgi_secondary_raw.json
=================================================================================
Usage :
    python3 scripts/explore_secondary_lit.py
"""

import os
import re
import json

_SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_SCRIPT_DIR)
_SOURCE_DIR  = os.path.dirname(_PROJECT_DIR)   # LiturgiCiel 2010 WIN

OUTPUT_FILE  = os.path.join(_PROJECT_DIR, "liturgi_secondary_raw.json")

XOR_VAL = 0x5A

SECONDARY_FILES = [
    "Dossiers.lit",
    "Temps.lit",
    "Catalogues.lit",
    "Liens.lit",
    os.path.join("Transfert", "Transfert.lit"),
]


def decode_xor(path):
    if not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        data = f.read()
    return bytes(b ^ XOR_VAL for b in data)


def detect_format(data):
    """Détecte le format d'un fichier .lit décodé."""
    # Format A : séparateur [J.YK + 4 chiffres
    if re.search(rb'\[J.YK[0-9]{4}', data):
        count = len(re.findall(rb'\[J.YK[0-9]{4}', data))
        return 'A', count

    # Format B : séparateur [Y1X ou [Y2X
    if re.search(rb'\[Y[12]X', data):
        count = len(re.findall(rb'\[Y[12]X', data))
        return 'B', count

    # Inconnu : chercher des patterns de texte français
    text_sample = data[:2000].decode('mac_roman', errors='replace')
    has_french = bool(re.search(r'[éèêàùôïîûœ]', text_sample))
    return 'UNKNOWN', 0 if not has_french else -1


def extract_format_a(data, filename):
    """Extrait les records de format A ([J.YK)."""
    records = []
    pattern = re.compile(rb'\[J.YK[0-9]{4}')
    matches = list(pattern.finditer(data))

    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(data)
        chunk = data[start:end]

        id_match = re.search(rb'[0-9]{14}', chunk)
        internal_id = id_match.group(0).decode() if id_match else None

        # Extraire les champs \Label{valeur}
        fields = {}
        parts = chunk.split(b'\\')
        for part in parts[1:]:
            if not part:
                continue
            lm = re.match(rb'([A-Za-z0-9_]{1,20})', part)
            if lm:
                label = lm.group(1).decode('mac_roman', errors='replace')
                val_bytes = part[len(lm.group(1)):]
                val = val_bytes.decode('mac_roman', errors='replace')
                val = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', val)
                val = re.sub(r'\s+', ' ', val).strip()
                if val and len(val) > 1:
                    fields[label] = val

        # Extraire un sample texte lisible
        sample = chunk.decode('mac_roman', errors='replace')
        sample = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', sample)
        sample = re.sub(r'\s+', ' ', sample).strip()[:200]

        records.append({
            "internal_id": internal_id,
            "all_fields":  fields,
            "sample":      sample,
            "source_file": filename,
        })

    return records


def extract_format_b(data, filename):
    """Extrait les records de format B ([Y1X/[Y2X)."""
    records = []
    sep = re.compile(rb'\[Y[12]X')
    chunks = sep.split(data)

    for chunk in chunks:
        id_match = re.search(rb'\[T(\d{14})\]', chunk)
        if not id_match:
            continue

        internal_id = id_match.group(1).decode()
        after_id = chunk[id_match.end():]

        # Type de record
        type_match = re.match(rb'(..)', after_id)
        rec_type = type_match.group(1).decode('mac_roman', errors='replace') if type_match else '??'

        # Contenu si XX ou X[
        content = ''
        cm = re.match(rb'(?:XX|X\[).([\\s\\S]*)', after_id)
        if cm:
            raw = cm.group(1)
            content = raw.decode('mac_roman', errors='replace')
            content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', content)
            content = re.sub(r'\s+', ' ', content).strip()[:300]

        records.append({
            "internal_id": internal_id,
            "rec_type":    rec_type,
            "content":     content,
            "source_file": filename,
        })

    return records


def explore_unknown(data, filename):
    """Extrait un aperçu lisible d'un fichier de format inconnu."""
    decoded = data.decode('mac_roman', errors='replace')
    # Trouver les séquences de texte lisible
    readable = re.findall(r'[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9\s\'\-\.,;:!?]{10,}', decoded)

    return [{
        "source_file": filename,
        "format":      "UNKNOWN",
        "sample_texts": readable[:30],
    }]


# ─── Main ─────────────────────────────────────────────────────────────────────

print("🔍 Passe 1b — Exploration des fichiers .lit secondaires")
print()

all_results = {}
summary = []

for rel_path in SECONDARY_FILES:
    abs_path = os.path.join(_SOURCE_DIR, rel_path)
    fname    = os.path.basename(rel_path)

    print(f"📄 {fname}...")

    data = decode_xor(abs_path)
    if data is None:
        print(f"   ⚠️  Introuvable : {abs_path}")
        summary.append({"file": fname, "status": "missing"})
        continue

    print(f"   → {len(data):,} octets bruts décodés")

    fmt, count = detect_format(data)
    print(f"   → Format détecté : {fmt}  ({count} séparateurs)")

    if fmt == 'A':
        records = extract_format_a(data, fname)
    elif fmt == 'B':
        records = extract_format_b(data, fname)
    else:
        records = explore_unknown(data, fname)

    print(f"   → {len(records)} records extraits")

    # Afficher un aperçu des labels trouvés
    if fmt == 'A' and records:
        all_labels = set()
        for r in records:
            all_labels.update(r.get('all_fields', {}).keys())
        if all_labels:
            print(f"   → Labels découverts : {sorted(all_labels)[:20]}")

    all_results[fname] = records
    summary.append({
        "file":    fname,
        "format":  fmt,
        "records": len(records),
        "status":  "ok",
    })
    print()

# Export
output = {
    "summary":  summary,
    "records":  all_results,
}

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"✅ Export → {OUTPUT_FILE}")
print()
print("📊 Résumé :")
for s in summary:
    status = s['status']
    if status == 'missing':
        print(f"   ❌  {s['file']} — introuvable")
    else:
        print(f"   ✅  {s['file']} — format {s['format']} — {s['records']} records")
