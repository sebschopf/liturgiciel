# ADR 017 : Organisation du Code et Structure des Dossiers

## État
Accepté

## Contexte
Maintenant que les couches sont définies (ADR 013), la question est : **où physiquement chaque fichier doit-il vivre ?** Une structure de dossiers ambiguë entraîne des incohérences entre développeurs (et agents IA). Ce document est prescriptif : il n'y a pas d'interprétation possible.

## Décision

### Règle générale
> Un fichier se range là où sa **couche** le place, et dans le sous-dossier correspondant à son **domaine métier**.

Domaines métier : `fiches`, `dossiers`, `cultes`, `utilisateurs`.

### Structure prescriptive

```
LiturgiCielauri/
│
├── .gitea/                        ← Gouvernance Gitea (ADR 010, 011)
│   ├── workflows/ci.yml
│   ├── pull_request_template.md
│   └── issue_template.md
│
├── src-tauri/                     ← BACKEND (couche Rust)
│   ├── src/
│   │   ├── main.rs                ← Point d'entrée Tauri uniquement
│   │   ├── errors.rs              ← AppError centralisé (voir ADR 018)
│   │   ├── commands/              ← Points d'entrée IPC : 1 fichier = 1 domaine
│   │   │   ├── mod.rs
│   │   │   ├── fiches.rs
│   │   │   ├── dossiers.rs
│   │   │   └── cultes.rs
│   │   ├── services/              ← Logique métier pure (+ tests #[cfg(test)])
│   │   │   ├── mod.rs
│   │   │   ├── fiches.rs
│   │   │   ├── dossiers.rs
│   │   │   └── cultes.rs
│   │   ├── models/                ← Structures Rust serde (Serialize/Deserialize)
│   │   │   ├── mod.rs
│   │   │   ├── fiche.rs
│   │   │   ├── dossier.rs
│   │   │   └── culte.rs
│   │   └── db/                    ← Accès SurrealDB uniquement
│   │       ├── mod.rs
│   │       ├── connection.rs      ← Initialisation DB
│   │       └── schema.surql       ← Schéma SurrealQL (source vérité technique)
│   ├── Cargo.toml                 ← Versions verrouillées (ADR 001)
│   └── rustfmt.toml               ← Config linter Rust (ADR 003)
│
├── src/                           ← FRONTEND (couche Svelte 5)
│   ├── app.css                    ← Tokens CSS globaux (Open Props, ADR 001)
│   ├── lib/
│   │   ├── components/            ← Composants Svelte réutilisables
│   │   │   ├── Fiche.svelte       ← Avec Fiche.test.ts associé (ADR 005)
│   │   │   └── ...
│   │   ├── stores/                ← État global réactif (Svelte $state, ADR 018)
│   │   │   ├── fiches.ts
│   │   │   └── navigation.ts
│   │   ├── api/                   ← Wrappers invoke() Tauri (seul accès au backend)
│   │   │   └── index.ts
│   │   └── shortcuts.ts           ← Raccourcis clavier (ADR 014)
│   └── routes/                    ← Pages SvelteKit (routage défini dans ADR 018)
│       ├── +layout.svelte
│       ├── +page.svelte
│       └── ...
│
├── Documentation/
│   └── adr/                       ← Source de vérité des décisions
│
├── CHANGELOG.md                   ← Tenu à jour par l'auteur (ADR 008)
├── .eslintrc.json                 ← Linting TypeScript (ADR 003)
├── prettier.config.js             ← Formatage (ADR 003)
├── .markdownlint.json             ← Linting docs (ADR 003)
└── package.json                   ← Dépendances frontend versionnées (ADR 001)
```

## Conséquences
- Un agent IA ou développeur sait immédiatement où chercher ou créer un fichier.
- Toute exception à cette structure doit être documentée dans le commit qui la crée.

## Référence
- Conventions de nommage des fichiers frontend → ADR 023
- Conventions de nommage des fichiers backend → ADR 024
