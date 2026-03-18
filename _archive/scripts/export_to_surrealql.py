#!/usr/bin/env python3
"""
export_to_surrealql.py — Générateur d'import pour SurrealDB.
Transforme le JSON consolidé en scripts SurrealQL conformes à l'ADR 015.
"""

import json
import os

def escape_surreal(text):
    if not text: return "''"
    # Echappement simple pour les chaînes SurrealDB
    return "'" + text.replace("'", "\\'") + "'"

def main():
    source_file = "../fiches_final_optimized.json"
    target_file = "../import_liturgy_optimized.surrealql"
    
    if not os.path.exists(source_file):
        print("Fichier source non trouvé.")
        return

    with open(source_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(target_file, "w", encoding="utf-8") as f:
        f.write("-- Import LiturgiCielauri (ADR 015)\n")
        f.write("USE NS liturgiciel DB main;\n\n")
        
        for item in data:
            f_id = f"fiche:{item['id']}"
            f.write(f"CREATE {f_id} CONTENT {{\n")
            f.write(f"  titre: {escape_surreal(item['titre'])},\n")
            f.write(f"  contenu: {escape_surreal(item['contenu'])},\n")
            f.write(f"  auteur: {escape_surreal(item['auteur'])},\n")
            f.write(f"  source: {escape_surreal(item['source'])},\n")
            f.write(f"  langue: 'fr',\n")
            f.write(f"  tags: ['extrait_filemaker']\n")
            f.write(f"}};\n\n")
            
    print(f"✅ Script SurrealQL généré : {target_file} ({len(data)} records)")

if __name__ == "__main__":
    main()
