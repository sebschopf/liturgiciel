# ADR 021 : Injection de Dépendances & Testabilité

## État

Accepté

## Question

> *Comment structurer le code pour faciliter les tests unitaires et le mocking ?*

## Contexte

Le projet nécessite une haute fiabilité, particulièrement pour la logique d'extraction et de migration. Un code
fortement couplé aux entrées/sorties (système de fichiers, base de données) est difficile à tester.

## Décision

### 1. Utilisation de Traits pour les services

Chaque service backend doit définir son comportement via un `trait` avant son implémentation.

### 2. Injection par constructeur

Les services reçoivent leurs dépendances (traits) via leur constructeur (ex: `new(db: Box<dyn DatabaseTrait>)`).

### 3. Mocking en Rust

Utilisation de la crate `mockall` pour générer des mocks automatiques pendant les tests.

### 4. Structure Frontend

Utilisation des `stores` Svelte et des `contextes` pour injecter les services API, permettant de substituer le
backend par des mocks en environnement de test Vitest.

## Référence

- Protocole de Tests → ADR 005
- Architecture en Couches → ADR 013

## Conséquences

- Toute fonction de `services/` doit être testable sans nécessiter une instance réelle de SurrealDB.
- Les tests unitaires sont rapides car ils n'utilisent aucune ressource externe.
