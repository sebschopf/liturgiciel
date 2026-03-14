# ADR 010 : Étiquettes Gitea & Tags Git Protégés

## État
Accepté

## Contexte
Gitea fournit un jeu d'étiquettes prédéfini lors de l'initialisation d'un dépôt. Ce référentiel d'étiquettes doit être enrichi avec les étiquettes spécifiques au projet, et les tags Git doivent être protégés pour éviter toute création accidentelle de versions.

## Décision

### 1. Étiquettes Gitea existantes (générées par défaut)

Ces étiquettes sont déjà présentes dans Gitea et font partie de notre protocole :

#### `Compat/`
| Étiquette | Usage |
|---|---|
| `Compat/Breaking` | Changement incompatible — déclenche une version MAJEUR (ADR 006) |

#### `Kind/`
| Étiquette | Usage |
|---|---|
| `Kind/Bug` | Quelque chose ne fonctionne pas |
| `Kind/Documentation` | Mise à jour de documentation ou ADR |
| `Kind/Enhancement` | Amélioration d'une fonctionnalité existante |
| `Kind/Feature` | Nouvelle fonctionnalité |
| `Kind/Security` | Problème ou correctif de sécurité (ADR 009) |
| `Kind/Testing` | PR ou issue liée aux tests (ADR 005) |

#### `Priority/`
| Étiquette | Valeur | Usage |
|---|---|---|
| `Priority/Critical` | 1 | Bloquant — ponctuation ou sens biblique erroné |
| `Priority/High` | 2 | À traiter en priorité |
| `Priority/Medium` | 3 | Standard |
| `Priority/Low` | 4 | Peut attendre |

#### `Reviewed/`
| Étiquette | Usage |
|---|---|
| `Reviewed/Confirmed` | Issue confirmée et reproductible |
| `Reviewed/Duplicate` | Issue ou PR déjà existante |
| `Reviewed/Invalid` | Issue invalide |
| `Reviewed/Won't Fix` | Problème connu, pas de correction prévue |

#### `Status/`
| Étiquette | Usage |
|---|---|
| `Status/Abandoned` | Travail commencé mais abandonné |
| `Status/Blocked` | Bloqué par une dépendance externe |
| `Status/Need More Info` | Informations supplémentaires requises |

---

### 2. Étiquettes à créer manuellement

Ces étiquettes sont **spécifiques au projet** et doivent être créées dans **Gitea > Étiquettes**.

| Étiquette | Couleur (hex) | Description |
|---|---|---|
| `Kind/Dependency` | `#e4e669` | Ajout ou mise à jour d'une dépendance (ADR 007) |
| `Kind/Data` | `#f9d0c4` | Extraction ou migration de données bibliques (ADR 002) |
| `Kind/Release` | `#0e8a16` | PR de préparation d'une release (ADR 006) |
| `Status/data-fidelity-checked` | `#1d76db` | Rapport d'intégrité des données validé (ADR 002) |

---

### 3. Tags Git Protégés (Versions)

Les tags de version **ne doivent être créés que lors d'une release officielle** (ADR 006).

- Aller dans **Paramètres > Tags** (`/settings/tags`)
- Ajouter la règle de motif : `v*`
- Restreindre la création/suppression à **`mous_tik`** uniquement

## Conséquences
- Vocabulaire commun et cohérent pour toutes les Issues et PRs.
- Les 4 étiquettes spécifiques au projet doivent être créées manuellement.
- Les tags de version sont protégés et traçables (ADR 006).
