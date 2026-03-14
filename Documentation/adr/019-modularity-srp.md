# ADR 019 : Modularité & Principe de Responsabilité Unique (SRP, DRY)

## État

Accepté

## Question

> *Comment organiser le code interne pour éviter la dette technique ?*

## Contexte

LiturgiCielauri est un projet à long terme. Un code monolithique ou trop couplé rendra les futures évolutions
(nouvelles langues, nouveaux exports) impossibles.

## Décision

### 1. Single Responsibility Principle (SRP)

Chaque fichier ou module doit avoir une seule raison de changer.

- Un module pour l'extraction SQLite.
- Un module pour la transformation en JSON.
- Un module pour l'injection SurrealDB.

### 2. Don't Repeat Yourself (DRY)

Toute logique répétée (ex: formatage de date biblique) doit être extraite dans un utilitaire partagé.

### 3. Modularité par domaine

Le code est découpé par entité métier (Fiche, Verset, Auteur) plutôt que par type technique.

## Référence

- Architecture en Couches → ADR 013
- Organisation du Code → ADR 017

## Conséquences

- Un traitement métier n'est jamais dupliqué entre le frontend et le backend.
- Les tests unitaires sont plus faciles à écrire car les responsabilités sont isolées.
- Une PR contenant une fonctionnalité "touche-à-tout" sera systématiquement refusée.
