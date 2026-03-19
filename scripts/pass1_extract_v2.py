import os
import json
import re
from collections import defaultdict

# --- Configuration ---
SOURCE_DIR = "LitugiCiel"
FILES = ["Fiches.lit", "Sauvegarde.lit", "Echanges.lit"]
OUTPUT_FILE = "liturgi_raw_v2.json"
XOR_VAL = 0x5A

# Binary Markers
RECORD_SEP_RE = re.compile(rb'\x40\x30\xc1|\x01\x10.{2}\x11.{4}')

# Enhanced Label Whitelist
TECH_LABELS = {
    'RY', 'WT', 'HT', 'NT', 'IP', 'LP', 'yP', 'FB', 'JP', '8T', 'PF', 
    'SE', 'SF', 'SG', 'PP', 'GV', 'GP', 'GN', 'LC', 'UE', 'GE', 'QA',
    'TT', 'XT', 'ZV', 'VN', 'VN30', 'TxtPage', 'JTemps', 'DTemps', 'CTemps', 
    'ITemps', 'zInstallation', 'CInstallation', 'GMariage', 'zMariage', 
    'DFuner', 'zFuner', 'zBapteme', 'DCene', 'QAdolescence', 'QEnfants', 
    'QJeunes', 'DTous', 'vTous', '_T', '_Y', '_No', '_V', 'PK', 'PJ', 'SJ', 
    'VJ', 'VO', 'SW', 'GNoel', 'GPaques', 'GEpiphanie', 'LCar',
    'PPentec', 'GVendredi', 'UEpiphanie', 'CEnfants', 'CJeunes',
    'G', 'T', 'V', 'R', 'P', 'S', 'O', 'J', 'U', 'A', 'B', 'C', 'D', 'E', 'F', 'H', 'I', 'K', 'L', 'M', 'N'
}
SORTED_LABELS = sorted(TECH_LABELS, key=len, reverse=True)

def decode_xor(data):
    ba = bytearray(data)
    for i in range(len(ba)): ba[i] ^= XOR_VAL
    return bytes(ba)

def is_garbage(text):
    """Detect if a string is likely technical debris using academic heuristics."""
    if not text: return True
    text_str = str(text).strip()
    if len(text_str) < 2: return True
    
    # 1. Natural Language Proof (Glue Words)
    # Natural French text has a high density of these "glue" words.
    GLUE_WORDS = {'de', 'le', 'la', 'et', 'que', 'en', 'un', 'une', 'des', 'les', 'pour', 'dans', 'par', 'sur', 'ce', 'au'}
    words = re.findall(r'\b[a-zA-ZÀ-ÿ]{2,}\b', text_str.lower())
    if not words: return True
    
    glue_count = sum(1 for w in words if w in GLUE_WORDS)
    
    # Heuristic: If it's long (>30 chars) and has NO glue words, it's 99% junk.
    if len(text_str) > 30 and glue_count == 0:
        return True
    
    # Ratio of glue words to total words
    glue_ratio = glue_count / len(words)
    if len(words) > 5 and glue_ratio < 0.10: # Liturgical text is very glue-rich
        return True

    # 2. Character Density & Diversity
    clean_text = re.sub(r'\s', '', text_str)
    letters = re.sub(r'[^a-zA-ZÀ-ÿ]', '', clean_text)
    if not letters: return True
    
    density_ratio = len(letters) / len(clean_text)
    unique_chars = len(set(letters.lower()))
    diversity_ratio = unique_chars / len(letters) if letters else 0
    
    # If it's mostly random letters (alphabet soup), diversity is high but it's weird
    # But binary patterns often repeat: ZS.ZZHZZ...
    if len(letters) > 30 and diversity_ratio < 0.20: return True # Too repetitive
    
    # 3. Vowel Density (French is vowel-rich: ~40%)
    vowels = re.sub(r'[^aeiouyàâéèêëîïôûù]', '', letters.lower())
    vowel_ratio = len(vowels) / len(letters)
    if len(letters) > 10 and (vowel_ratio < 0.20 or vowel_ratio > 0.60):
        return True # Technical debris has weird vowel distribution
    
    # 4. Uppercase explosion (Acronyms/Technical IDs)
    uppers = re.sub(r'[^A-Z]', '', clean_text)
    if len(uppers) / len(clean_text) > 0.70 and len(clean_text) > 8: return True

    return False

