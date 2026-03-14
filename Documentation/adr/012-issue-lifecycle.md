# ADR 012 : Cycle de Vie des Issues Gitea

## État
Accepté

## Contexte
Une Issue mal gérée mène à du travail perdu ou à des décisions sans traçabilité. Pour un projet de haute précision comme LiturgiCielauri, chaque modification — même mineure — doit être initiée par une Issue avant toute action.

## Décision

### Règle fondamentale
> **Aucune PR ne peut exister sans une Issue qui la justifie.**  
> Exception unique : les PRs de type `Kind/Documentation` portant uniquement sur les ADR.

### Cycle de vie d'une Issue

```
[Ouverture] → [Triage] → [En cours] → [En révision] → [Fermée]
```

| Étape | Qui | Action Gitea |
|---|---|---|
| **Ouverture** | Humain ou IA | Créer l'Issue avec le modèle, assigner une étiquette et un jalon |
| **Triage** | Humain | Valider la priorité, assigner un responsable |
| **En cours** | IA (agent) | Créer une branche liée, référencer l'Issue dans les commits (`Closes #N`) |
| **En révision** | Humain | Ajouter `Status/Needs More Info` si besoin |
| **Fermée** | Automatique | Fermée automatiquement quand la PR liée est fusionnée |

### Lien Issue → PR → Commit
- La branche porte le numéro de l'Issue : `feature/42-recherche-par-verset`.
- Le commit de clôture mentionne : `feat: ajouter la recherche par verset (Closes #42, ADR-001)`.
- Cela crée une traçabilité totale : **Issue → Branche → Commit → PR → Fusion**.

### Étiquettes au moment de l'ouverture
Toute nouvelle Issue doit avoir au minimum :
- **1 étiquette `Kind/`** (ex: `Kind/Feature`)
- **1 étiquette `Priority/`** (ex: `Priority/High`)
- **1 jalon** (ex: `Phase 1 – Extraction`)

## Conséquences
- Traçabilité totale de chaque décision jusqu'au code.
- Un agent IA peut reconstruire l'intention originelle d'une fonctionnalité à partir de l'Issue.
