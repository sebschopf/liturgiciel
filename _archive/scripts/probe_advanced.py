#!/usr/bin/env python3
import os
import re

XOR_VAL = 0x5A

def decode_xor(in_path):
    if not os.path.exists(in_path): return None
    with open(in_path, 'rb') as f:
        data = f.read()
    return bytes(b ^ XOR_VAL for b in data)

def probe_around(data, search_str):
    search_bytes = search_str.encode('mac_roman', errors='replace')
    pos = data.find(search_bytes)
    if pos == -1:
        print(f"❌ '{search_str}' not found")
        return

    print(f"✅ Found '{search_str}' at {pos}")
    # Search for YoXXXX, XoXXXX, etc. in a large window
    window = data[max(0, pos-2000):pos+2000]
    
    # Pattern: a capital letter, 'o', followed by 4 digits
    matches = re.findall(br'[A-Z]o[0-9]{4}', window)
    print(f"Markers found in window: {matches}")
    
    # Show context
    print("--- Context ---")
    print(window.decode('mac_roman', errors='replace'))

source_dir = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN"
data = decode_xor(os.path.join(source_dir, "Fiches.lit"))

if data:
    probe_around(data, "agitation")
else:
    print("File not found.")
