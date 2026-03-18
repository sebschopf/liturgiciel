# 📒 Journal de Bord des Tâches — LiturgiCielauri

## [2026-03-17] Session : Restauration de la Pureté Absolue

### Matin : Perfectionnement du Pipeline V1 (Cleaning)
- **Objectif** : Atteindre 100% de pureté sur la base du pipeline multi-passes.
- **Réussite** : Restoration de mots comme "Adolescence" via whitelist étendue dans `pass1`.
- **Réussite** : Résurrection de records "ghosts" qui contenaient du texte réel.
- **Limitation** : Découverte d'artefacts persistants comme `X}ZZXy` (ID 23483140000841).

### [2026-03-17 14:45] Phase : Finalisation V2.2 et Pureté Chirurgicale
- **Objectif** : Synchroniser le pipeline sur `id_fiche`, extraire les dates et éliminer les scories binaires résiduelles.
- **Actions** :
    - [x] Correction de `pass2_merge.py` : Utilisation de `id_fiche` (ex-`id_filemaker`).
    - [x] Renforcement de `pass1_extract_v2.py` : Nouveau `clean_value` agressif et extraction de l'année via `YoXXXX`.
    - [x] Optimisation de `pass3_prune.py` : Ajout de patterns ciblés pour `X_Z`, `u1`, `j1`, etc.
    - [x] Raffinement de `pass5_rubriques.py` : Extension du vocabulaire de classification par `types`.
- **Réussite** : Élimination de la majorité des marqueurs structurels visibles en V2.1.
- **Réussite** : Extraction des années de création depuis les labels Yo.
- **Statut** : Pipeline V2.2 opérationnel.

### Status Documentation
- [x] ADR 030 Created (Binary Format Reverse-Engineering)
- [x] Data Mapping Spec Updated (V2 Discoveries)
- [x] Extraction Specification Updated (V2 Workflow)
- [x] Implementation Plan V2.2 (Schema & Purity) Approved
- [x] Task Journal Updated

> [!NOTE]
> **Phase 1** : Exploration & XOR discovery.  
> **Phase 2** : Pipeline V1 (Regex-based cleaning).  
> **Phase 3** : Pipeline V2 (Structural binary parsing).
> **Phase 4** : Pipeline V2.2 (Final Schema & Purity Refinement).
