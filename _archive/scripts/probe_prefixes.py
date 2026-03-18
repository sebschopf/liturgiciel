#!/usr/bin/env python3
import os

XOR_VAL = 0x5A

def decode_xor(in_path):
    if not os.path.exists(in_path): return None
    with open(in_path, 'rb') as f:
        data = f.read()
    return bytes(b ^ XOR_VAL for b in data)

def probe_prefixes(data, search_str):
    target = search_str.encode('mac_roman', errors='replace')
    pos = -1
    while True:
        pos = data.find(target, pos + 1)
        if pos == -1: break
        
        print(f"\n--- Found '{search_str}' at {pos} ---")
        # Context 100 bytes before
        prefix = data[max(0, pos-100):pos]
        print(f"Hex Prefix: {prefix.hex(' ')}")
        print(f"Str Prefix: {prefix.decode('mac_roman', errors='replace')}")

source_dir = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN"
data = decode_xor(os.path.join(source_dir, "Fiches.lit"))

if data:
    probe_prefixes(data, "accueillerons-nous")
else:
    print("File not found.")
