# ADR 008 : Changelog & Notes de Version

## État
Accepté

## Contexte
Les utilisateurs de LiturgiCielauri doivent savoir ce qui a changé entre deux versions, notamment si des données bibliques ont été corrigées ou si de nouvelles fonctionnalités sont disponibles.

## Décision
Adoption du format **[Keep a Changelog](https://keepachangelog.com/fr/1.1.0/)** dans un fichier `CHANGELOG.md` à la racine du projet.

### Format des entrées
```markdown
## [version] - AAAA-MM-JJ
### Ajouts
- Description de la nouveauté (ADR-XXX)
### Corrections
- Correction de bug ou de donnée (ADR-002)
### Modifications
- Changement de comportement existant
### Suppressions
- Fonctionnalité retirée
```

### Règles de mise à jour
- Le `CHANGELOG.md` est mis à jour dans la **même PR** que la fonctionnalité ou le fix.
- Les corrections de données bibliques (ponctuation, accent) sont signalées avec le tag `[DONNÉES]` pour les identifier facilement.
- Le fichier est maintenu en **français**.

### Lien avec Gitea
- Chaque release Gitea (`Gitea > Releases`) reprend le contenu correspondant du `CHANGELOG.md`.
- Le tag Git correspond à la version : `v1.0.0`, `v1.1.0`, etc. (voir ADR 006).

## Conséquences
- Traçabilité totale pour l'utilisateur final.
- Historique auditable des corrections de données bibliques.
