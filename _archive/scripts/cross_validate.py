#!/usr/bin/env python3
import os
import re
import json

XOR_VAL = 0x5A

calibration_targets = {
    "1": "Explorateurs de Dieu",
    "2": "qu’une parole d’espérance",
    "3": "Seigneur, tu es notre Père",
    "5": "Bienvenue à vous tous",
    "15": "Rien ne pourra nous séparer",
    "24": "Seigneur, ami des hommes",
    "32": "Dieu notre Père, toi qui nous aimes",
    "121": "accueillerons-nous",
    "186": "Ta grande maison",
    "196": "Seigneur, nous voici devant toi",
    "206": "Dieu notre Père, nous te prions",
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
files = ["Fiches.lit", "Echanges.lit"]

results = {}

for filename in files:
    data = decode_xor(os.path.join(source_dir, filename))
    if not data: continue
    
    for pdf_id, phrase in calibration_targets.items():
        t_bytes = phrase.encode('mac_roman', errors='replace')
        pos = -1
        while True:
            pos = data.find(t_bytes, pos + 1)
            if pos == -1: break
            
            # Find all internal IDs within 2000 bytes before
            window = data[max(0, pos-2000):pos]
            ids = re.findall(br'[0-9]{14}', window)
            if ids:
                last_id = ids[-1].decode()
                if pdf_id not in results: results[pdf_id] = []
                results[pdf_id].append({
                    "file": filename,
                    "internal_id": last_id,
                    "pos": pos,
                    # Capture 20 bytes before the ID to find the "active" flag
                    "flags": data[data.find(ids[-1])-20:data.find(ids[-1])].hex(' ')
                })

with open("calibration_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("✅ Calibration results saved to calibration_results.json")
