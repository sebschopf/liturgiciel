# ADR 015 : Entités du Domaine Métier (Modèle LiturgiCielauri)

## État
Amendé — voir [Historique des amendements](#historique-des-amendements)

## Contexte
L'analyse des fichiers FileMaker (`.lit`) et de la documentation officielle de LiturgiCiel révèle que le logiciel est un **gestionnaire de répertoire liturgique**, pas un simple lecteur de textes. Avant de concevoir la base de données, il faut nommer et justifier les entités du domaine. Ce document est la référence unique pour savoir **ce qu'est une Fiche, un Dossier, une Célébration**, etc.

---

## Décision

### Entités retenues et leurs justifications

#### `Fiche` — L'unité de contenu liturgique
**Ce que c'est** : Un texte liturgique atomique et réutilisable (prière, chant, lecture, silence, réponse).

**Pourquoi c'est une entité centrale** : Une Fiche existe indépendamment de tout culte. Elle peut être utilisée dans plusieurs célébrations, classée dans plusieurs dossiers, avoir des variantes. C'est l'objet que les utilisateurs cherchent, créent et partagent.

**Champs clés et leurs justifications** :
- `titre` est *facultatif* : une fiche peut n'avoir qu'un texte sans titre (ex: un silence musical).
- `statut` (`officielle` / `personnelle` / `protegee`) : les textes validés par l'Église sont protégés contre toute modification. Une entité sans statut mettrait en danger l'intégrité des textes officiels.
- `langue` (`fr` / `de` / `it`) : les fiches peuvent être en français, allemand ou italien selon la communauté d'origine. Champ **obligatoire**, valeur par défaut `fr`. Sans ce champ, la recherche filtrée par langue et la correction orthographique sont impossibles. Voir [ADR 026](026-language-strategy.md).
- `smiley` (1–5) : l'appréciation personnelle guide la sélection lors de la préparation d'une célébration. C'est un champ subjectif, propre à chaque utilisateur.
- `date_creation` et `date_premiere_utilisation` sont **manuelles** : l'utilisateur saisit ces dates lui-même, car la fiche peut précéder sa saisie dans le système.

#### `TempsLiturgique` — Le calendrier de l'Église
**Ce que c'est** : Une période du calendrier liturgique chrétien (Avent, Noël, Carême, Pâques, Pentecôte, Temps ordinaire).

**Pourquoi c'est une entité** : Les utilisateurs recherchent des fiches **par temps liturgique**. C'est un axe de recherche principal. Ce n'est pas un simple tag : chaque temps a une couleur, un ordre et une signification théologique.

#### `Catalogue` — La source bibliographique
**Ce que c'est** : Le livre ou recueil dont est extraite une Fiche (ex: "EERV – Textes liturgiques 1997").

**Pourquoi c'est une entité** : Un même catalogue est référencé par des centaines de fiches. Normaliser évite la duplication et permet de filtrer par source.

#### `Culte` — Le modèle de célébration
**Ce que c'est** : Un gabarit de service religieux (Culte du Dimanche, Baptême, Mariage, Enterrement…). Il définit la **structure des moments liturgiques** qui le composent.

**Pourquoi c'est une entité différente de `Célébration`** : Le Culte est le *modèle* (invariant). La Célébration est une *instance* datée (le culte du 29 novembre 2020). Cette séparation permet de réutiliser le même gabarit pour chaque dimanche.

#### `MomentLiturgique` — La section ordonnée d'un culte
**Ce que c'est** : Une étape nommée dans le déroulement d'un Culte (Accueil, Psaume, Fraction, Bénédiction…).

**Pourquoi c'est une entité** : Les moments sont **hiérarchiques** (Repas du Seigneur > Fraction) et **ordonnés**. Ils constituent le "squelette" d'un culte dans lequel on insère les Fiches. Sans cette entité, impossible de respecter l'ordre liturgique officiel.

#### `Célébration` — L'instance réelle d'un culte
**Ce que c'est** : Un culte effectivement célébré, à une date et un lieu précis.

**Pourquoi on distingue Culte et Célébration** : Une Célébration associe des Fiches spécifiques à chaque moment. Deux célébrations du même type de Culte n'ont pas forcément les mêmes fiches. L'historique des célébrations constitue une mémoire précieuse de la communauté.

#### `Dossier` — Le classeur personnel ou partagé
**Ce que c'est** : Un regroupement de Fiches constitué par l'utilisateur (par thème, par culte à venir, etc.).

**Règles** : Les dossiers sont **personnels par défaut**. Le partage est explicite. Un dossier peut contenir des sous-dossiers (hiérarchie libre).

#### `Utilisateur` — Le créateur et propriétaire de contenu
**Rôle** : Auteur des Fiches et Dossiers personnels. Seul l'auteur peut modifier ou supprimer ses créations.

#### `Label` — La catégorie libre
**Ce que c'est** : Une étiquette libre (ex: "chant", "prière silencieuse", "SATB").

**Pourquoi c'est différent de `TempsLiturgique`** : Le Label est subjectif et créé par l'utilisateur, tandis que le Temps Liturgique est une structure officielle de l'Église.

---

### Entités exclues et pourquoi

| Entité | Raison de l'exclusion |
|---|---|
| `Caddie` | État temporaire géré côté client (Svelte `$state`). Voir ADR 013. |
| `Picto` | Icônes intégrées dans le bundle d'application, pas des données métier. |
| `Print` | Les modèles d'impression sont des templates frontend, pas des enregistrements DB. |

---

## Alternatives considérées
- **Tout dans une seule table `texte` avec un champ `type`** : Rejeté. Mélanger Fiches, Cultes et Moments dans une table générique rendrait les requêtes illisibles et perdrait la sémantique du domaine.
- **Fusionner `Culte` et `Célébration`** : Rejeté. On perdrait la capacité de réutiliser un gabarit de culte et l'historique serait illisible.

## Conséquences
- Chaque entité de ce document correspond à une table SurrealDB (voir ADR 016 pour les relations).
- Toute nouvelle entité doit faire l'objet d'un amendement de cet ADR via une PR.
- Le schéma technique (SurrealQL) vit dans `src-tauri/src/db/schema.surql`, PAS dans cet ADR.

---

## Historique des amendements

| Version | Date | Auteur | Description |
|---|---|---|---|
| v1.0 | 2026-03-13 | mous_tik | Version initiale — entités fondamentales du domaine |
| v1.1 | 2026-03-14 | mous_tik | Ajout du champ `langue` sur `Fiche` (suite à l'analyse de `Extensions/` — ADR 026) |
