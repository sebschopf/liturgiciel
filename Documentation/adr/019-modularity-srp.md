# ADR 019 : Modularité & Principe de Responsabilité Unique

## État
Accepté

## Question
> *Combien de responsabilités a ce module, cette fonction, ce composant ?*

## Contexte
Sans règle explicite, les fonctions grossissent, les modules se mélangent, et le code devient impossible à tester ou à modifier sans tout casser.

## Décision

**Un module, une responsabilité. Une fonction, une action.**

### Rust (Backend)
- `services/fiches.rs` gère uniquement les Fiches. Il ne contient pas de logique de Dossiers ou de Cultes.
- Une fonction fait **une seule chose** : `get_fiche()` récupère — elle ne valide pas, ne transforme pas, ne log pas.
- Règle de taille : une fonction > **30 lignes** est un signal de refactorisation. La scinder.
- La logique partagée entre plusieurs services est extraite dans un module `utils/` ou `services/common.rs`.

### Svelte 5 (Frontend)
- Un composant = une responsabilité d'affichage. `Fiche.svelte` affiche une fiche. Il ne sait pas chercher ni classer.
- Les Stores sont organisés par domaine (`fiches.ts`, `dossiers.ts`). Pas de store global fourre-tout.
- Un Store qui fait plus de 50 lignes est un signal de découpage.

### Ouvert/Fermé (O de SOLID)
> Le code existant ne se modifie pas — il s'étend.

- Ajouter `Célébrations` ne modifie pas `services/fiches.rs`. On crée `services/celebrations.rs`.
- Les commandes Tauri exposent des points d'entrée stables. On ajoute des fonctions, on ne réécrit pas les existantes.

### DRY (Don't Repeat Yourself)
- Un traitement métier n'existe qu'en un seul endroit : dans `services/`.
- Si deux commandes partagent une logique, elle est extraite dans un service commun.
- Les constantes (statuts, types de moment liturgique) sont centralisées dans `models/`.

## Conséquences
- Une PR contenant une fonction > 30 lignes non justifiée peut être refusée.
- Toute logique dupliquée dans deux modules est un bug de conception, pas de code.
