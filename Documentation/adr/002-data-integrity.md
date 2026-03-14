# ADR 002 : Protocole d'Intégrité et de Vérification des Données

## État

Proposé

## Contexte

LiturgiCiel contient des études bibliques de haute précision où la ponctuation et les caractères spécifiques sont critiques pour le sens. Toute perte ou altération lors de l'extraction est inacceptable.

## Décision

Nous mettrons en œuvre un protocole de vérification à 3 niveaux pour toutes les tâches de migration de données :

1. **Vérification de la Source d'Extraction** :
   - Utiliser `fmptools` pour extraire les données binaires brutes sans transformations intermédiaires qui pourraient affecter l'encodage.
   - Forcer l'encodage **UTF-8** avec une gestion stricte des erreurs.

2. **Validation Automatisée de la Fidélité** :
   - Implémenter un script pour comparer le nombre de caractères (ponctuation incluse) entre les fichiers sources bruts et les enregistrements SurrealDB extraits.
   - Utiliser des sommes de contrôle (checksums/hashes) pour les blocs de texte volumineux.

3. **Revue de Pair Manuelle (Échantillonnage)** :
   - Pour chaque migration de table, un document de "Preuve de Fidélité" doit être créé.
   - Ce document montrera des comparaisons côte à côte des passages les plus complexes (avec ponctuation dense ou caractères Grecs/Hébreux) entre le logiciel de 2010 et LiturgiCielauri.

## Conséquences

- Chaque PR de données prendra plus de temps mais garantira une fidélité à 100%.
- Nous disposerons d'une piste d'audit permanente de la correction des données.
