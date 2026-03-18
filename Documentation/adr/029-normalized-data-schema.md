# ADR 029 : Schéma Normalisé des Données LiturgiCielauri

## État

Accepté (2026-03-16)

## Question

> *Quel schéma de données adopter pour LiturgiCielauri, au regard des problèmes identifiés dans les données sources (ADR 028) ? Comment normaliser les rubriques de classement ? Vocabulaire contrôlé ou libre ?*

---

## Contexte

L'analyse des données FileMaker (ADR 028) a révélé un **chaos sémantique** des rubriques de classement : le même concept "Pentecôte" apparaît sous des dizaines de formes différentes, saisi librement par différents utilisateurs sur des années.

Pour LiturgiCielauri, deux approches s'affrontent :

| Approche | Avantage | Risque |
|---|---|---|
| **Vocabulaire libre** (comme FileMaker) | Flexible, saisie rapide | Chaos garanti à long terme |
| **Vocabulaire contrôlé** (enum SurrealDB) | Recherche cohérente, UI fiable | Rigide, nécessite une saisie guidée |
| **Hybride** (nom normalisé + alias libres) | Flexible ET cohérent | Complexité de validation |

---

## Décision

### 1. Entité Principale : `fiche`

La fiche est l'unité fondamentale. Elle est amendée par rapport à ADR 015 :

```sql
DEFINE TABLE fiche SCHEMAFULL;

DEFINE FIELD id_filemaker    ON fiche TYPE string;     -- ID FileMaker original (14 chiffres)
DEFINE FIELD id_utilisateur  ON fiche TYPE option<string>; -- Numéro user FileMaker (ex: "121")
DEFINE FIELD titre           ON fiche TYPE string;
DEFINE FIELD contenu         ON fiche TYPE string;     -- Texte liturgique principal
DEFINE FIELD auteur          ON fiche TYPE option<string>;
DEFINE FIELD source          ON fiche TYPE option<string>; -- Notes bibliographiques
DEFINE FIELD langue          ON fiche TYPE string DEFAULT "fr"; -- ADR 026
DEFINE FIELD fichier_origine ON fiche TYPE string;     -- "Fiches.lit" | "Echanges.lit" | "Sauvegarde.lit"
DEFINE FIELD incomplete      ON fiche TYPE bool DEFAULT false; -- vrai si contenu vide
DEFINE FIELD raw_fields      ON fiche TYPE option<object>; -- all_fields FileMaker bruts conservés

-- Classification liturgique normalisée
DEFINE FIELD temps_liturgiques ON fiche TYPE set<record<temps_liturgique>>;
DEFINE FIELD occasions          ON fiche TYPE set<record<occasion_liturgique>>;
DEFINE FIELD publics            ON fiche TYPE set<record<public_cible>>;

-- Tags : deux niveaux (voir §5)
DEFINE FIELD tags_communs      ON fiche TYPE set<record<tag>>;             -- tags partagés, définis
DEFINE FIELD tags_personnels   ON fiche TYPE set<record<tag_utilisateur>>; -- tags propres à un user
```

> [!IMPORTANT]
> `raw_fields` conserve les rubriques FileMaker d'origine intactes. On ne perd rien. La normalisation est une **couche ajoutée**, pas un remplacement.

---

### 2. Vocabulaire Contrôlé : `temps_liturgique`

**Décision : ENUM semi-ouvert.** Les valeurs sont prédéfinies mais extensibles via un nouvel ADR.

```sql
DEFINE TABLE temps_liturgique SCHEMAFULL;
DEFINE FIELD nom    ON temps_liturgique TYPE string; -- identifiant normalisé
DEFINE FIELD label  ON temps_liturgique TYPE string; -- label affiché dans l'UI
DEFINE FIELD ordre  ON temps_liturgique TYPE number; -- pour tri calendaire
```

**Valeurs canoniques initiales :**

