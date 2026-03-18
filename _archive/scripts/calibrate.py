#!/usr/bin/env python3
import os
import re

XOR_VAL = 0x5A

# Phrases unique to each PDF for calibration
# pdf_map = { "id_from_filename": "unique_phrase" }
calibration_targets = {
    "1": "Explorateurs de Dieu", # Found near Yo2044
    "2": "qu’une parole d’espérance",
    "3": "Seigneur, tu es notre Père",
    "5": "Bienvenue à vous tous",
    "15": "Rien ne pourra nous séparer",
    "24": "Seigneur, ami des hommes",
    "32": "Dieu notre Père, toi qui nous aimes",
    "121": "accueillerons-nous",
    "186": "grande maison",
    "196": "Seigneur, nous voici devant toi",
    "1500": "Jean-Michel Sordet",
    "1700": "institution du mariage",
    "2000": "accident d’avion",
    "2200": "François Paccaud",
    "2528": "Dieu de tendresse et de pitié",
    "2537": "Nathalie Schopfer", 
    "2066": "agitation"
}

def decode_xor(in_path):
    if not os.path.exists(in_path): return None
    with open(in_path, 'rb') as f:
        data = f.read()
    return bytes(b ^ XOR_VAL for b in data)

source_dir = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN"
data = decode_xor(os.path.join(source_dir, "Fiches.lit"))

if data:
    mapping = {}
    for pdf_id, phrase in calibration_targets.items():
        # Try finding phrase (MacRoman)
        t_bytes = phrase.encode('mac_roman', errors='replace')
        pos = data.find(t_bytes)
        if pos != -1:
            # Find closest 14-digit ID
            window = data[max(0, pos-1500):pos+1500]
            ids = re.findall(br'[0-9]{14}', window)
            mapping[pdf_id] = {
                "pos": pos,
                "internal_ids": [i.decode() for i in set(ids)]
            }
        else:
            mapping[pdf_id] = "NOT_FOUND"
    
    import json
    with open("calibration_map.json", "w") as f:
        json.dump(mapping, f, indent=2)
    print("✅ Calibration mapping saved to calibration_map.json")
else:
    print("❌ Fiches.lit not found")
