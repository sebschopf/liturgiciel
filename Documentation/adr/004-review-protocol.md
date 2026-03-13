# ADR 004 : Protocole de Révision des Pull Requests

## État
Accepté

## Contexte
Le projet LiturgiCielauri est développé par un binôme humain + IA. L'expérience de la PR #1 a révélé un softlock : Gitea interdit à un auteur d'approuver sa propre PR, mais aucun protocole ne précisait les rôles d'évaluation.

## Décision

### Rôles
- **L'IA (agent)** : auteur et assigné des changements techniques.
- **L'humain (mous_tik)** : évaluateur et décideur final. C'est lui qui fusionne.

### Règle d'approbation selon la phase
| Phase | Approbations minimales | Justification |
|---|---|---|
| Phase 1 – Solo (IA + 1 humain) | **0** | L'humain valide *en fusionnant* |
| Phase 2 – Équipe (≥ 2 humains) | **1** | Un pair humain doit approuver |

### Processus de révision
1. L'IA ouvre une PR sur une branche dédiée (ex: `docs/`, `feature/`, `data/`).
2. L'IA remplit le modèle de PR (checklist ADR, intégrité des données).
3. L'humain examine les **"Fichiers modifiés"**.
4. L'humain fusionne s'il approuve, ou demande des changements via un commentaire.

### Critères de refus d'une PR
- Aucune référence à un ADR dans le message de commit.
- Rapport de haute fidélité manquant pour les PRs de type `data/`.
- Conflit non résolu avec un ADR existant.

## Conséquences
- Pendant la Phase 1, régler le minimum d'approbations à `0` dans Paramètres > Branches.
- Ce protocole évite tout futur softlock.
