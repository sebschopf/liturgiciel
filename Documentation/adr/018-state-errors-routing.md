# ADR 018 : Gestion de l'État, des Erreurs et du Routage Frontend

## État

Accepté

## Question

> *Quels sont les standards pour la réactivité et la navigation dans le frontend ?*

## Contexte

Svelte 5 introduit les `Runes` pour la réactivité. Nous devons définir comment les utiliser de manière cohérente.

## Décision

### 1. Gestion de l'État (Runes)

- **`$state` (local)** : Pour l'état interne d'un composant simple.
- **`$state` (global)** : Pour l'état partagé (ex: session utilisateur), exporté via un module `.ts`.
- **`$derived`** : Utilisation systématique pour tout état calculé à partir d'un autre.

### 2. Gestion des Erreurs

Toute erreur provenant du backend doit être typée et affichée via un composant `Toast`.

```typescript
type AppError = {
  code: string;
  message: string;
};
```

### 3. Routage

Utilisation du routeur standard de SvelteKit.

## Référence

- Architecture en Couches → ADR 013
- Code as Documentation → ADR 020

## Conséquences

- Aucune bibliothèque de state management externe (Redux, Pinia) n'est autorisée.
- Un type unique force à traiter tous les cas d'erreur.
