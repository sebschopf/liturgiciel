# ADR 022 : Performance Délibérée du Code

## État

Accepté

## Question

> *Quelles sont les cibles de performance et comment les garantir ?*

## Contexte

LiturgiCielauri doit être réactif, même avec des milliers de fiches. L'utilisateur ne doit jamais percevoir de
latence lors de la recherche biblique.

## Décision

### Règle fondamentale

**"No blocking the UI thread"**. Toutes les opérations lourdes (calculs, accès DB) se font dans le backend Rust.

### Stratégies par couche

#### Rust

- Utilisation de `rayon` pour le parallélisme si nécessaire sur les gros volumes de données.
- Utilisation des itérateurs et évitement des copies inutiles de mémoire (`Zero-copy` quand possible).

#### Svelte 5

- Utilisation des `Runes` (`$state`, `$derived`) pour une réactivité fine et performante.
- Évitement des re-rendus massifs de listes (utilisation de `{#each ... (key)}`).

#### SurrealDB

- Utilisation systématique d'index sur les champs de recherche fréquents (titre, tags, langue).
- Utilisation des relations de graphe pour éviter les JOINs SQL coûteux.

## Métriques cibles

- **Démarrage à froid** : < 1 seconde.
- **Recherche plein texte** : < 100ms.
- **Navigation entre fiches** : < 50ms (instantanéité perçue).

## Conséquences

- Le suivi des métriques sera centralisé dans un tableau de bord (ADR 028 futur).
- Tests de charge obligatoires lors de la Phase 2.