| `nom` (clé) | `label` (UI) | `ordre` | Aliases FileMaker mappés |
|---|---|---|---|
| `avent` | Avent | 1 | `JTemps: "avent"`, `DTemps: "avent"` |
| `noel` | Noël | 2 | `GNoel`, `ITemps: "noël"` |
| `epiphanie` | Épiphanie | 3 | `UEpiphanie`, `GEpiphanie` |
| `ordinaire` | Temps Ordinaire | 4 | `JTemps: "ordinaire"`, `DTous: "les temps"` |
| `careme` | Carême | 5 | `LCar`, `ITemps: "carÍme"`, `DTemps: "carême"` |
| `semaine_sainte` | Semaine Sainte | 6 | `ITemps: "Íme/Semaine sainte"` |
| `paques` | Pâques | 7 | `ITemps: "pascal"`, `GVendredi` (Vendredi Saint) |
| `pentecote` | Pentecôte | 8 | `PPentec`, `vTous: "PentecÙte"` |
| `tous_temps` | Tous les temps | 0 | `DTous`, `vTous`, `JTemps: "ordinaire Culte"` |

---

### 3. Vocabulaire Contrôlé : `occasion_liturgique`

```sql
DEFINE TABLE occasion_liturgique SCHEMAFULL;
DEFINE FIELD nom   ON occasion_liturgique TYPE string;
DEFINE FIELD label ON occasion_liturgique TYPE string;
```

**Valeurs canoniques initiales :**

| `nom` | `label` | Aliases FileMaker |
|---|---|---|
| `culte_dominical` | Culte dominical | `DTemps: "ordinaire Culte"` |
| `installation` | Installation de pasteur | `zInstallation`, `CInstallation` |
| `mariage` | Mariage | `GMariage`, `zMariage` |
| `funerailles` | Funérailles / Deuil | `DFuner`, `zFuner` |
| `bapteme` | Baptême | `zBapteme` |
| `cene` | Sainte Cène / Communion | `DCene` |
| `confirmation` | Confirmation | `zConfirm` |
| `veille_pascale` | Veillée Pascale | `GVendredi`, `GPaques` |

---

### 4. Vocabulaire Semi-Ouvert : `public_cible`

```sql
DEFINE TABLE public_cible SCHEMAFULL;
DEFINE FIELD nom   ON public_cible TYPE string;
DEFINE FIELD label ON public_cible TYPE string;
```

| `nom` | `label` | Aliases FileMaker |
|---|---|---|
| `enfants` | Enfants | `QEnfants` |
| `adolescents` | Adolescents | `QAdolescence` |
| `jeunes` | Jeunes | `QJeunes` |
| `adultes` | Adultes | — (défaut) |
| `tout_public` | Tout public | `DTous` |

---

### 5. Tags : Deux Niveaux

**Décision : tags structurés ET personnels, jamais de string brut en base.**

#### Tags Communs (`tag`)

Tags partagés entre tous les utilisateurs. Définis à l'import FileMaker et maintenus par l'équipe.

```sql
DEFINE TABLE tag SCHEMAFULL;
DEFINE FIELD nom         ON tag TYPE string; -- clé (ex: "lien-oeuvres")
DEFINE FIELD label       ON tag TYPE string; -- affiché dans l'UI
DEFINE FIELD description ON tag TYPE option<string>;
DEFINE FIELD categorie   ON tag TYPE string; -- "theme" | "forme" | "usage" | "biblique"
```

**Exemples de tags communs initiaux (hérités des données FileMaker) :**

| `nom` | `label` | `categorie` |
|---|---|---|
| `priere` | Prière | `forme` |
| `psaume` | Psaume | `forme` |
| `cantique` | Cantique | `forme` |
| `lecture` | Lecture biblique | `forme` |
| `meditation` | Méditation | `forme` |
| `confession` | Confession de foi | `forme` |
| `bénédiction` | Bénédiction | `forme` |
| `action-de-grace` | Action de grâce | `theme` |
| `pardon` | Pardon / Réconciliation | `theme` |
| `esperance` | Espérance | `theme` |
| `creation` | Création | `theme` |
| `lumiere` | Lumière | `theme` |
| `reference-biblique` | Avec référence biblique | `usage` |
| `a-lire` | À lire à voix haute | `usage` |
| `interactif` | Participatif / Réponse | `usage` |

> [!NOTE]
> La liste des tags communs est extensible par les utilisateurs **avec validation communautaire** (ex: vote ou rôle admin). Un tag commun mal choisi pollue toute la base — il faut un filtre.

#### Tags Personnels (`tag_utilisateur`)

Tags créés librement par un utilisateur pour son usage propre. Invisibles pour les autres.

