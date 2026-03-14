# ADR 016 : Stratégie de Relations (Champ direct vs Graphe SurrealDB)

## État

Accepté

## Question

> *Comment modéliser les liens entre fiches, auteurs et célébrations ?*

## Contexte

SurrealDB est une base de données multi-modèle (document et graphe). Nous devons choisir quand utiliser un
champ `record<ID>` (document) et quand utiliser une relation `->relation->` (graphe).

## Décision

### 1. Relations Directes (Record ID)

Utiliser un champ direct pour les relations 1:1 ou 1:N simples et stables.

- Exemple : `fiche.auteur_id`.

### 2. Relations de Graphe (`RELATE`)

Utiliser le graphe pour les relations N:M ou celles nécessitant des métadonnées sur le lien lui-même.

- Exemple : `celebration->contient->fiche`.

### Cas particulier : L'ordre dans `moment_fiche`

La relation `contient` entre une célébration et une fiche doit porter un champ `ordre` pour respecter la liturgie.

- `celebration` : dans quelle célébration ?
- `fiche` : quelle fiche ?
- `ordre` : position dans le culte (1, 2, 3...).

## Alternatives considérées

- **Tout en tables de relation (style SQL)** : Rejeté. Perd l'avantage de performance du graphe SurrealDB.
- **Tout en documents imbriqués** : Rejeté. Rend la mise à jour des auteurs ou des tags trop complexe.

## Conséquences

- Le schéma technique SurrealQL doit explicitement définir les permissions sur les arêtes (edges).
- La recherche peut utiliser des traversées de graphe (`SELECT ->contient->fiche.* FROM celebration`).
