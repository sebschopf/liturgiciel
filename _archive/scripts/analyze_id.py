#!/usr/bin/env python3
import os
import re

XOR_VAL = 0x5A

def decode_xor(in_path):
    if not os.path.exists(in_path): return None
    with open(in_path, 'rb') as f:
        data = f.read()
    return bytes(b ^ XOR_VAL for b in data)

def analyze_id_occurrences(data, internal_id):
    id_bytes = internal_id.encode('ascii')
    matches = list(re.finditer(id_bytes, data))
    print(f"--- Analysis for Internal ID {internal_id} ---")
    print(f"Found {len(matches)} occurrences.")
    
    for i, m in enumerate(matches):
        print(f"\nOccurrence {i+1} at {m.start()}:")
        # Look at 200 bytes around the ID to find state flags
        # Often FileMaker uses specific bytes before/after for status
        context_raw = data[max(0, m.start()-50):m.end()+150]
        print(f"   Hex: {context_raw.hex(' ')}")
        # Check if the text of "accueillerons" is nearby
        if b"accueillerons" in data[m.start():m.start()+4000]:
             print(f"   ✅ CONTAINS TARGET TEXT")
        else:
             print(f"   ❌ NO TARGET TEXT")

source_dir = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN"
data = decode_xor(os.path.join(source_dir, "Echanges.lit"))

if data:
    targets = ["Singer"]
    for t in targets:
        print(f"\nSearching for target: '{t}'")
        t_bytes = t.encode('mac_roman')
        pos = data.find(t_bytes)
        if pos != -1:
            # Look for ANY 14-digit number nearby
            window = data[max(0, pos-1500):pos+1500]
            matches = re.findall(br'[0-9]{14}', window)
            if matches:
                 unique_ids = list(set(m.decode() for m in matches))
                 print(f"Potential internal IDs found: {unique_ids}")
                 for uid in unique_ids:
                     analyze_id_occurrences(data, uid)
            else:
                 print(f"No 14-digit ID found near '{t}'")
        else:
            print(f"'{t}' not found")
else:
    print("File not found.")
