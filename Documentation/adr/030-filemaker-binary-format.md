# ADR 030 : Format Binaire FileMaker 11 (Reverse-Engineering)

## Statut
Proposé

## Contexte
Le pipeline V1 (Regex-based cleaning) parvenait à extraire du texte mais laissait de nombreux résidus structurels binaires dans les données. Pour atteindre 100% de fidélité, nous devons comprendre et parser la structure binaire native des fichiers `.lit`.

## Décisions

### 1. Encodage Global
L'intégralité du fichier (records et métadonnées) est obfusquée via une opération **XOR** avec la valeur constante `0x5A`.

### 2. Séparation des Records
L'enveloppe universelle de séparation des records est la séquence d'octets bruts (non décodés) :
`40 30 c1`
Ce qui correspond, une fois décodé via XOR 0x5A, à :
`1a 6a 9b`

### 3. Identification des Records & "Echo" d'ID
L'ID interne (14 chiffres) est stocké au format ASCII mais aussi **XORé** 0x5A à l'intérieur des segments de données.
- **Pattern typique** : `[Lettre optionnelle][14 chiffres][Scories binaires]`.
- **Exemple de scories après ID** : `œ`, `…`, `ﬁ`, `‹`, `”`, `’`, `◊`.
- **Raison** : FileMaker semble préfixer chaque bloc de donnée par l'ID du record pour assurer l'intégrité lors de la reconstruction.

### 4. Marqueurs de Champs
FileMaker 11 utilise des marqueurs d'octets spécifiques pour structurer les données :
*   **Séparateur Majeur (`FM_06`)** : `0x06` (Original) -> `0x5C` (`\`) après XOR. C'est le point d'entrée principal pour splitter les rubriques.
*   **Sous-marqueurs de Structure** :
    *   `0x01` (Source) -> `0x5B` (`[`) après XOR.
    *   `0x02` (Source) -> `0x58` (`X`) après XOR.
    *   `0xDA`, `0x80`, `0x1e`, `0x1f` sont également présents comme métadonnées de style ou de répétition.

### 5. Étiquettes (Labels) de Rubriques
Les données sont précédées d'étiquettes de 1 à 4 caractères (Majuscules ou `_`).
*   `PF` : Titre (Fiche principale)
*   `TxtPage`, `G`, `T`, `V`, `ZV` : Zones de contenu textuel (dépend du fichier)
*   `SE`, `SF`, `SG` : Auteur / Source
*   `_T` : ID technique de liaison

### 6. Encodage des Valeurs
Les chaînes de caractères après étiquette utilisent l'encodage **Mac Roman**.

### 7. Stratégie de Pureté "Chirurgicale" (V2.2)
Pour atteindre 100% de pureté, le pipeline applique :
1. **Regex de Nettoyage Agressif** : `^[A-Z_]?\d{14}[a-zA-Z\x80-\xff _¿~z…œ\"ﬁ‹”’◊]*`. Cette regex supprime l'ID injecté par FileMaker et ses scories binaires de bordure.
2. **Filtrage de Poids** : Les segments textuels dont le ratio de caractères alphanumériques est trop faible sont ignorés.
3. **Validation de Titre** : Rejet des titres commençant par `\_T` (pointeurs techniques).

## Implications
*   Passage à un script `pass1_extract_v2.py` (V2.2) qui réalise un nettoyage binaire en amont du mapping.
*   Simplification drastique du JSON final (supression des champs de traçabilité technique comme `raw_fields`).
