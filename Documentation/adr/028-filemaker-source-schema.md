# ADR 028 : Schéma des Données Source FileMaker

## État

Accepté (2026-03-16)

## Question

> *Quelle est la structure réelle des données dans les fichiers FileMaker `.lit` et quels problèmes pose-t-elle pour la migration ?*

## Contexte

Les données liturgiques ont été saisies dans FileMaker Pro 10 (Windows) sur plusieurs années, sans schéma contraint. Le reverse engineering binaire (ADR 027) a révélé la structure suivante.

---

## Structure Découverte

### Inventaire Complet — 11 fichiers sources

L'application LiturgiCiel 2010 comprend **11 fichiers `.lit`** (FileMaker Pro 10/11). Seule une partie contient du contenu liturgique exploitable :

| Fichier | Rôle | Format Records | Priorité |
|---|---|---|---|
| `Fiches.lit` | Base principale : titre (`PF`), auteur, ID utilisateur | `[J.YK[0-9]{4}` | ✅ PRIMAIRE |
| `Echanges.lit` | Index de classement liturgique par rubriques | `[J.YK[0-9]{4}` | ✅ PRIMAIRE |
| `Sauvegarde.lit` | Backup textes complets (`TxtPage`) | `[Y1X¶` / `[Y2X¶` | ✅ PRIMAIRE |
| `Dossiers.lit` | Structure hiérarchique des dossiers | inconnu | 🔶 SECONDAIRE |
| `Temps.lit` | Vocabulaire des temps liturgiques | inconnu | 🔶 SECONDAIRE |
| `Catalogues.lit` | Organisation des catalogues | inconnu | 🔶 SECONDAIRE |
| `Liens.lit` | Liens et relations entre fiches | inconnu | 🔶 SECONDAIRE |
| `Label.lit` | Définitions des labels de rubriques | inconnu | ⚪ UI FileMaker |
| `Picto.lit` | Pictogrammes et icônes | binaire | ⚪ UI FileMaker |
| `Print.lit` | Paramètres d'impression | binaire | ⚪ UI FileMaker |
| `Transfert/Transfert.lit` | Fichier de transfert (export) | inconnu | 🔶 À explorer |

> **Note ADR 030** : Le format binaire exact de chaque fichier est documenté dans [ADR 030](030-filemaker-binary-format.md).

---

### Structure Universelle des Records
Le reverse engineering (ADR 030) a confirmé que tous les fichiers .lit partagent une structure binaire commune, bien que leur rôle sémantique diffère.

#### 1. Le Séparateur Universel
Tous les records sont délimités par la séquence `\x1aj\x9b`. Un "record conceptuel" (une fiche liturgique) est souvent fragmenté en plusieurs records physiques à travers différents fichiers.

#### 2. Rôle des Fichiers Sources (Stratégie Zero-Fragmentation)
*   **Sauvegarde.lit** : Contient le texte liturgique brut dans la rubrique longue `TxtPage`. C'est la source de la "vérité textuelle".
*   **Fiches.lit** : Contient les métadonnées de haut niveau : Titre (`PF`), Auteur (`SE`, `SF`), Source (`VN`).
*   **Echanges.lit** : Contient les rubriques de classement (Temps, Occasions) et les liens `WT` (Working Tag) qui relient les différentes couches de données d'un même ID.

#### 3. Réconciliation par ID
L'ID unique de 14 chiffres présent dans chaque fragment est le seul pivot fiable permettant de reconstruire la fiche complète.

---

### Champs Structurés (Labels FileMaker — Format A)

| Label | Champ Cible | Exemple |
|---|---|---|
| `\PF` | titre | `"Pour la lecture de l'Évangile"` |
| `\TxtPage` | contenu principal | long texte de prière |
| `\SEG` / `\SF` | auteur | `"Nathalie Schopfer"` |
| `\LP` | date création | `"24/11/2005"` (format Mac) |
| `\RY` | date modification | `"12/03/2010"` |
| `\VN` / `\VN30` | notes bibliographiques | `"Vivre ensemble 48"` |
| `\QA` | verset / réponses | classification `verset` |
| `\UE` | lectures / récit | classification `texte` |

