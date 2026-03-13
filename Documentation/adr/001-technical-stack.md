# ADR 001 : Sélection de la Pile Technique (Stack)

## État
Accepté

## Contexte
LiturgiCiel 2010 est une application FileMaker Pro 10 obsolète. Elle doit être modernisée pour fonctionner nativement sur Linux, Windows et macOS avec des performances élevées, une interface professionnelle et une intégrité absolue des données.

## Décision
Nous utiliserons la pile technique suivante :
- **Framework Principal** : Tauri (backend en Rust)
- **Base de Données** : SurrealDB (Embarquée)
- **Frontend** : SvelteKit
- **Style** : CSS Classique (Design Éditorial Professionnel)

## Conséquences
- Distribution sous forme de binaire unique avec installeur intégré (.exe pour Windows).
- Performances élevées et faible consommation de ressources.
- Support de données multi-modèle (Relationnel, Graphe, Document).
- Capacités de recherche sémantique (Vector search).
- Interface identique sur toutes les plateformes.
