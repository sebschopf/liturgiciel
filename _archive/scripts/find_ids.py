#!/usr/bin/env python3
import os

XOR_VAL = 0x5A
SEARCH_IDS = [b"Yo0121", b"Yo0186", b"Yo0196", b"Yo0206"]

def check_file(path):
    try:
        with open(path, 'rb') as f:
            data = f.read()
        decoded = bytes(b ^ XOR_VAL for b in data)
        found = []
        for sid in SEARCH_IDS:
            if sid in decoded:
                found.append(sid.decode())
        return found
    except Exception as e:
        return [f"Error: {e}"]

source_dir = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN"
for root, dirs, files in os.walk(source_dir):
    # Avoid recursion into the project dir if it's inside
    if "LiturgiCielauri" in root: continue
    
    for name in files:
        if name.endswith(".lit"):
            path = os.path.join(root, name)
            results = check_file(path)
            if results:
                print(f"{path}: {', '.join(results)}")
