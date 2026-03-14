# ADR 013 : Architecture en Couches (Séparation des Responsabilités)

## État

Accepté

## Contexte

LiturgiCielauri est une application desktop native (Tauri) avec un frontend web. La question centrale est :
**qui fait quoi, et comment les couches communiquent-elles ?**

## Décision

### Les trois couches et leurs responsabilités exclusives

```text
FRONTEND (Svelte 5)          — Afficher, réagir aux actions utilisateur
        ↕ Tauri IPC (invoke)
BACKEND (Rust / Tauri)       — Traiter, valider, orchestrer
        ↕ SurrealDB SDK Rust
BASE DE DONNÉES (SurrealDB)  — Persister, rechercher, relier
```

**Chaque couche a une responsabilité exclusive :**

| Couche | Fait | Ne fait JAMAIS |
|---|---|---|
| **Frontend** | Affichage, interaction | Requêtes DB directes |
| **Backend** | Validation, orchestration | Logique d'affichage |
| **Base de données** | Persistance, recherche | Calcul applicatif |

## Conséquences

- Le frontend ne contient aucun code SurrealDB.
- Tous les accès aux données se font via des `commands` Rust typées.
- Facile à migrer si on change d'UI ou de base de données à l'avenir.
