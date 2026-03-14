# ADR 011 : Automatisation CI/CD avec Gitea Actions

## État
Proposé

## Contexte
Les tests définis dans l'ADR 005 doivent s'exécuter automatiquement à chaque Pull Request pour garantir qu'aucune régression n'est introduite — en particulier pour la fidélité des données bibliques. Cela requiert une infrastructure CI (Intégration Continue) configurée dans Gitea.

## Décision

### Phase 1 – Validation manuelle (actuel)
Pendant la Phase 1 (extraction des données), pas d'exécuteur (runner) CI configuré. Les tests sont exécutés manuellement par l'agent IA avant chaque PR.

### Phase 2 – CI automatisée (à configurer avant le premier commit de code)
Un workflow Gitea Actions sera défini dans `.gitea/workflows/ci.yml`.

#### Pipeline de validation d'une PR
```
Trigger: pull_request vers main
Étapes :
  1. cargo fmt --check      → Vérification du style Rust
  2. cargo clippy           → Analyse statique du code Rust
  3. cargo test             → Tests unitaires backend
  4. npm run check          → TypeScript strict (SvelteKit)
  5. npm run test           → Tests Vitest (frontend)
```

#### Pipeline de release (tag `v*`)
```
Trigger: push d'un tag v*
Étapes :
  1. Exécuter tous les tests CI
  2. cargo tauri build --target windows
  3. cargo tauri build --target linux
  4. Créer une Release Gitea avec les artefacts
```

### Infrastructure
- L'exécuteur (runner) Gitea Actions sera installé sur la machine locale de développement.
- Les secrets de signature Windows seront stockés dans Gitea Secrets (ADR 009).

## Conséquences
- Phase 1 : zéro configuration requise, tests manuels.
- Phase 2 : un fichier `.gitea/workflows/ci.yml` à créer (PR dédiée avec `Kind/Feature` + `Kind/Testing`).
- Aucune release ne peut être créée sans passer tous les tests.