### Rubriques de Classement (`all_fields` — depuis Echanges.lit)

Les rubriques suivent le pattern `[Lettre][Occasion]` (quand et pour qui utiliser la fiche) :

| Exemple de Label | Signification |
|---|---|
| `JTemps`, `DTemps`, `CTemps`, `ITemps` | Temps liturgique |
| `DTous`, `vTous` | Applicable à tous les temps |
| `GVendredi` | Vendredi Saint |
| `UEpiphanie` | Épiphanie |
| `QAdolescence` | Public : adolescents |
| `zInstallation`, `CInstallation` | Occasion : installation de pasteurs |
| `LCar` | Carême |
| `PPentec` | Pentecôte |
| `FB` | Bénédiction (?) |

---

## Problèmes Identifiés

### 1. Incohérence des noms de rubriques (chaos sémantique)

Le même **concept liturgique** est exprimé par des labels différents selon la personne qui a saisi :

| Concept | Labels trouvés |
|---|---|
| Pentecôte | `PPentec`, `UEpiphanie` (confusion), `vTous` avec valeur "PentecÙte" |
| Temps pascal | `ITemps: "pascal"`, `JTemps: "ordinaire Culte pascal"` |
| Carême | `LCar`, `ITemps: "carÍme"` |
| Tous los temps | `DTous`, `vTous`, `JTemps: "ordinaire"` |

### 2. Artefacts d'encodage

Certains champs ont été saisis sous Windows (cp1252) mais décodés en mac_roman, produisant :

| Vu | Attendu |
|---|---|
| `È` | `é` |
| `Ë` | `è` |
| `Ù` | `ô` |
| `Í` | `ê` ou partie d'ordinal |
| `ß` | caractère parasite |

### 3. Champs coupés à la frontière d'un caractère non-ASCII

Exemple : le label `PPentec` au lieu de `PPentecôte` — le `ô` étant multi-octet, il a tronqué le nom de label.

### 4. Padding binaire dans les valeurs

Certaines valeurs contiennent des résidus binaires :
- `K K K K K K` = octets `0x11` XOR'd → zones nulles FileMaker
- `ZZZZZ...` = octets `0x00` XOR'd → padding de fin de champ
- Séquences parasites : `JöW`, `ZQ`, `ZX` = résidus de structure binaire

### 5. Records sans contenu principal

Certains records ont `TxtPage` vide et `PF` vide. Seules des rubriques de classement sont présentes (ex: `JTemps: "ordinaire"`). Ce sont des **fiches de classement** ou des **entrées orphelines**.

### 6. Valeurs mixtes dans une même rubrique

Certaines valeurs mélangent plusieurs concepts :
```
JTemps: "ordinaire Culte pascal"
```
→ le champ contient à la fois le temps liturgique ET le type de culte, sans séparateur fiable.

---

## Champs Binaire Identifiés (Structural IDs)

Plutôt que des labels textuels (`\PF`), le moteur FileMaker utilise des IDs de champs numériques codés dans les headers binaires :

| ID Champ (Hex XOR'd) | Signification Probable |
|---|---|
| `0x23` | Contenu Principal (Long Text) |
| `0x27` | Titre de la Fiche |
| `0x0E` | Reference ID (14 chars) |
| `0x1F` | Auteur / Propriétaire |

---

## Données "Propres" vs "Bruit" (V2 Analysis)

---

## Normalisation V2.2 (Cible Application)

À partir de l'analyse structurelle, nous avons figé le schéma cible épuré :
- `id_fiche` : L'ID 14 chiffres (ex-`id_filemaker`).
- `types` : Classification auto (`prière`, `chant`, `prédication`, `verset`, `texte`, `autres`).
- `tags_communs` : Fusion des anciennes `occasions` et des labels non-mappés.
- `date_creation` / `date_modification` : Extraits des labels `LP` et `RY`.

## Conséquences

- Ce schéma est optimisé pour SurrealDB et l'application finale.
- Les données techniques (`raw_fields`, `v`) sont supprimées de l'export final pour ne garder que la "substance" liturgique.
- La pureté est assurée par un nettoyage "chirurgical" des IDs régnant à l'intérieur des segments de texte.
