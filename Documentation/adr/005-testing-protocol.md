# ADR 005 : Protocole de Tests

## État
Proposé

## Contexte
LiturgiCielauri manipule des textes bibliques de haute précision. Une seule virgule manquante peut changer le sens théologique d'un passage. Un protocole de tests rigoureux est donc essentiel, à la fois pour le code et pour les données.

## Décision

### 1. Tests des Données (Priorité Absolue)
Tout pipeline d'extraction ou de migration doit passer ces tests avant fusion :

| Type | Outil | Critère de succès |
|---|---|---|
| Fidélité bit-à-bit | `diff` / checksum SHA-256 | 0 différence entre source et cible |
| Encodage | `file --mime-encoding` | UTF-8 strict sur tous les fichiers |
| Échantillonnage | Revue manuelle | 5 passages aléatoires validés visuellement |

### 2. Tests du Code (Backend Rust)
- Utilisation de `cargo test` pour tous les modules Rust.
- Couverture minimale : **80%** pour les fonctions d'accès aux données.
- Les tests doivent s'exécuter sans erreur avant toute PR.

### 3. Tests du Frontend (SvelteKit)
- Utilisation de **Vitest** pour les tests unitaires des composants.
- Tests de rendu des pages critiques (affichage de texte biblique).
- Aucune régression visuelle tolérée sur les composants typographiques.

### 4. Tests d'Intégration
- Vérifier que les données extraites s'affichent correctement dans l'UI.
- Tester sur les 3 plateformes cibles (Windows, macOS, Linux) avant une release.

## Conséquences
- Chaque PR de type `data/` doit inclure un rapport de checksum.
- Les tests `cargo test` et `vitest` seront intégrés aux Gitea Actions à la Phase 2.
