# ADR 020 : Code as Documentation — Quand et comment commenter

## État

Accepté

## Question

> *Quelles sont les règles pour les commentaires dans le code ?*

## Contexte

Le code doit être sa propre documentation. Cependant, certaines décisions complexes ou contextes métiers
nécessitent des explications.

## Décision

### Règle fondamentale

Le principe directeur est : **Ne commentez pas ce que fait le code, commentez POURQUOI il le fait.**

### 1. Commentaires de documentation (Rust/TS)

- Toute fonction publique ou service complexe DOIT avoir un bloc de documentation.
- **Rust** : Utiliser `///`.
- **TypeScript** : Utiliser `/** ... */`.
- Expliquer les invariants métiers.

### 2. Commentaires internes

- À utiliser uniquement pour expliquer une optimisation obscure ou une contrainte héritée.

### 3. Liens vers ADR

- Si une logique complexe découle d'un ADR, inclure la référence (ex: `// Voir ADR-015`).

## Conséquences

- Toute fonction `pub` sans documentation pourra être signalée.
- La documentation technique peut être générée automatiquement.

## Référence

- Conventions de nommage frontend → ADR 023
- Conventions de nommage backend → ADR 024
