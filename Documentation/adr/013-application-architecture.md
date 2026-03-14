# ADR 013 : Architecture en Couches (Séparation des Responsabilités)

## État
Accepté

## Contexte
LiturgiCielauri est une application desktop native (Tauri) avec un frontend web. La question centrale est : **qui fait quoi, et comment les couches communiquent-elles ?** Sans règle explicite, la logique métier finit dans l'UI, la DB est appelée depuis n'importe où, et le code devient impossible à tester.

## Décision

### Les trois couches et leurs responsabilités exclusives

```
FRONTEND (Svelte 5)          — Afficher, réagir aux actions utilisateur
        ↕ Tauri IPC (invoke)
BACKEND (Rust / Tauri)       — Traiter, valider, orchestrer
        ↕ SurrealDB SDK Rust
BASE DE DONNÉES (SurrealDB)  — Persister, rechercher, relier
```

**Chaque couche a une responsabilité exclusive :**

| Couche | Fait | Ne fait JAMAIS |
|---|---|---|
| **Frontend** | Affichage, navigation, interaction | Requêtes DB directes, logique métier |
| **Backend** | Validation, traitement, orchestration | Logique d'affichage, HTML/CSS |
| **Base de données** | Persistance, recherche plein texte | Calcul applicatif, règles métier |

### Règles d'interaction — inviolables

1. **Frontend → Backend uniquement via `invoke()`** (Tauri IPC). Aucun import Rust direct depuis Svelte.
2. **Backend → DB uniquement via la couche `db/`**. Aucune requête SurrealQL dans `commands/` ou `services/`.
3. **Les Stores Svelte ne connaissent pas SurrealDB**. Ils n'appellent que des fonctions de `src/lib/api/`.
4. **Zéro effet de bord caché**. Toute mutation d'état transite par un Store Svelte explicite.

### Pourquoi Tauri IPC et non une API REST locale ?

| Critère | Tauri IPC ✅ | API REST locale ❌ |
|---|---|---|
| Port réseau ouvert | Non | Oui (risque sécurité) |
| Typage bout-en-bout | Sérialisation JSON automatique | Manuel |
| Performance | Mémoire partagée (IPC) | Socket TCP |
| Packaging | Bundlé dans l'application | Process séparé |

## Alternatives considérées
- **Monolithique (tout dans Rust, rendu HTML server-side)** : Rejeté. Pas d'interface réactive.
- **Frontend pur avec SurrealDB en WASM** : Rejeté. SurrealDB embarquée n'est pas disponible en WASM stable à ce jour.

## Conséquences
- Toute violation de la règle de couche est détectable à la revue de code.
- Chaque couche peut être testée indépendamment (ADR 005).
- L'organisation physique des fichiers découle directement de ce modèle (voir ADR 017).
