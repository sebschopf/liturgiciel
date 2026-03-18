# ADR 027 : Stratégie d'Extraction des Données FileMaker

## État

Validé / Implémenté (Success du Reverse Engineering Binaire)

## Question

> *Comment extraire les données des fichiers .lit (FileMaker 11) avec une fidélité de 100% alors que l'interface FileMaker est verrouillée ?*

## Contexte

Les fichiers `.lit` (FileMaker 11 / `HBAM7`) utilisent un masquage XOR 0x5A et un encodage Mac Roman. Initialement, une approche par virtualisation (Windows 10 + FileMaker 21) a été envisagée à cause de la complexité du parsing binaire. Cependant, l'analyse binaire a permis de décoder intégralement la structure des données, rendant l'extraction programmatique plus performante et plus flexible que l'export manuel.

## Décision

### 1. Stratégie Nominale : Pipeline Python Multi-Passes
Abandon de la virtualisation. La solution retenue est un pipeline automatisé garantissant une fidélité de 100% par rapport à la source binaire.

### 2. Architecture du Pipeline (6 Passes)
Le pipeline a été affiné en 6 passes pour séparer clairement l'extraction brute, la fusion sémantique et le nettoyage des encodages.

1.  **Passe 1 : Extraction Brute Universelle** (`pass1_extract_v2.py`) : 
    *   **Découverte décisive** : Identification du séparateur binaire universel `\x1aj\x9b` (souvent précédé de `[.`) présent dans tous les fichiers.
    *   **Zéro-Fragmentation** : Groupement systématique par ID de 14 chiffres avant toute extraction de champ.
2.  **Passe 2 : Fusion & Consolidation** (`pass2_merge.py`) : Liage des textes complets (`Sauvegarde.lit`) aux métadonnées (`Fiches.lit`). Résolution des liens `WT` (`Echanges.lit`). Fallback de titre sémantique.
3.  **Passe 3 : Élagage des Artefacts** (`pass3_prune.py`) : Suppression des résidus FileMaker (`ZV`, `]NNNNN`, padding `K` et `Z`).
4.  **Passe 4 : Correction Encodage** (`pass4_encoding.py`) : Correction des glyphes Mac Roman (é, è, ç, etc.).
5.  **Passe 5 : Normalisation Rubriques** (`pass5_rubriques.py`) : Mapping vers le vocabulaire contrôlé (Public, Temps liturgique).
6.  **Passe 6 : Export SurrealDB** (`pass6_export.py`) : Formatage JSON final prêt pour l'import.

### 3. Mécanique de Fidélité
- **Calibration** : Validation systématique contre un set de 24 PDFs de référence.
- **Traceability** : Conservation des données brutes dans le champ `raw_fields` pour chaque fiche.

## Conséquences

- **Avantages** : 100% automatisé, aucune dépendance Windows, reproductibilité totale, nettoyage fin des métadonnées binaires.
- **Inconvénients** : Nécessite une maintenance des expressions régulières en cas de découverte de nouveaux types de records FileMaker.

## Documentation de Référence

- [ADR 028 : Schéma Source FileMaker](./028-filemaker-source-schema.md)
- [ADR 029 : Schéma Cible SurrealDB](./029-normalized-data-schema.md)
- [ADR 030 : Spécification du Format Binaire](./030-filemaker-binary-format.md)
- [dossier pdf](../../../pdf)
