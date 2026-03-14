# ADR 003 : Standards de Développement, Qualité du Code & Linters

## État
Accepté

## Contexte
Le projet LiturgiCielauri doit être maintenable sur le long terme par des humains ou des agents IA. Une cohérence absolue dans la structure du code, les conventions de nommage et la qualité du style est non négociable.

## Décision

### 1. Langages & Frameworks
- **Backend** : Rust (Tauri). Utilisation de types stricts et gestion d'erreurs explicite (`Result<T, E>`). Jamais de `.unwrap()` en production.
- **Frontend** : TypeScript strict (SvelteKit). Option `"strict": true` dans `tsconfig.json`. Aucun `any` toléré.

### 2. Linters & Formateurs (Qualité Automatisée)

#### Backend Rust
| Outil | Version | Rôle | Commande | Critère de succès |
|---|---|---|---|---|
| `rustfmt` | Bundlé avec `rustup` | Formatage | `cargo fmt` | 0 différence |
| `clippy` | Bundlé avec `rustup` | Analyse statique | `cargo clippy -- -D warnings` | 0 warning |
| `cargo audit` | `cargo-audit 0.21+` | Vulnérabilités | `cargo audit` | 0 critique |

#### Frontend TypeScript / Svelte 5
| Outil | Version | Rôle | Commande | Critère de succès |
|---|---|---|---|---|
| `eslint` | `^9.0` | Analyse statique | `npm run lint` | 0 erreur |
| `prettier` | `^3.0` | Formatage | `npm run format` | 0 différence |
| `svelte-check` | `^4.0` | Vérification Svelte 5 | `npm run check` | 0 erreur de type |
| `@sveltejs/vite-plugin-svelte` | `^4.0` | Build Svelte 5 | Via `vite` | Build réussi |

#### Documentation Markdown
| Outil | Version | Rôle | Commande | Critère de succès |
|---|---|---|---|---|
| `markdownlint-cli` | `^0.39` | Style Markdown | `markdownlint Documentation/**/*.md` | 0 violation |

### 3. Configuration des linters
- `rustfmt.toml` à la racine du projet pour la config Rust.
- `.eslintrc.json` et `prettier.config.js` à la racine du projet.
- `.markdownlint.json` pour la documentation.
- Ces fichiers de config sont versionnés dans Git et font loi.

### 4. Organisation & Traçabilité
- **Logique Métier** : Réside exclusivement dans le backend Rust (`src-tauri/src/services/`).
- **Traçabilité des Commits** : Aucun commit sans référence à un ADR.
- **Communication Frontend/Backend** : Exclusivement via `commands` Tauri (voir ADR 013).

### 5. Base de Données (SurrealDB)
- Requêtes centralisées dans `src-tauri/src/services/`.
- Utilisation du langage **SurrealQL** via le SDK Rust officiel.
- Aucune requête SurrealQL dans le frontend ou dans les `commands`.

### 6. Style CSS
- Variables CSS (Custom Properties) exclusivement pour tous les tokens de design (couleurs, tailles, espacements).
- Aucune valeur magique (ex: `color: #3a2f1b`) hors du fichier de tokens.
- Respect du design éditorial (voir ADR futur : Interface & UX).

## Conséquences
- Qualité du code vérifiable automatiquement à chaque PR (ADR 011).
- Un agent IA peut auditer le code et détecter les violations de standard.
- Zéro dette technique accumulée silencieusement.
