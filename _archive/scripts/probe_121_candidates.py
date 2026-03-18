#!/usr/bin/env python3
import os

XOR_VAL = 0x5A

def decode_xor(in_path):
    if not os.path.exists(in_path): return None
    with open(in_path, 'rb') as f:
        data = f.read()
    return bytes(b ^ XOR_VAL for b in data)

def probe_id(data, internal_id, name):
    target = internal_id.encode('ascii')
    pos = data.find(target)
    if pos != -1:
        # Capture context
        chunk = data[max(0, pos-200):pos+1000]
        text = chunk.decode('mac_roman', errors='replace')
        print(f"--- {name} ({internal_id}) at {pos} ---")
        print(f"Contains 'accueillerons': {'accueillerons' in text}")
        print(f"Snippet: {text[:200]}...")
    else:
        print(f"--- {name} ({internal_id}) NOT FOUND ---")

source_dir = "/home/mous_tik/Documents/LiturgiCiel 2010 WIN"
data = decode_xor(os.path.join(source_dir, "Fiches.lit"))

if data:
    probe_id(data, "23483140003720", "Candidate A")
    probe_id(data, "23483140003809", "Candidate B")
    probe_id(data, "23483140003534", "Candidate C")
else:
    print("File not found.")
