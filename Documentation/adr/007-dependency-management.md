# ADR 007 : Gestion des Dépendances

## État

Accepté

## Contexte

Chaque nouvelle dépendance (bibliothèque Rust, paquet npm) est un risque potentiel : sécurité, compatibilité, pérennité. Pour un logiciel destiné à durer, chaque ajout doit être délibéré.

## Décision

### Critères d'acceptation d'une dépendance

Une dépendance est acceptée si elle remplit **tous** ces critères :

1. **Active** : Dernier commit de moins de 12 mois ou maintenu par une organisation connue.
2. **Licenciée** : Licence MIT, Apache 2.0, ou MPL-2.0 uniquement.
3. **Nécessaire** : Impossible à implémenter raisonnablement en interne.
4. **Justifiée** : Un ADR ou un commentaire de PR documente pourquoi elle est ajoutée.

### Processus d'ajout

1. Ouvrir une **Issue Gitea** avec le tag `Kind/Dependency` avant d'ajouter la dépendance.
2. Préciser : nom, version, licence, raison.
3. L'ajout se fait via une PR dédiée référençant l'Issue.

### Outils de gestion

- **Rust** : `cargo update` pour les mises à jour. `cargo audit` pour les vulnérabilités.
- **npm/SvelteKit** : `npm audit` avant chaque release.

### Dépendances de base approuvées

| Paquet | Environnement | Rôle |
|---|---|---|
| `tauri` | Rust | Moteur applicatif |
| `surrealdb` | Rust | Base de données embarquée |
| `sveltekit` | npm | Framework frontend |

## Conséquences

- Dépendances minimales, auditables et documentées.
- Réduction du risque de supply chain attack.
