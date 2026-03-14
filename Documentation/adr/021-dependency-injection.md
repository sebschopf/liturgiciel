# ADR 021 : Injection de Dépendances & Testabilité

## État
Accepté

## Question
> *Comment rendre ce code testable sans modifier l'environnement de production ?*

## Contexte
Un code qui instancie lui-même ses dépendances (connexion DB, clients HTTP) est impossible à tester sans un environnement réel. L'injection de dépendances inverse ce rapport : le module reçoit ce dont il a besoin — il ne le crée pas.

## Décision

### Règle fondamentale
> Les modules ne créent pas leurs dépendances. Ils les **reçoivent en paramètre**.

### Rust — Injection de la connexion DB

```rust
// ✅ Testable : la connexion est injectée
pub async fn get_fiche(db: &Surreal<Db>, id: &str) -> Result<Fiche, AppError>

// ❌ Non testable : connexion hardcodée, impossible à mocker
pub async fn get_fiche(id: &str) -> Result<Fiche, AppError> {
    let db = db::connect().await?; // impossible à remplacer dans un test
}
```

**En test**, on passe une connexion vers une DB en mémoire (`Surreal::new(Mem::default())`).
**En production**, Tauri injecte la connexion réelle via l'état global (`tauri::State<DbConnection>`).

### Svelte 5 — Injection via Props

```svelte
<!-- ✅ Testable : les données arrivent via $props -->
<script lang="ts">
  let { fiche }: { fiche: Fiche } = $props();
</script>

<!-- ❌ Non testable : le composant appelle lui-même l'API -->
<script lang="ts">
  const fiche = await getFiche(id); // impossible à mocker dans Vitest
</script>
```

Les composants Svelte reçoivent leurs données via `$props`. Les appels API se font dans les **Stores** ou dans les **layouts/routes**, pas directement dans les composants.

### Les mocks dans les tests Rust
```rust
#[cfg(test)]
mod tests {
    use surrealdb::engine::local::Mem;

    #[tokio::test]
    async fn test_get_fiche_introuvable() {
        let db = Surreal::new::<Mem>(()).await.unwrap();
        let result = get_fiche(&db, "id_inexistant").await;
        assert!(matches!(result, Err(AppError::NotFound(_))));
    }
}
```

## Conséquences
- Toute fonction de `services/` qui crée une connexion DB en interne est un échec de conception.
- Les composants Svelte qui appellent l'API directement ne peuvent pas être testés avec Vitest.
- Couverture de tests de 80% atteignable uniquement si ce principe est respecté (ADR 005).
