# ADR 015 : Entités du Domaine Métier

## État

Amendé (2026-03-14)

## Question

> *Quelles sont les tables et champs principaux pour représenter le contenu liturgique ?*

## Décision

### 1. Entité : Fiche

C'est l'unité de base (un chant, une prière, une lecture).

- `titre` : string
- `contenu` : string (markdown)
- `langue` : enum ("fr", "de", "it") (Ajouté le 2026-03-14)
- `auteur_id` : record<auteur>
- `tags` : set<string>

### 2. Entité : Célébration (Culte)

- `date` : datetime
- `lieu` : string
- `type` : enum ("dimanche", "mariage", "enterrement")

### 3. Entité : Dossier

Regroupement logique de fiches (ex: "Cantiques", "Textes Bibliques").

## Historique des Amendements

| Date | Auteur | Changement |
|---|---|---|
| 2026-03-14 | Antigravity | Ajout du champ `langue` à l'entité `Fiche` (ADR-026). |

## Conséquences

- Chaque entité de ce document doit avoir un schéma SurrealQL défini.
- La migration des données FileMaker doit s'aligner sur ces entités.
