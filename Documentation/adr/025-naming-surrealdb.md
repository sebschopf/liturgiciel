# ADR 025 : Conventions de Nommage SurrealDB (Tables, Champs, Relations)

## État

Accepté

## Question

> *Comment nommer les objets de base de données dans SurrealDB ?*

## Décision

### 1. Tables

- **Format** : `snake_case`
- **Nombre** : Singulier (comme en Rust)
- **Langue** : Français
- **Exemple** : `fiche`, `verset`, `auteur`

### 2. Champs

- **Format** : `snake_case`
- **Exemple** : `date_creation`, `titre_fiche`

### 3. Relations (Graphe)

- **Format** : `snake_case` (Verbes)
- **Exemple** : `fiche->est_ecrite_par->auteur`

### 4. Langue

- Noms de tables et champs en français, sans accents pour éviter les problèmes d'encodage SQL/SurrealQL.
- Exemple : `categorie` au lieu de `catégorie`.

### 5. Valeurs d'enum dans les champs `ASSERT`

- En minuscules, français, sans accents.
- Exemple : `statut: "publie" | "brouillon"`

### 6. Identifiants significatifs

- Préférer un identifiant lisible quand c'est possible (ex: `fiche:psaume_23`) plutôt qu'un UUID aléatoire pour les données statiques bibliques.

## Référence

- Entités du domaine → ADR 015
- Stratégie de relations → ADR 016
