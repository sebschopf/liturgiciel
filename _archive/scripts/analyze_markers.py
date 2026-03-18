#!/usr/bin/env python3
import os
import re
from collections import Counter

XOR_VAL = 0x5A

def decode_xor(in_path):
    if not os.path.exists(in_path): return None
    with open(in_path, 'rb') as f:
        data = f.read()
    return bytes(b ^ XOR_VAL for b in data)

source_dir = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN"
data = decode_xor(os.path.join(source_dir, "Fiches.lit"))

if data:
    # Find all patterns like [A-Z]o[0-9]{4}
    all_markers = re.findall(br'[A-Z]o[0-9]{4}', data)
    counter = Counter(m.decode()[:2] for m in all_markers)
    print("Marker distribution:")
    for prefix, count in counter.items():
        print(f"{prefix}: {count}")
    
    # Also find IDs around the "accueillerons-nous" area
    pos = data.find("accueillerons-nous".encode('mac_roman'))
    if pos != -1:
        window = data[max(0, pos-2000):pos+2000]
        local_markers = re.findall(br'[A-Z]o[0-9]{4}', window)
        print(f"\nMarkers around 'accueillerons-nous': {local_markers}")
else:
    print("File not found.")
