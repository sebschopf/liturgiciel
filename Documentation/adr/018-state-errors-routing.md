# ADR 018 : Gestion de l'État, des Erreurs et du Routage Frontend

## État
Accepté

## Contexte
Trois questions liées au frontend n'avaient pas leur propre ADR : comment l'état applicatif est-il géré ? Comment les erreurs remontées du backend sont-elles présentées ? Quelles pages existent et pourquoi ? Ce document répond à ces trois questions.

---

## Décision

### 1. Gestion de l'état — Pourquoi Svelte Stores et pas Redux/Zustand ?

**Décision** : L'état global est géré exclusivement via les **primitives réactives de Svelte 5** (`$state`, Stores).

| Critère | Svelte Stores ✅ | Redux / Zustand ❌ |
|---|---|---|
| Dépendance externe | Aucune | Paquet npm supplémentaire (ADR 007) |
| Intégration Svelte 5 | Native (Runes) | Adaptateur requis |
| Courbe d'apprentissage | Minimale | Moyenne (actions, reducers...) |
| Bundle produit | Zéro ajout | +15–40 Ko |

**Deux niveaux d'état** :
- **`$state` (local)** : état contenu dans un composant (ex: input de recherche en cours de saisie).
- **Store Svelte (global)** : état partagé entre composants (ex: fiche actuellement affichée, résultats de recherche).

**Règle** : Un état ne monte au niveau Store que s'il est consommé par plus d'un composant.

---

### 2. Gestion des erreurs — Flux bout-en-bout

**Problème à résoudre** : Une erreur SurrealDB ne doit pas apparaître brute en UI. L'utilisateur doit voir un message en français, actionnable.

**Flux décidé** :
```
DB (SurrealDB)         → Erreur technique brute
      ↓ services/
Backend Rust           → AppError typé (NotFound, Database, Encoding...)
      ↓ commands/ → Result<T, AppError> sérialisé en JSON
Frontend (api/)        → Catch de l'erreur, mapping vers message FR
      ↓ Store erreur
UI (composant)         → Affichage du message localisé
```

**Pourquoi `AppError` centralisé ?**
- Un type unique force à traiter tous les cas d'erreur explicitement.
- Interdit les erreurs silencieuses (`unwrap()` banni en production, ADR 003).
- Le frontend reçoit toujours le même format JSON : `{ "type": "NotFound", "message": "Fiche introuvable" }`.

---

### 3. Routage — Pages de l'application et leur justification

| Route | Page | Justification |
|---|---|---|
| `/` | Accueil / Recherche | Point d'entrée unique — la recherche est l'action principale |
| `/fiche/[id]` | Détail d'une fiche | Fiche addressable par URL pour navigation clavier (ADR 014) |
| `/dossier/[id]` | Contenu d'un dossier | Permet de partager un lien vers un dossier |
| `/culte/[id]` | Structure d'un culte | Vue du gabarit de célébration |
| `/celebration/[id]` | Célébration datée | Visualisation d'un culte celebré |
| `/recherche?q=` | Résultats de recherche | URL partageable avec la recherche pré-remplie |
| `/parametres` | Configuration | Langue, thème, préférences utilisateur |

**Règle de routage** : Toute entité principale (Fiche, Dossier, Culte) est addressable par son propre URL. Cela garantit la navigation clavier (ADR 014) et les liens directs.

## Conséquences
- Aucune bibliothèque de state management externe ne sera installée sans nouveau ADR.
- Tout message d'erreur affiché en UI doit être en français et venir du mapping `AppError`.
- Les nouvelles pages doivent être ajoutées à ce tableau avant d'être implémentées.
