# ADR 026 : Stratégie de Langue (UI et Contenu Liturgique)

## État
Accepté

## Question
> *En quelle langue est l'interface ? Les fiches peuvent-elles être dans d'autres langues ?*

## Contexte
L'analyse du dossier `Extensions/` de LiturgiCiel 2010 révèle que l'application FileMaker originale supportait 10 langues d'interface et des dictionnaires orthographiques en français, allemand, italien, espagnol, néerlandais, suédois et portugais. LiturgiCielauri cible les Églises réformées suisses, qui utilisent trois langues liturgiques : le **français** (Vaud, Genève, Neuchâtel), l'**allemand** (Berne, Zurich) et l'**italien** (Tessin).

---

## Décision

### 1. Langue de l'interface applicative
**L'interface de LiturgiCielauri est exclusivement en français.**

Justification :
- La communauté initiale est francophone.
- Le multilinguisme de l'interface représente un coût de développement non justifié en Phase 1.
- Si une traduction est souhaitée à l'avenir, ouvrir une Issue `Kind/Feature` pour un ADR d'amendement.

### 2. Langue du contenu liturgique (Fiches)
**Les fiches peuvent être rédigées en français, allemand ou italien.**

Justification :
- LiturgiCiel était utilisé dans toute la Suisse réformée.
- Les dictionnaires présents (`francais.mpr`, `deutsch.mpr`, `italiano.mpr`) confirment un usage multilingue des textes.
- Ne pas stocker la langue d'une fiche rendrait la recherche et le tri impossibles pour les communautés germanophones ou italophones.

**Langues supportées pour le contenu :**
| Code | Langue | Communauté |
|---|---|---|
| `fr` | Français | EERV (Vaud), Genève, Neuchâtel |
| `de` | Allemand | Berne, Zurich et cantons alémaniques |
| `it` | Italien | Tessin |

### 3. Conséquence sur le modèle de données
Le champ `langue` est **obligatoire** sur l'entité `Fiche` (voir amendement ADR 015).

**Valeur par défaut** : `"fr"` (français), car la communauté fondatrice est francophone.

### 4. Recherche et filtrage
La langue est un axe de recherche : un utilisateur germanophone ne devrait pas être noyé dans des fiches françaises. Le filtre par langue est exposé dans l'interface de recherche.

### 5. Correcteur orthographique
Le correcteur orthographique (si implémenté) détecte automatiquement la langue depuis le champ `langue` de la fiche en cours d'édition.

## Alternatives considérées
- **Détection automatique de la langue** (NLP) : Rejeté. Trop complexe, trop fragile pour des textes courts et liturgiques.
- **Interface multilingue dès Phase 1** : Rejeté. Coût élevé, priorité à l'extraction et à la migration des données.

## Conséquences
- Le champ `langue` est ajouté à `Fiche` (amendement ADR 015).
- Tout message d'erreur ou label UI reste en français (ADR 018).
- Les conventions de nommage du code restent en français, quelle que soit la langue de la fiche (ADR 023, 024).
