# ADR 023 : Conventions de Nommage Frontend (Svelte 5 / TypeScript)

## État
Accepté

## Question
> *Quelles sont les conventions de nommage dans le code frontend ?*

## Décision

| Élément | Convention | Exemple |
|---|---|---|
| Composant Svelte | `PascalCase` | `Fiche.svelte`, `ListeDossiers.svelte` |
| Test de composant | Même nom + `.test.ts` | `Fiche.test.ts` |
| Test d'accessibilité | Même nom + `.a11y.test.ts` | `Fiche.a11y.test.ts` |
| Store Svelte | `camelCase`, nom du domaine | `fiches.ts`, `navigation.ts` |
| Fichier de route | Convention SvelteKit | `+page.svelte`, `+layout.svelte` |
| Fonction TypeScript | `camelCase`, verbe + nom | `getFiche`, `creerDossier` |
| Variable | `camelCase`, intention explicite | `ficheSelectionnee`, `resultatsRecherche` |
| Type / Interface | `PascalCase` | `Fiche`, `TempsLiturgique` |
| Constante globale | `SCREAMING_SNAKE_CASE` | `STATUT_OFFICIELLE` |
| Prop de composant | `camelCase` | `tempsLiturgique`, `estEditable` |
| Booléen | Préfixe `est`, `peut`, `a` | `estOfficielle`, `peutModifier` |

### Langue
- Tous les identifiants sont en **français** (noms de domaine, variables métier).
- L'anglais est réservé aux termes techniques sans équivalent (`store`, `layout`, `props`).

### Interdictions
- Abréviations : `f`, `d`, `usr`, `res` → interdit.
- Noms génériques : `data`, `result`, `items`, `obj` → interdit.

## Référence
- Convention de fichiers → ADR 017
- Convention de commentaires → ADR 020
