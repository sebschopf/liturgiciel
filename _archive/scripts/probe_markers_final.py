#!/usr/bin/env python3
import os

XOR_VAL = 0x5A

def decode_xor(in_path):
    if not os.path.exists(in_path): return b""
    with open(in_path, 'rb') as f:
        data = f.read()
    return bytes(b ^ XOR_VAL for b in data)

def probe_markers(data, search_str):
    target = search_str.encode('mac_roman', errors='replace')
    pos = data.find(target)
    if pos != -1:
        print(f"\n--- Found '{search_str}' at {pos} ---")
        ahead = data[max(0, pos-150):pos]
        # Look for the last '\' or '[' marker
        print(f"Hex Context: {ahead.hex(' ')}")
        print(f"Str Context: {ahead.decode('mac_roman', errors='replace')}")
    else:
        print(f"--- '{search_str}' NOT FOUND ---")

source_dir = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN"
fiches = decode_xor(os.path.join(source_dir, "Fiches.lit"))
echanges = decode_xor(os.path.join(source_dir, "Echanges.lit"))

print("Checking Fiches.lit:")
probe_markers(fiches, "accueillerons-nous")
probe_markers(fiches, "grande maison")

print("\nChecking Echanges.lit:")
probe_markers(echanges, "Explorateurs de Dieu")
probe_markers(echanges, "1.11.002")
