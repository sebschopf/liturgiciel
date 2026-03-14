# ADR 024 : Conventions de Nommage Backend (Rust / Tauri)

## État
Accepté

## Question
> *Quelles sont les conventions de nommage dans le code backend Rust ?*

## Décision

| Élément | Convention | Exemple |
|---|---|---|
| Module / Fichier | `snake_case` | `fiches.rs`, `temps_liturgique.rs` |
| Fonction publique | `snake_case`, verbe + nom | `get_fiche`, `rechercher_par_temps` |
| Commande Tauri | `snake_case`, préfixe d'action | `get_fiche`, `creer_dossier`, `supprimer_dossier` |
| Struct | `PascalCase` | `Fiche`, `TempsLiturgique`, `AppError` |
| Enum | `PascalCase`, variantes `PascalCase` | `Statut::Officielle` |
| Variable locale | `snake_case`, intention explicite | `fiche_trouvee`, `temps_avent` |
| Constante | `SCREAMING_SNAKE_CASE` | `MAX_RESULTATS_RECHERCHE` |
| Booléen | Préfixe `est_`, `peut_`, `a_` | `est_admin`, `peut_modifier` |
| Paramètre de durée de vie | `'a`, `'db` | Minuscule, court |

### Préfixes d'action pour les commandes Tauri
| Préfixe | Usage |
|---|---|
| `get_` | Récupérer un enregistrement unique |
| `lister_` | Récupérer une liste |
| `rechercher_` | Recherche filtrée |
| `creer_` | Créer un enregistrement |
| `modifier_` | Modifier un enregistrement existant |
| `supprimer_` | Supprimer un enregistrement |

### Langue
- Tous les identifiants métier en **français** (`fiche`, `dossier`, `temps_liturgique`).
- Les termes techniques Rust restent en anglais (`error`, `result`, `handler`).

### Interdictions
- Abréviations : `f`, `d`, `usr`, `res` → interdit.
- Préfixe `do_`, `handle_`, `process_` sans précision → interdit.

## Référence
- Structure des dossiers → ADR 017
- Documentation des fonctions publiques → ADR 020
