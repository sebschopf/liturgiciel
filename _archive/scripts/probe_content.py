#!/usr/bin/env python3
import os

XOR_VAL = 0x5A

def decode_xor(in_path):
    if not os.path.exists(in_path): return None
    with open(in_path, 'rb') as f:
        data = f.read()
    return bytes(b ^ XOR_VAL for b in data)

def probe_data(data, search_str):
    pos = data.find(search_str.encode('mac_roman', errors='replace'))
    if pos != -1:
        print(f"✅ Found '{search_str}' at position {pos}")
        chunk = data[max(0, pos-2000):pos+2000]
        with open("probe_context.txt", "w", encoding="utf-8") as f:
            f.write(chunk.decode('mac_roman', errors='replace'))
        print("Context saved to probe_context.txt")
    else:
        print(f"❌ '{search_str}' not found")

source_dir = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN"
path = os.path.join(source_dir, "Echanges.lit")
data = decode_xor(path)

if data:
    probe_data(data, "61.001 & 64.002")
else:
    print("File not found.")
