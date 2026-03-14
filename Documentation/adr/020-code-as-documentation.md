# ADR 020 : Code as Documentation — Nommage et Commentaires

## État
Accepté

## Question
> *Quand est-ce que je commente mon code, et comment ?*

## Contexte
Un code illisible oblige à faire de l'archéologie pour comprendre l'intention. Le nommage et les commentaires sont la première couche de documentation — ils doivent être suffisants pour comprendre le POURQUOI sans lire une ligne de la documentation externe.

## Décision

### Règle fondamentale
> Les commentaires expliquent le **POURQUOI**. Le code explique le **QUOI**.

```rust
// ✅ Bon : explique le POURQUOI
// Le statut "officielle" est protégé par décision synodale (ADR 015).
// Seul l'administrateur peut le modifier.
if fiche.statut == Statut::Officielle && !utilisateur.est_admin() {
    return Err(AppError::Forbidden("Texte officiel protégé".into()));
}

// ❌ Mauvais : le QUOI est déjà visible dans le code
// Vérifie si le statut est officielle et si l'utilisateur est admin
if fiche.statut == Statut::Officielle && !utilisateur.est_admin() {
```

## Conséquences
- Toute fonction `pub` sans `///` dans `services/` est refusée à la revue de code.

## Référence
- Conventions de nommage frontend → ADR 023
- Conventions de nommage backend → ADR 024
