# ADR 014 : Accessibilité (WCAG AAA) & Navigation Clavier

## État
Accepté

## Contexte
LiturgiCielauri est un outil d'étude biblique à usage intensif et prolongé. Ses utilisateurs peuvent être malvoyants, utiliser un lecteur d'écran, ou préférer la navigation au clavier pour une étude rapide. L'accessibilité n'est pas une option : c'est une exigence fondamentale du projet, au même titre que l'intégrité des données.

## Décision

### 1. Niveau de conformité cible

**W3C WCAG 2.2 — Niveau AAA** (le niveau le plus élevé).

> Toute interface livrée doit satisfaire l'intégralité des critères de niveau A, AA **et** maximiser les critères de niveau AAA, notamment pour la lisibilité, le contraste et la navigation.

---

### 2. Navigation Clavier

#### Règles générales
- **Tout est accessible au clavier.** Aucune action ne doit nécessiter une souris.
- **Ordre de tabulation logique.** Le focus suit le sens de lecture naturel (haut → bas, gauche → droite).
- **Focus visible.** Un indicateur visuel clair (bordure colorée, ombre) est toujours visible sur l'élément focalisé.
- **Aucun piège clavier.** L'utilisateur peut toujours quitter un composant avec `Echap` ou `Tab`.

#### Raccourcis clavier globaux
Documentés dans une fenêtre d'aide accessible via `?` ou `F1` :

| Raccourci | Action |
|---|---|
| `F1` ou `?` | Afficher/masquer la liste des raccourcis |
| `Ctrl + F` | Recherche plein texte |
| `Ctrl + G` ou `Ctrl + J` | Aller à un verset (ex: "Jn 3:16") |
| `←` / `→` | Chapitre précédent / suivant |
| `↑` / `↓` | Verset précédent / suivant (dans un chapitre) |
| `Ctrl + ←` / `Ctrl + →` | Livre précédent / suivant |
| `Echap` | Fermer un panneau, revenir à la vue principale |
| `Tab` | Élément focalisable suivant |
| `Shift + Tab` | Élément focalisable précédent |
| `Entrée` | Activer l'élément focalisé |
| `Espace` | Activer un bouton ou cocher une case |

#### Sens de navigation (Ordre logique)
```
[Barre de navigation] → [Sélecteur Livre/Chapitre/Verset] → [Zone de texte biblique] → [Actions (Copier, Notes)]
```
- L'utilisateur ne doit jamais avoir à "retraverser" l'interface pour accomplir une action.

---

### 3. Standards ARIA & HTML Sémantique

| Composant | Balise HTML requise | Rôle ARIA |
|---|---|---|
| Zone de texte biblique | `<article>` | `role="document"` |
| Barre de navigation | `<nav>` | `aria-label="Navigation principale"` |
| Sélecteur de livre | `<select>` | `aria-label="Sélectionner un livre"` |
| Résultats de recherche | `<ul>` | `role="listbox"`, `aria-live="polite"` |
| Raccourcis clavier | `<kbd>` | N/A (balise sémantique) |
| Messages d'erreur | `<div>` | `role="alert"`, `aria-live="assertive"` |

- **`aria-live`** : Les résultats de recherche et les messages d'état sont annoncés automatiquement aux lecteurs d'écran.
- **`lang="fr"`** sur `<html>` pour la prononciation correcte (lecteurs d'écran).

---

### 4. Lisibilité & Perception (WCAG AAA)

| Critère | Valeur requise |
|---|---|
| Contraste texte / fond (normal) | Ratio ≥ **7:1** (AAA) |
| Contraste texte / fond (grand) | Ratio ≥ **4.5:1** (AA min) |
| Taille de police minimale | **18px** (texte biblique), **14px** (UI) |
| Espacement des lignes | `line-height` ≥ **1.8** pour le texte biblique |
| Largeur de colonne | Maximum **75 caractères** par ligne (lisibilité biblique) |
| Espacement des paragraphes | ≥ `1.5 × font-size` |
| Mode sombre | Disponible, respectant les mêmes ratios de contraste |

---

### 5. Tests d'Accessibilité

| Outil | Rôle | Commande |
|---|---|---|
| `axe-core` + `@axe-core/svelte` | Audit WCAG automatisé | Intégré dans les tests Vitest |
| `svelte-a11y` (eslint plugin) | Lint des attributs ARIA dans Svelte | Via `eslint` |
| Lecteur d'écran NVDA (Windows) | Test manuel avant release | Manuel |
| Test clavier seul | Navigation sans souris | Manuel avant chaque PR `Kind/Feature` |

**Format de test d'accessibilité obligatoire :**
```typescript
import { axe } from '@axe-core/svelte';

test('le composant Verset est accessible', async () => {
  const { container } = render(Verset, { props: { texte: '...', reference: 'Jn 3:16' } });
  const results = await axe(container);
  expect(results.violations).toHaveLength(0);
});
// ✅ Test d'accessibilité : Verset.a11y.test.ts — axe-core : 0 violation
```

---

## Conséquences
- Chaque composant Svelte 5 a un test `axe-core` associé (en plus de son test fonctionnel).
- La liste des raccourcis est maintenue dans un fichier `src/lib/shortcuts.ts` versionné.
- Toute PR de type `Kind/Feature` ou `Kind/Enhancement` inclut une vérification clavier manuelle.
- LiturgiCielauri pourra être utilisé par des personnes malvoyantes, âgées, ou pratiquant l'étude biblique intensive au clavier.
