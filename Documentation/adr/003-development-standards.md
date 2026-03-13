# ADR 003 : Standards de Développement & Qualité du Code

## État
Proposé

## Contexte
Le projet LiturgiCielauri doit être maintenable sur le long terme par des humains ou des agents IA. Une cohérence absolue dans la structure du code et les conventions est nécessaire.

## Décision
Nous adoptons les standards suivants :

### 1. Langages & Frameworks
- **Backend** : Rust (Tauri). Utilisation de types stricts et gestion d'erreurs explicite (`Result`).
- **Frontend** : TypeScript (SvelteKit). Typage obligatoire pour tous les composants et stores.

### 2. Organisation & Traçabilité
- **Logique Métier** : Doit résider en priorité dans le backend Rust.
- **Traçabilité des Commits** : Aucun commit n'est accepté sans la mention explicite de l'ADR qui justifie le changement.
- **Communication** : Utilisation exclusive des `commands` Tauri pour l'échange Frontend <-> Backend.

### 3. Base de Données (SurrealDB)
- Les requêtes doivent être centralisées dans des services Rust.
- Utilisation du langage **SurrealQL** via le SDK Rust.
- Pas de requêtes brutes codées en dur dans le frontend.

### 4. Style CSS
- Utilisation de variables CSS (Custom Properties) pour le thème (HSL).
- Respect strict du design éditorial (voir ADR 005).

## Conséquences
- Code plus robuste et auto-documenté.
- Transition fluide entre le backend et le frontend grâce au typage.
- Facilité pour un futur contributeur de comprendre "où va quoi".
