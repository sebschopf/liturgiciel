# ADR 005 : Protocole de Tests & Documentation Testée

## État

Accepté

## Question

> *Comment garantir que le code et les données sont valides à chaque étape du développement ?*

## Contexte

La fidélité biblique est l'exigence numéro 1. Une erreur de ponctuation est une régression majeure.

---

## Décision

### 1. Tests d'Intégrité des Données (Fidélité Critique)

Tout pipeline d'extraction ou de migration doit passer ces vérifications avant fusion :

| Type | Outil | Commande | Critère de succès |
|---|---|---|---|
| Fidélité bit-à-bit | `sha256sum` | `sha256sum fichier.lit > ref.sha256 && sha256sum -c ref.sha256` | `OK` |
| Encodage | `file` | `file --mime-encoding données.json` | `utf-8` |
| Ponctuation | Script dédié | `cargo run --bin verify_punctuation` | 0 différence |
| Échantillonnage | Manuel | Revue de 5 passages aléatoires | Validation humaine signée |

**Rapport obligatoire** pour toute PR de type `Kind/Data` :

```markdown
## Rapport de Haute Fidélité
- SHA-256 source : [hash]
- SHA-256 cible  : [hash]
- Correspondance : ✅ OUI / ❌ NON
- Encodage       : UTF-8 ✅
- Passages vérifiés : [liste des 5 passages]
- Validé par     : [nom/agent]
```

### 3. Tests du Code Backend (Rust)

- `cargo test` obligatoire avant toute PR.
- Couverture minimale : **80%** pour les fonctions dans `services/`.
- Chaque fonction publique dans `services/` a un test `#[cfg(test)]` dans le même fichier.
- Aucun `.unwrap()` non testé toléré.

### 4. Tests du Frontend (Svelte 5 + Vitest)

**Outil** : `vitest` + `@testing-library/svelte` (compatibilé Svelte 5).

#### Tests des Runes Svelte 5

Les Runes sont la fonctionnalité centrale de Svelte 5. Chaque Rune utilisée doit avoir un test dédié :

| Rune | Ce qu'on teste | Exemple de test |
|---|---|---|
| `$state` | La modification de l'état déclenche un re-render | Changer le verset affiché met à jour le DOM |
| `$derived` | La valeur dérivée se met à jour quand la source change | `chapitreTitre` change quand `chapitreId` change |
| `$effect` | L'effet s'exécute au bon moment | Le scroll se déclenche quand `versetCible` change |
| `$props` | Les props sont correctement typées et transmises | Verset reçoit `texte: string` et `reference: string` |
| `$bindable` | La liaison bidirectionnelle fonctionne | L'input de recherche synchro le store parent |

**Format obligatoire pour chaque composant :**

```typescript
// Verset.test.ts
import { render, screen } from '@testing-library/svelte';
import Verset from './Verset.svelte';

test('affiche le texte du verset', () => {
  render(Verset, { props: { texte: 'Test', reference: 'Jn 3:16' } });
  expect(screen.getByText('Jn 3:16')).toBeTruthy();
});
// ✅ Test associé : Verset.test.ts::affiche_le_texte — Résultat : PASS
```

- Aucun composant sans `Component.test.ts` associé.
- Aucune régression visuelle tolérée sur les composants typographiques.
- Commande : `npm run test`

### 5. Tests d'Intégration

- Scénario de bout en bout : Extraction → Stockage SurrealDB → Affichage dans l'UI.
- Tester sur les 3 plateformes cibles (Windows, macOS, Linux) avant toute release (ADR 006).

### 6. Tests de Linting (qualité du code)

Intégrés dans le pipeline CI (ADR 011) :

```bash
cargo fmt --check
cargo clippy -- -D warnings
npm run check
npm run lint
markdownlint Documentation/**/*.md
```

## Conséquences

- Zéro régression biblique.
- Documentation technique toujours synchro avec les tests.
