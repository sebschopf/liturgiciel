# ADR 009 : Gestion des Secrets & Sécurité

## État
Accepté

## Contexte
Le projet utilise des tokens Gitea, de potentielles clés de signature de code (pour Windows), et des variables de configuration sensibles. Aucun de ces éléments ne doit se retrouver dans l'historique Git.

## Décision

### Règle d'Or
> **Aucune clé, token, mot de passe ou donnée sensible ne doit jamais être commité dans Git.**

Une violation de cette règle est un motif de refus immédiat de PR, même si le secret a été retiré dans un commit ultérieur (il reste dans l'historique).

### Stockage des Secrets
| Type de secret | Où le stocker |
|---|---|
| Variables de build | Variables Gitea (`Paramètres > Actions > Variables`) |
| Clés de signature Windows | Secrets Gitea (`Paramètres > Actions > Secrets`) |
| Config locale de développement | Fichier `.env.local` (listé dans `.gitignore`) |
| Mots de passe DB locaux | Jamais en DB embarquée (SurrealDB n'en a pas besoin) |

### Fichiers à exclure (`.gitignore`)
```
.env
.env.local
*.key
*.pem
*.p12
*.pfx
/target
/node_modules
```

### Processus en cas de fuite
1. Révoquer immédiatement le secret exposé (token Gitea, clé de signature).
2. Le signaler via une Issue Gitea taguée `Kind/Security`.
3. Réécrire l'historique Git si nécessaire (`git filter-branch` ou `git filter-repo`).

## Conséquences
- Dépôt safe à rendre public à l'avenir.
- Aucun risque de compromission des clés de signature de l'application.
