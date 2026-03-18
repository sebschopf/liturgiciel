#!/usr/bin/env python3
import os

XOR_VAL = 0x5A

def decode_xor(in_path):
    if not os.path.exists(in_path): return None
    with open(in_path, 'rb') as f:
        data = f.read()
    return bytes(b ^ XOR_VAL for b in data)

def search_flexible(data, search_str):
    # Try different encodings
    encs = ['mac_roman', 'utf-8', 'latin-1']
    for enc in encs:
        try:
            target = search_str.encode(enc)
            pos = data.find(target)
            if pos != -1:
                return pos, enc
        except:
            continue
    return -1, None

source_dir = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN"
data = decode_xor(os.path.join(source_dir, "Echanges.lit"))

if data:
    # Try just "Singer" or "12 temps"
    for s in ["Singer", "12 temps", "D'après Singer"]:
        pos, enc = search_flexible(data, s)
        if pos != -1:
            print(f"✅ Found '{s}' at {pos} with {enc}")
            # Look around
            chunk = data[max(0, pos-1000):pos+2000]
            with open(f"start_probe_{s.replace(' ', '_')}.txt", "w", encoding="utf-8") as f:
                f.write(chunk.decode('mac_roman', errors='replace'))
        else:
            print(f"❌ '{s}' not found")
else:
    print("File not found.")
