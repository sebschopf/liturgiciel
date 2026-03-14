# ADR 017 : Organisation du Code et Structure des Dossiers

## État

Accepté

## Question

> *Comment organiser les fichiers sources pour un projet hybride Rust/SvelteKit ?*

## Contexte

LiturgiCielauri est un projet Tauri 2.0. Il nécessite une séparation claire entre le frontend (SvelteKit) et le
backend (Rust), tout en facilitant la communication entre les deux.

## Décision

### 1. Racine du projet

- `.gitea/` : Workflows et modèles Gitea.
- `Documentation/` : ADR, protocole, manuels.
- `src/` : Code source frontend (SvelteKit).
- `src-tauri/` : Code source backend (Rust).

### 2. Structure Frontend (`src/`)

- `lib/` : Composants, services et utilitaires partagés.
- `routes/` : Pages et API routes de SvelteKit.
- `static/` : Assets statiques (images, polices).

### 3. Structure Backend (`src-tauri/src/`)

- `commands/` : Points d'entrée appelables par le frontend.
- `services/` : Logique métier, accès base de données.
- `models/` : Structures de données Rust.
- `main.rs` : Initialisation de l'application.

## Référence

- Conventions de nommage des fichiers → ADR 023
- Architecture en Couches → ADR 013
