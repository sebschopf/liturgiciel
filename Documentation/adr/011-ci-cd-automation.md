# ADR 011 : Automatisation CI/CD avec Gitea Actions

## État

Proposé

## Contexte

Les tests définis dans l'ADR 005 doivent s'exécuter automatiquement à chaque PR pour garantir qu'aucune
régression n'est introduite. Cela requiert une infrastructure CI configurée dans Gitea.

## Décision

### Phase 1 – Validation manuelle (actuel)

Pendant la Phase 1 (extraction des données), pas d'exécuteur (runner) CI configuré.
Les tests sont exécutés manuellement par l'agent IA avant chaque PR.

### Phase 2 – CI automatisée (à configurer avant le premier commit de code)

Un workflow Gitea Actions sera défini dans `.gitea/workflows/ci.yml`.

#### Pipeline de validation d'une PR

```yaml
Trigger: pull_request vers main
Étapes :
  1. cargo fmt --check      → Vérification du style Rust
  2. cargo clippy           → Analyse statique du code Rust
  3. cargo test             → Tests unitaires backend
  4. npm run check          → TypeScript strict (SvelteKit)
  5. npm run test           → Tests Vitest (frontend)
```

#### Pipeline de release (tag `v*`)

```yaml
Trigger: push d'un tag v*
Étapes :
  1. Exécuter tous les tests CI
  2. cargo tauri build --target windows
  3. cargo tauri build --target linux
  4. Créer une Release Gitea avec les artefacts
```

### Infrastructure

- L'exécuteur (runner) Gitea Actions sera installé localement.
- Les secrets de signature Windows seront stockés dans Gitea Secrets (ADR 009).

## Conséquences

- Aucune release ne peut être créée sans passer tous les tests.
