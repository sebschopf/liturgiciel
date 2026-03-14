# ADR 006 : Versionnage (Semantic Versioning)

## État

Accepté

## Contexte

LiturgiCielauri doit produire des releases stables et identifiables. Il faut définir ce qui constitue un changement majeur, mineur ou un correctif — particulièrement critique pour un logiciel biblique où même un patch peut corriger une coquille théologique.

## Décision

Adoption du **Semantic Versioning 2.0.0** (`MAJEUR.MINEUR.CORRECTIF`) avec les règles suivantes :

| Version | Déclencheur | Exemple |
|---|---|---|
| **MAJEUR** | Changement incompatible de base de données ou de structure de données | `2.0.0` |
| **MINEUR** | Nouvelle fonctionnalité (nouveau livre biblique, nouvelle recherche) | `1.2.0` |
| **CORRECTIF** | Fix d'un bug, correction de ponctuation dans les données | `1.2.1` |

### Jalons Gitea correspondants

| Jalon | Objectif |
|---|---|
| `Phase 1 – Extraction` | Avant la v0.1.0 (données fonctionnelles) |
| `Phase 2 – Interface` | Avant la v1.0.0 (logiciel utilisable) |
| `Phase 3 – Publication` | v1.0.0 et au-delà |

### Règles

- Le numéro de version est défini dans `src-tauri/Cargo.toml`.
- Chaque release est taguée dans Git : `git tag v1.0.0`.
- Aucune version `1.x` ne peut être releasée sans que l'ADR 002 (intégrité des données) soit entièrement satisfait.

## Conséquences

- Historique clair et traçable pour les utilisateurs.
- Les jalons Gitea correspondent directement aux versions.
