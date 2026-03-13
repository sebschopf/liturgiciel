# Protocole de Développement

Pour garantir une précision et une traçabilité absolues pour le projet LiturgiCielauri, le protocole suivant doit être strictement respecté :

## 1. Comptes-rendus de Décisions Architecturales (ADR)
- Chaque choix technique ou architectural majeur DOIT être documenté dans un ADR.
- Les ADR sont stockés dans `Documentation/adr/`.
- Format : [000-titre.md]
- Tout changement de la stack ou de la logique centrale nécessite un nouvel ADR ou une mise à jour d'un existant.

## 2. Pull Requests (PR) et Commits
- Toutes les modifications doivent être effectuées via des PR (ou traitées comme des unités logiques atomiques dans ce dépôt).
- Les commits doivent suivre la convention [Conventional Commits](https://www.conventionalcommits.org/fr/) :
    - `feat:` pour les nouvelles fonctionnalités
    - `fix:` pour les corrections de bugs
    - `docs:` pour les mises à jour de documentation
    - `chore:` pour la maintenance
- Chaque PR doit inclure un résumé des changements et une étape de vérification.

## 3. Vérification de l'Intégrité des Données
- Toute PR affectant l'extraction des données ou la couche de stockage doit inclure un "Rapport de Haute Fidélité".
- Ce rapport doit prouver qu'aucune ponctuation ou caractère n'a été altéré pendant le processus.

## 4. Documentation d'abord
- La documentation doit être mise à jour *avant* ou *en même temps* que l'implémentation du code.
