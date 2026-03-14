# ADR 023 : Conventions de Nommage Frontend (Svelte 5 / TypeScript)

## État

Accepté

## Question

> *Comment nommer les fichiers, composants et variables dans le frontend ?*

## Décision

### 1. Composants Svelte

- **Format** : `PascalCase`
- **Suffixe** : `.svelte`
- **Exemple** : `LivreBiblique.svelte`, `BoutonAction.svelte`
- **Justification** : Distingue visuellement les composants des éléments HTML standards.

### 2. Dossiers

- **Format** : `kebab-case`
- **Exception** : Les dossiers spéciaux de SvelteKit comme `(app)` ou `[id]`.
- **Exemple** : `lib/components/`, `routes/api/v1/`

### 3. Fichiers TypeScript/JavaScript

- **Format** : `kebab-case`
- **Exemple** : `auth-service.ts`, `data-mapper.js`

### 4. Variables et Fonctions

- **Format** : `camelCase`
- **Langue** : Français (ADR 018)
- **Exemple** : `const listeFiches = []`, `function recupererVerset() {}`

### 5. Classes CSS

- **Format** : `kebab-case`
- **Méthode** : BEM simplifié ou composants encapsulés.
- **Exemple** : `.carte-fiche`, `.btn-primaire`

## Référence

- Organisation du Code → ADR 017
- Code as Documentation → ADR 020
- Langue de l'interface → ADR 018
