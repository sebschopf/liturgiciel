# ADR 024 : Conventions de Nommage Backend (Rust / Tauri)

## État

Accepté

## Question

> *Comment nommer les modules, fonctions et structures dans le backend Rust ?*

## Décision

### 1. Modules et Fichiers

- **Format** : `snake_case`
- **Exemple** : `src/services/db_manager.rs`
- **Justification** : Standard Rust (RFC 433).

### 2. Structures, Enums et Traits

- **Format** : `PascalCase`
- **Exemple** : `struct GestionnaireFiche`, `enum TypeVerset`

### 3. Fonctions et Variables

- **Format** : `snake_case`
- **Langue** : Français (ADR 018)
- **Exemple** : `fn extraire_texte()`, `let liste_tags = vec![]`

### 4. Macros

- **Format** : `snake_case!`
- **Exemple** : `log_info!()`

### 5. Commands Tauri (Appelables depuis le JS)

- **Format** : `snake_case` (côté Rust), mappées en `camelCase` par Tauri si configuré, mais nous préférons garder la cohérence.
- **Décision** : Les commands Tauri utilisent le `snake_case` côté Rust.
- **Exemple** : `#[tauri::command] fn get_fiche_by_id()`

## Référence

- Organisation du Code → ADR 017
- Code as Documentation → ADR 020
- Langue de l'interface → ADR 018
