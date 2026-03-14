# ADR 025 : Conventions de Nommage SurrealDB (Tables, Champs, Relations)

## État
Accepté

## Question
> *Quelles sont les conventions de nommage dans le schéma SurrealDB ?*

## Décision

| Élément | Convention | Exemple |
|---|---|---|
| Nom de table | `snake_case` singulier, français | `fiche`, `temps_liturgique`, `moment_liturgique` |
| Nom de champ | `snake_case`, français | `date_creation`, `temps_liturgique`, `est_partage` |
| Relation (table) | `snake_case`, verbe passé ou préposition | `est_variante_de`, `dans_dossier`, `tagged` |
| Index | `idx_` + table + champ(s) | `idx_fiche_titre`, `idx_fiche_statut` |
| Identifiant SurrealDB | `table:identifiant` | `fiche:11004`, `temps_liturgique:avent` |

### Langue
- Noms de tables et champs en **français** (domaine métier).
- Exception : termes techniques SurrealDB sans équivalent (`TYPE RELATION`, `SCHEMAFULL`) restent en anglais.

### Valeurs d'enum dans les champs `ASSERT`
- En minuscules, français, sans accent (contrainte SurrealQL) :
  ```surql
  ASSERT $value IN ["officielle", "personnelle", "protegee"]
  ```

### Identifiants significatifs
- Préférer un identifiant lisible quand c'est possible : `temps_liturgique:avent` plutôt qu'un UUID.
- Pour les entités utilisateur (fiches, dossiers) : ID auto-généré par SurrealDB.

## Référence
- Entités du domaine → ADR 015
- Stratégie de relations → ADR 016
