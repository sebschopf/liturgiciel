#!/usr/bin/env python3
import os

XOR_VAL = 0x5A

def decode_xor(in_path):
    if not os.path.exists(in_path): return None
    with open(in_path, 'rb') as f:
        data = f.read()
    return bytes(b ^ XOR_VAL for b in data)

source_dir = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN"
data = decode_xor(os.path.join(source_dir, "Fiches.lit"))

if data:
    target = "accueillerons-nous".encode('mac_roman')
    pos = data.find(target)
    if pos != -1:
        window = data[max(0, pos-2000):pos+2000]
        text = window.decode('mac_roman', errors='replace')
        print("--- Context around 'accueillerons-nous' ---")
        if "121" in text:
            print("✅ Found '121' in context!")
            # Find exact position of 121 in window
            subpos = text.find("121")
            print(f"   Context: ...{text[subpos-50:subpos+50]}...")
        else:
            print("❌ '121' not found in this window.")
            # Search for other numbers
            import re
            nums = re.findall(r'\d+', text)
            print(f"   Numbers found: {nums}")
else:
    print("File not found.")
