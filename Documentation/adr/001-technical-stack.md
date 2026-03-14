# ADR 001 : Sélection de la Pile Technique (Stack)

## État

Accepté

## Contexte

LiturgiCiel 2010 est une application FileMaker Pro 10 obsolète, fermée, non portable et sans documentation. Elle doit être entièrement réécrite pour fonctionner nativement sur Windows, macOS et Linux, avec des performances élevées, un design professionnel adapté à l'étude biblique, et une intégrité absolue des données.

## Décision

### Versions verrouillées

| Technologie | Version | Rôle |
|---|---|---|
| **Rust** | `1.77+` (stable) | Langage backend Tauri |
| **Tauri** | `2.x` (latest stable) | Framework applicatif cross-platform |
| **Svelte** | `5.x` (Runes) | Compilateur frontend réactif |
| **SvelteKit** | `2.x` | Routeur et framework SSG/SPA pour Svelte 5 |
| **SurrealDB** | `2.x` (embedded) | Base de données embarquée |
| **Node.js** | `20 LTS` | Environnement de build frontend |
| **@sveltejs/vite-plugin-svelte** | `^4.0` | Plugin Svelte pour Vite |

> **Règle** : Les versions sont épinglées dans `Cargo.toml` et `package.json`. Aucune mise à jour de version majeure sans un nouvel ADR.

---

### Justifications des choix technologiques

#### Tauri (au lieu d'Electron ou d'un installeur MSI custom)

| Critère | Tauri ✅ | Electron ❌ |
|---|---|---|
| Taille du binaire | ~5-10 Mo | ~150-200 Mo |
| Consommation mémoire | ~30 Mo RAM | ~300 Mo RAM |
| Langage backend | Rust (sécurité mémoire) | Node.js |
| Multi-plateforme | Windows, macOS, Linux | Idem |
| Installeur natif | .exe, .deb, .dmg | Idem mais plus lourd |

- **Décision** : Tauri garantit un logiciel biblique léger, rapide et sécurisé installable via un `.exe` sur Windows.

#### Svelte 5 avec Runes (au lieu de Vue, React ou Angular)

| Critère | Svelte 5 ✅ | React ❌ |
|---|---|---|
| Réactivité | Runes (`$state`, `$derived`) compilées | Virtual DOM runtime |
| Bundle produit | Très léger (compile vers JS vanilla) | Inclut le runtime React (~45 Ko) |
| Courbe d'apprentissage | Faible | Moyenne / Élevée (hooks, JSX) |
| TypeScript natif | Oui | Partiel (nécessite config) |
| Compatibilité Tauri | Officielle et documentée | Non officielle |

- **Décision** : Svelte 5 avec les **Runes** (`$state`, `$derived`, `$effect`, `$props`) est le choix le plus performant et le plus lisible pour une interface de lecture intensive.
- **Runes Svelte 5 utilisées** :
  - `$state` : état réactif local (ex: verset affiché)
  - `$derived` : valeur calculée (ex: titre d'un chapitre)
  - `$effect` : effets de bord (ex: scroll automatique)
  - `$props` : props typées des composants
  - `$bindable` : liaison bidirectionnelle contrôlée

#### SurrealDB (au lieu de SQLite)

| Critère | SurrealDB ✅ | SQLite ❌ |
|---|---|---|
| Modèle de données | Multi-modèle (graphe, doc, relationnel) | Relationnel uniquement |
| Relations | Natif (traversée de graphe) | JOINs manuels |
| Recherche plein texte | Intégrée (SurrealQL `SEARCH`) | Extension FTS5 |
| Vecteur sémantique | Supporté (Phase 3) | Non disponible |
| Rust SDK natif | Officiel | Via `rusqlite` |
| Performance lectures | Très élevée | Elevée |

- **Décision** : Les textes bibliques ont des relations complexes (parallèles, références croisées, commentaires, variantes). SurrealDB modélise cela naturellement là où SQLite nécessiterait des dizaines de JOINs.

#### CSS Classique + Open Props (au lieu de Tailwind ou d'un framework CSS)

| Critère | CSS + Open Props ✅ | Tailwind ❌ |
|---|---|---|
| Contrôle typographique | Total (variable par variable) | Limité aux utilitaires |
| Lisibilité HTML | Propre (classes sémantiques) | Pollué (classes inline) |
| Custom Properties | Native | Via plugin |
| Design éditorial | Idéal | Difficile |

- **Open Props** (`open-props`) : bibliothèque de variables CSS prédéfinies (couleurs, espacement, typographie, ombres). Elle fournit un système de tokens cohérent sans imposer de style — parfait pour un design éditorial sur mesure.
- **Aucun framework de composants imposé** (pas de Shadcn, pas de DaisyUI) : les composants sont écrits from scratch pour contrôle total du rendu biblique.

---

## Conséquences

- Binaire final : ~10 Mo (Windows `.exe`), identique sur les 3 plateformes.
- Réactivité Svelte 5 Runes = meilleure performance d'affichage des listes de versets.
- SurrealDB permet la recherche croisée sans requêtes SQL complexes.
- Open Props garantit un design cohérent sans imposer un style générique.
- Toute déviation de cette stack nécessite un nouvel ADR.
