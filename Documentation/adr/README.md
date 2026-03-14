# Index des Décisions Architecturales (ADR)

Ce document regroupe toutes les décisions structurantes du projet LiturgiCielauri, classées par thématique. Chaque contributeur (humain ou bot) doit se référer à ces documents avant toute modification.

> **Règle** : Si une situation n'est pas couverte par un ADR, une nouvelle proposition doit être soumise via une Pull Request avant toute implémentation.

## Fondations & Stack

- [ADR 001 : Sélection de la Pile Technique (Tauri, SurrealDB, Svelte 5, Open Props)](001-technical-stack.md)
- [ADR 003 : Standards de Développement, Qualité du Code & Linters](003-development-standards.md)
- [ADR 013 : Architecture en Couches — qui fait quoi, règles d'interaction](013-application-architecture.md)
- [ADR 017 : Organisation du Code et Structure des Dossiers](017-code-organization.md)
- [ADR 018 : Gestion de l'État, des Erreurs et du Routage Frontend](018-state-errors-routing.md)
- [ADR 019 : Modularité & Principe de Responsabilité Unique (SRP, DRY)](019-modularity-srp.md)
- [ADR 020 : Code as Documentation — Quand et comment commenter](020-code-as-documentation.md)
- [ADR 021 : Injection de Dépendances & Testabilité](021-dependency-injection.md)
- [ADR 022 : Performance Délibérée du Code](022-performance.md)

## Conventions de Nommage

- [ADR 023 : Conventions de Nommage Frontend (Svelte 5 / TypeScript)](023-naming-frontend.md)
- [ADR 024 : Conventions de Nommage Backend (Rust / Tauri)](024-naming-backend.md)
- [ADR 025 : Conventions de Nommage SurrealDB (Tables, Champs, Relations)](025-naming-surrealdb.md)

## Langue

- [ADR 026 : Stratégie de Langue (UI français, contenu multilingue fr/de/it)](026-language-strategy.md)

## Données & Intégrité

- [ADR 002 : Protocole d'Intégrité et de Vérification des Données](002-data-integrity.md)

## Gouvernance & Qualité

- [ADR 004 : Protocole de Révision des Pull Requests](004-review-protocol.md)
- [ADR 005 : Protocole de Tests & Documentation Testée](005-testing-protocol.md)
- [ADR 006 : Versionnage (Semantic Versioning)](006-versioning.md)
- [ADR 007 : Gestion des Dépendances](007-dependency-management.md)
- [ADR 008 : Changelog & Notes de Version](008-changelog.md)
- [ADR 009 : Gestion des Secrets & Sécurité](009-security-secrets.md)
- [ADR 010 : Étiquettes Gitea & Tags Git Protégés](010-labels-and-tags.md)
- [ADR 011 : Automatisation CI/CD avec Gitea Actions](011-ci-cd-automation.md)
- [ADR 012 : Cycle de Vie des Issues Gitea](012-issue-lifecycle.md)

## Interface & UX

- [ADR 014 : Accessibilité (WCAG AAA) & Navigation Clavier](014-accessibility.md)
*(Design éditorial à définir lors de la Phase 2 avec les 3 graphistes)*

## Données & Schéma SurrealDB

- [ADR 015 : Entités du Domaine Métier (Fiche, Culte, Dossier, Célébration...)](015-surrealdb-schema.md)
- [ADR 016 : Stratégie de Relations (Champ direct vs Graphe SurrealDB)](016-data-relations.md)
