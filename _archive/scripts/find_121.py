#!/usr/bin/env python3
import os
import re

XOR_VAL = 0x5A

def decode_xor(in_path):
    if not os.path.exists(in_path): return None
    with open(in_path, 'rb') as f:
        data = f.read()
    return bytes(b ^ XOR_VAL for b in data)

source_dir = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN"
data = decode_xor(os.path.join(source_dir, "Fiches.lit"))

if data:
    # Search for [A-Z]o0121
    pattern = re.compile(br'[A-Za-z]o0121')
    matches = list(pattern.finditer(data))
    if matches:
        for m in matches:
            print(f"✅ Found marker '{m.group().decode()}' at {m.start()}")
            chunk = data[max(0, m.start()-100):m.end()+100]
            print(f"Context: {chunk.decode('mac_roman', errors='replace')}")
    else:
        print("❌ Marker [A-Z]o0121 not found")
        # Try just '0121' preceded by anything
        pattern2 = re.compile(br'.o0121')
        matches2 = list(pattern2.finditer(data))
        for m in matches2:
            print(f"✅ Found potential marker '{m.group().decode(errors='replace')}' at {m.start()}")
else:
    print("File not found.")