def clean_value(text, aggressive=False):
    if not text: return ""
    
    # V2.4 — ACADEMIC UNICODE WHITELISTING (Pre-processing)
    # Drop EVERYTHING except basic Latin and French. Technical symbols are pure noise here.
    text = re.sub(r'[^a-zA-ZÀ-ÿ0-9\s.,\'?!:;()\-—«»\"\/<>\x80-\xff\u0152\u0153\u2026\u2018\u2019\u201C\u201D]', ' ', text)

    # Strip any 14-digit ID and surrounding junk anywhere if aggressive
    if aggressive:
        # HARD TRUNCATION: Some fields have massive technical indices at the end
        trunc_markers = [
            r'z\s+[\xf0\uf000]', # z 
            r'z_{1,3}\s+[a-z]\s+', # z__ b l b
            r'\[ZZ\[',           # Common index start
            r'\[Xr',             # Record info start
            r'\[[A-Z] \[[A-Z]', # Pattern of multiple single-letter tags
            r'\s+[A-Z]\s+[A-Z]\s+[A-Z]\s+[A-Z]\s+[A-Z]', # Rapid-fire capital letters
            r'[A-Z]{5,}',        # Long Uppercase sequences (often technical soup)
        ]
        for marker in trunc_markers:
            match = re.search(marker, text)
            if match:
                text = text[:match.start()]
                break

        # Multi-pass cleaning to handle nested markers
        for _ in range(2):
            # Pattern to catch technical IDs like \8T56526470001650T or similar
            text = re.sub(r'\\?[A-Z]{1,2}\d{14}[A-Z]?', ' ', text)
            # Catch bare 14-digit IDs
            text = re.sub(r'\d{14}', ' ', text)
            # Catch [...] markers like [u1[j1[n4
            text = re.sub(r'\[[a-zA-Z]\d+', ' ', text)
            # Catch technical markers like Yo2004, Yo2005
            text = re.sub(r'Yo\d{4}', ' ', text)
            # Catch technical tags like X_Z, _X, Xã, X_
            text = re.sub(r'z?[A-Z]_[A-Z]', ' ', text)
            text = re.sub(r'\b_?[A-Z]\b', ' ', text)
            text = re.sub(r'\b[A-Z]_', ' ', text)
            # Catch specific patterns seen in output
            text = re.sub(r'[XYZ]Z[XYZ][A-Z\d]', ' ', text) # Catch XZZX, ZZXT, ZZXJ etc.
            text = re.sub(r'z[A-Z][a-z0-9]?', ' ', text) 
            # Remove internal technical pointers like \PF, \SO, etc.
            text = re.sub(r'\\[A-Z]{1,3}', ' ', text)

    # Strip common binary padding/technical prefixes at start
    text = re.sub(r'^[\[\]XYZ \t\n\r]{1,15}', '', text)
    
    return text.strip()

def extract_year(text):
    """Attempt to find a year in YoXXXX format."""
    if not text: return None
    match = re.search(r'Yo(\d{4})', text)
    if match:
        return match.group(1)
    return None

def extract_date(text):
    """Attempt to find a date in DD/MM/YYYY or similar formats."""
    if not text: return None
    match = re.search(r'(\d{1,2}[./]\d{1,2}[./]\d{2,4})', text)
    if match:
        return match.group(1).replace('.', '/')
    return None

def parse_hybrid_record(chunk_decoded):
    fields = {}
    parts = re.split(rb'[\x06\x01\x02\x0b\x1c\x1d\x1e\x1f]', chunk_decoded)
    
    for part in parts:
        if not part: continue
        try:

            # Pre-decode fix for apostrophes often stored as 0x05 0x19 in FileMaker
            part = part.replace(b'\x05\x19', b"'")
            part = part.replace(b'\x05\x01', b"'")
            part = part.replace(b'\x05', b"'")
            payload_text = part.decode('mac_roman', errors='replace')

        except:
            continue
            
        found_label = None
        for label in SORTED_LABELS:
            # Check for label at the very beginning of the part
            if payload_text.startswith(label):
                found_label = label
                break
        
        if found_label:
            # PROFESSIONAL HEURISTIC: A label is usually either:
            # 1. More than 1 char (PF, RY, etc.)
            # 2. A single char followed by a non-alphanumeric or non-lowercase char (e.g. S[...)
            # We must NOT strip a single char if it's followed by a lowercase letter (e.g. "Seigneur")
            should_strip = True
            if len(found_label) == 1:
                if len(payload_text) > 1:
                    next_char = payload_text[1]
                    # If it's a lowercase letter or some common French characters, don't strip
                    if next_char.islower() or next_char in ' àâéèêëîïôûùç':
                        should_strip = False
            
            if should_strip:
                val = payload_text[len(found_label):]
            else:
                val = payload_text
                
            val_clean = clean_value(val)
            if val_clean:
                if found_label in fields:
                    if val_clean not in fields[found_label]:
                        fields[found_label] += " | " + val_clean
                else:
                    fields[found_label] = val_clean
        else:
            val_clean = clean_value(payload_text)
            if val_clean and len(val_clean) > 5:
                if "UNKNOWN" in fields: fields["UNKNOWN"] += " | " + val_clean
                else: fields["UNKNOWN"] = val_clean
            
    return fields

