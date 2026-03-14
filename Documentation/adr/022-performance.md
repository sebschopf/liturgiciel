# ADR 022 : Performance Délibérée du Code

## État
Accepté

## Question
> *Quand et comment optimiser les performances, sans optimisation prématurée ?*

## Contexte
L'optimisation prématurée est une source majeure de complexité inutile. Mais négliger les choix évidents de performance crée une dette difficile à résorber. Ce document définit les règles de performance qui s'appliquent **dès l'écriture** (sans mesurer) et celles qui nécessitent **une mesure avant d'agir**.

## Décision

### Règle fondamentale
> Appliquer les bonnes pratiques évidentes dès l'écriture. N'optimiser davantage que si une mesure prouve un problème.

---

### Optimisations appliquées systématiquement (sans mesurer)

#### Rust
| Pratique | Correct ✅ | À éviter ❌ | Raison |
|---|---|---|---|
| Références vs copies | `fn f(s: &str)` | `fn f(s: String)` | Clone inutile = allocation mémoire |
| Async correct | `async fn` + `await` | Blocage du thread | Tauri = multithreadé |
| Gestion d'erreurs | `?` operator | `.unwrap()` | Panique en production |

#### Svelte 5
| Pratique | Correct ✅ | À éviter ❌ | Raison |
|---|---|---|---|
| Valeurs calculées | `$derived(total)` | Calcul dans le template | Recalcul à chaque render |
| Images | `loading="lazy"` | Chargement immédiat | Délai perçu à l'ouverture |
| Listes longues | Composant `VirtualList` | `{#each grand_tableau}` | Rendu de milliers de DOM nodes |

#### SurrealDB
| Pratique | Correct ✅ | À éviter ❌ | Raison |
|---|---|---|---|
| Index sur champs filtrés | `DEFINE INDEX ON fiche FIELDS titre` | Aucun index | Scan complet de table |
| Limiter les résultats | `SELECT ... LIMIT 50` | `SELECT *` sans limite | Résultats infinis non paginés |
| Champs nécessaires | `SELECT titre, texte FROM fiche` | `SELECT *` | Données inutiles transférées |

---

### Optimisations conditionnelles (mesurer d'abord)

Ces optimisations ne s'appliquent **que si une mesure (profiling) prouve un goulot d'étranglement** :

| Optimisation | Outil de mesure | Seuil déclencheur |
|---|---|---|
| Cache LRU sur les services | `cargo flamegraph` | Requête > 50ms répétée |
| Pagination des résultats | Temps de réponse UI | > 200ms pour une liste |
| Compilation Svelte en SSG | Lighthouse score | FCP > 1.5s |

**Avant toute optimisation conditionnelle** : ouvrir une Issue `Kind/Enhancement` avec les mesures comme preuve. Pas de micro-optimisation sans données.

## Conséquences
- Les bonnes pratiques du tableau "systématique" sont vérifiables à la revue de code.
- Aucune optimisation avancée sans mesure documentée dans la PR.
