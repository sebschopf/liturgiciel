# ADR 014 : Accessibilité (WCAG AAA) & Navigation Clavier

## État

Accepté

## Contexte

LiturgiCielauri est un outil d'étude biblique à usage intensif. L'accessibilité est une exigence fondamentale.

## Décision

### 1. Niveau de conformité cible

**W3C WCAG 2.2 — Niveau AAA**.

### 2. Navigation Clavier

- **Tout est accessible au clavier.**
- **Ordre de tabulation logique.**
- **Focus visible.**

#### Sens de navigation (Ordre logique)

```text
[Barre de navigation] -> [Sélecteur] -> [Zone de texte] -> [Actions]
```

### 3. Standards ARIA & HTML Sémantique

- Utilisation de `<article>`, `<nav>`, `<kbd>`, etc.
- **`aria-live="polite"`** pour les résultats de recherche.

### 4. Lisibilité (WCAG AAA)

- Contraste ≥ **7:1**.
- Taille de police min **18px** pour le texte biblique.
- Largeur max **75 caractères** par ligne.

### 5. Tests d'Accessibilité

Utilisation de `axe-core` intégré dans les tests Vitest.

```typescript
import { axe } from '@axe-core/svelte';

test('le composant Verset est accessible', async () => {
  const { container } = render(Verset, { props: { texte: '...', reference: 'Jn 3:16' } });
  const results = await axe(container);
  expect(results.violations).toHaveLength(0);
});
```

## Conséquences

- Chaque composant Svelte 5 a un test `axe-core` associé.
- Navigation ultra-performante pour les utilisateurs avancés au clavier.
