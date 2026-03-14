# ADR 016 : Stratégie de Relations entre Entités (Graphe vs Champ)

## État
Accepté

## Contexte
Une fois les entités définies (ADR 015), il faut décider COMMENT elles se connectent. SurrealDB offre deux mécanismes : les **champs de type `record<>`** (lien direct, comme une clé étrangère) et les **tables de relation `TYPE RELATION`** (graphe orienté, traversable dans les deux sens). Ce choix impacte la façon dont on interroge les données.

---

## Décision

### Règle de choix : Champ direct vs Relation graphe

| Critère | Champ direct `record<>` | Table de relation (graphe) |
|---|---|---|
| **Cardinalité** | 1 entité → 1 entité | N entités → N entités |
| **Navigation inverse** | Nécessite une requête explicite | Traversée native (`<-relation<-`) |
| **Métadonnées sur le lien** | Difficile | Naturel (champ sur la relation) |
| **Suppression** | Risque de référence orpheline | Relation supprimable proprement |

---

### Relations retenues et leurs justifications

#### Champs directs (liaison simple 1→1 ou N→1)

| Champ | Sur | Vers | Justification |
|---|---|---|---|
| `auteur` | `fiche`, `dossier` | `utilisateur` | Une fiche a un seul auteur. Pas de multi-auteur. |
| `catalogue_ref` | `fiche` | `catalogue` | Une fiche vient d'une seule source bibliographique. |
| `temps_liturgique` | `fiche` | `temps_liturgique` | Association directe, pas de métadonnées sur le lien. |
| `parent` | `moment_liturgique` | `moment_liturgique` | Hiérarchie d'arbre simple (autoréférence). |
| `parent` | `dossier` | `dossier` | Même raisonnement pour les sous-dossiers. |
| `culte` | `moment_liturgique` | `culte` | Un moment appartient à un seul culte. |
| `culte` | `celebration` | `culte` | Une célébration suit un seul modèle de culte. |

#### Tables de relation (graphe, liaison N↔N)

| Relation | De | Vers | Justification |
|---|---|---|---|
| `est_variante_de` | `fiche` | `fiche` | Une fiche peut dériver de plusieurs originaux. La relation doit être traversable dans les deux sens (trouver toutes les variantes d'un original). |
| `renvoie_vers` | `fiche` | `fiche` | Renvoi croisé bidirectionnel. Le lien porte un commentaire optionnel ("pour la même thématique"). |
| `dans_dossier` | `fiche` | `dossier` | Une fiche peut être dans N dossiers. Un dossier peut contenir N fiches. |
| `tagged` | `fiche` | `label` | Association libre N↔N. |
| `moment_fiche` | `moment_liturgique` | `fiche` | La relation porte des métadonnées : `celebration` (dans quelle instance ?) et `ordre` (quelle position ?). |
| `partage_dossier` | `utilisateur` | `dossier` | La relation porte la permission (`peut_modifier: bool`). |

---

### Cas particulier : L'ordre dans `moment_fiche`
La relation entre un Moment et une Fiche dans le contexte d'une Célébration porte **deux métadonnées** :
- `celebration` : dans quelle instance de culte (pour isoler les fiches du 29/11/2020 de celles du 06/12/2020)
- `ordre` : position de la fiche dans le moment (si plusieurs fiches pour un même moment)

Ce n'est possible qu'avec une table de relation, pas avec un simple champ.

---

## Alternatives considérées
- **Tout en tables de relation** : Rejeté. Sur-complexifie les liens simples (1→1) sans gain.
- **Tout en champs directs avec tableaux** (ex: `fiches: array<record<fiche>>`) : Rejeté. SurrealDB ne supporte pas les recherches inverses efficaces sur les tableaux pour les cas N↔N, et les métadonnées sur les liens sont impossibles.

## Conséquences
- Le schéma technique SurrealQL vit dans `src-tauri/src/db/schema.surql`.
- Toute nouvelle relation doit préciser : cardinalité, besoin de navigation inverse, métadonnées éventuelles.
- La distinction graphe/champ doit être justifiée dans la PR qui introduit la relation.
