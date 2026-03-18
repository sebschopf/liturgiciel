#!/usr/bin/env python3
import os

XOR_VAL = 0x5A
SEARCH_STRS = [
    "1.12.2006",
    "1.61.2002",
    "61.001 & 64.002"
]

def check_file(path):
    try:
        with open(path, 'rb') as f:
            data = f.read()
        decoded = bytes(b ^ XOR_VAL for b in data)
        found = []
        for s in SEARCH_STRS:
            s_bytes = s.encode('mac_roman', errors='replace')
            if s_bytes in decoded:
                found.append(s)
                # print(f"✅ Found {s} in {path} at {decoded.find(s_bytes)}")
        return found
    except Exception as e:
        # print(f"Error reading {path}: {e}")
        return []

source_dir = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN"
for root, dirs, files in os.walk(source_dir):
    if "LiturgiCielauri" in root: continue
    for name in files:
        if name.endswith(".lit"):
            path = os.path.join(root, name)
            results = check_file(path)
            if results:
                print(f"{path}: {', '.join(results)}")