```sql
DEFINE TABLE tag_utilisateur SCHEMAFULL;
DEFINE FIELD nom         ON tag_utilisateur TYPE string; -- librement saisi par l'utilisateur
DEFINE FIELD proprietaire ON tag_utilisateur TYPE record<utilisateur>; -- lié à son créateur
DEFINE FIELD couleur     ON tag_utilisateur TYPE option<string>; -- pour l'UI (hex color)
```

**Comportement :**
- Un pasteur voit ses `tags_personnels` partout dans l'app, uniquement sur ses propres fiches
- Il peut créer autant de tags personnels qu'il veut, sans validation
- Il peut **proposer** un tag personnel à devenir commun (via workflow)
- À l'import FileMaker : les valeurs non mappées issues de `all_fields` → `tags_communs` provisoires (catégorie `"import_filemaker"`) en attente de validation

---

### 6. Règles de Normalisation (Mapping)

**Règle 1 — Prédominance du contenu sur le label**
Le classement est dérivé de la **valeur** du champ (ex: `"pascal"`) autant que du **nom du label** (ex: `ITemps`).

**Règle 2 — Cascade de mapping**
1. Valeur reconnue → `temps_liturgiques` / `occasions` / `publics` (vocabulaire contrôlé)
2. Valeur non reconnue mais pertinente → `tags_communs` avec catégorie `"import_filemaker"` (à valider manuellement)
3. Rien → stocké dans `raw_fields` uniquement

**Règle 3 — Alias tolérés, forme canonique obligatoire**
La recherche porte sur la forme canonique (`nom`). Les aliases sont résolus à l'import. Jamais en base.

**Règle 4 — Pas de multi-valeur dans un seul champ**
Si une valeur FileMaker mélange plusieurs concepts (`"ordinaire Culte pascal"`), elle est **éclatée** en plusieurs entrées de `temps_liturgiques`.

**Règle 5 — Conservateur face au doute**
Si le mapping est incertain, on ajoute en `tags_communs` provisoires plutôt que de forcer un mauvais classement. Jamais de perte.

---

### 6. Encodage : Règle de Correction

Les artefacts d'encodage (ADR 028) sont corrigés par une passe dédiée (`normalize_encoding.py`) AVANT le mapping :

| Artefact | Correction |
|---|---|
| `È` | → `é` |
| `Ë` | → `è` |
| `Ù` | → `ô` |
| `Í` | → `ê` |
| `ß` | → supprimé |
| `K K K K` | → supprimé (padding binaire) |
| `ZZZZZ` | → supprimé (padding binaire) |

---

## Pipeline de Normalisation (6 Passes)

```
[Fiches.lit] [Sauvegarde.lit] [Echanges.lit]
            │
            ▼ pass1_extract.py     (Passe 1 : Extraction Zero-Fragmentation & Labels 2-chars)
    liturgi_raw.json 
            │
            ▼ pass2_merge.py       (Passe 2 : Fusion sémantique + Titre Fallback + Liens WT)
    liturgi_merged.json
            │
            ▼ pass3_prune.py       (Passe 3 : Élagage des résidus binaire FileMaker)
    liturgi_pruned.json
            │
            ▼ pass4_encoding.py    (Passe 4 : Correction accents Mac Roman)
    liturgi_encoded.json
            │
            ▼ pass5_rubriques.py   (Passe 5 : Mapping vocabulaire contrôlé)
    liturgi_rubriques.json
            │
            ▼ pass6_export.py      (Passe 6 : Formatage final SurrealDB)
    liturgi_final_surrealdb.json
            │
            ▼ SurrealDB IMPORT
```

---

## Conséquences

- **Ce qui est bloqué** : `temps_liturgiques`, `occasions`, `publics` = records SurrealDB prédéfinis. Toute extension requiert un ADR.
- **Tags communs** : définis à l'import, maintenus par l'équipe, proposables par les utilisateurs via workflow de validation.
- **Tags personnels** : entièrement libres, liés à leur créateur, invisibles pour les autres — chaque pasteur a son propre espace de classification.
- **Ce que l'UI doit faire** : liste déroulante pour les classements normalisés + autocomplete partagé pour les tags communs + champ libre pour les tags personnels.
- **Ce qui est conservé** : `raw_fields` avec les données brutes FileMaker — traçabilité à 100%.
- L'ADR 015 est **amendé** : les entités `temps_liturgique`, `occasion_liturgique`, `public_cible`, `tag`, `tag_utilisateur` s'ajoutent au schéma.
