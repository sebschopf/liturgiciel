#!/usr/bin/env python3
import os
import re
import json

XOR_VAL = 0x5A

def decode_xor(in_path):
    if not os.path.exists(in_path): return None
    with open(in_path, 'rb') as f:
        data = f.read()
    return bytes(b ^ XOR_VAL for b in data)

def find_internal_ids(data, record_num_str):
    # Search for "NoPage" or "NoFiche" or just the number in some context
    # Looking for [A-Z]oXXXX or just XXXX
    results = []
    # Pattern seen: Yo2537 or similar
    pattern = re.compile(record_num_str.encode('ascii') + br'\\8T([0-9]{14})')
    for m in pattern.finditer(data):
        results.append(m.group(1).decode())
    return results

source_dir = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN"
files = ["Fiches.lit", "Echanges.lit"]

mapping = {}
for filename in files:
    data = decode_xor(os.path.join(source_dir, filename))
    if not data: continue
    
    # Check some sample record numbers from PDFs
    for num in ["1", "5", "121", "186", "196", "2537", "2066"]:
        # Normalize to 4 digits if needed for search
        search_nums = [num]
        if len(num) < 4:
            search_nums.append(num.zfill(4))
        
        for s_num in search_nums:
            internal_ids = find_internal_ids(data, s_num)
            if internal_ids:
                if num not in mapping: mapping[num] = {}
                mapping[num][filename] = internal_ids

with open("final_calibration.json", "w") as f:
    json.dump(mapping, f, indent=2)
print("✅ Final calibration saved to final_calibration.json")