def run_v2_extraction():
    all_records = {}

    for filename in FILES:
        path = os.path.join(SOURCE_DIR, filename)
        if not os.path.exists(path): continue
            
        print(f"Processing {filename}...")
        with open(path, "rb") as f: raw_data = f.read()
            
        raw_chunks = RECORD_SEP_RE.split(raw_data)
        print(f"  Found {len(raw_chunks)} segments")
        
        for raw_chunk in raw_chunks:
            if len(raw_chunk) < 20: continue
            chunk_decoded = decode_xor(raw_chunk)
            
            # Find ID
            record_id = None
            id_match = re.search(rb'\d{14}', chunk_decoded)
            if id_match: 
                record_id = id_match.group().decode()
            
            parsed = parse_hybrid_record(chunk_decoded)
            
            if not record_id:
                for tid_field in ["_T", "8T", "HT"]:
                    if tid_field in parsed:
                        m = re.search(r'\d{14}', parsed[tid_field])
                        if m: record_id = m.group(); break

            if record_id:
                if record_id not in all_records:
                    all_records[record_id] = {
                        "id_fiche": record_id, 
                        "titre": None, "contenu": "", "auteur": None, "source": None,
                        "date_creation": None, "date_modification": None,
                        "raw_fields": {}, "source_files": set()
                    }
                rec = all_records[record_id]
                rec["source_files"].add(filename)
                
                # TITRE priority (Aggressive cleaning)
                titles_to_check = [parsed.get("PF"), parsed.get("P"), parsed.get("TT")]
                for raw_t in titles_to_check:
                    if raw_t:
                        clean_t = clean_value(raw_t, aggressive=True)
                        # Reject if it looks like technical stuff, too short, or garbage
                        if clean_t and not clean_t.startswith('\\') and len(clean_t) > 3:
                            if not is_garbage(clean_t):
                                rec["titre"] = clean_t
                                break

                # CONTENT mapping (Aggressive cleaning & Deduplication)
                content_labels = ["TxtPage", "ZV", "XT", "G", "T", "V"]
                for k in content_labels:
                    if parsed.get(k):
                        v_clean = clean_value(parsed[k], aggressive=True)
                        if len(v_clean) > 20 and v_clean not in rec["contenu"]:
                            # Deduction: if the new block is a prefix or suffix of existing, skip
                            if v_clean in rec["contenu"] or rec["contenu"] in v_clean:
                                if len(v_clean) > len(rec["contenu"]):
                                    rec["contenu"] = v_clean
                            else:
                                rec["contenu"] = (rec["contenu"] + "\n" + v_clean).strip()
                
                # Special case: UNKNOWN content if it's long and seems "clean"
                if parsed.get("UNKNOWN") and len(parsed["UNKNOWN"]) > 100:
                    u_clean = clean_value(parsed["UNKNOWN"], aggressive=True)
                    if len(u_clean) > 50 and u_clean not in rec["contenu"]:
                        # Heuristic: if u_clean has lots of spaces and few backslashes, it's likely text
                        if u_clean.count(' ') > 5 and u_clean.count('\\') < 3:
                            rec["contenu"] = (rec["contenu"] + "\n" + u_clean).strip()

                # AUTHOR mapping
                for al in ["SE", "SF", "SG"]:
                    if parsed.get(al):
                        rec["auteur"] = clean_value(parsed[al], aggressive=True)
                        break
                
                # DATE extraction
                if not rec["date_creation"]:
                    rec["date_creation"] = extract_date(parsed.get("LP")) or extract_year(str(parsed)) or extract_date(rec["contenu"])
                if not rec["date_modification"]:
                    rec["date_modification"] = extract_date(parsed.get("RY"))

                # Add all parsed fields to raw_fields (for Pass 5)
                for k, v in parsed.items():
                    if k != "UNKNOWN" and len(k) < 10:
                        if k in rec["raw_fields"]:
                            if v not in rec["raw_fields"][k]:
                                rec["raw_fields"][k] += " | " + v
                        else:
                            rec["raw_fields"][k] = v

    final_output = []
    for rid in sorted(all_records.keys()):
        data = all_records[rid]
        data["source_files"] = list(data["source_files"])
        # Final safety check: if everything is empty or nonsense, skip
        if data["titre"] or len(data["contenu"]) > 20:
            final_output.append(data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
    
    print(f"\nExtraction V2.2 complete. Saved {len(final_output)} records to {OUTPUT_FILE}")
    if final_output:
        with_title = sum(1 for r in final_output if r.get("titre"))
        with_content = sum(1 for r in final_output if len(r.get("contenu", "")) > 10)
        print(f"  Records with Title: {with_title}, Content: {with_content}")

if __name__ == "__main__":
    run_v2_extraction()
