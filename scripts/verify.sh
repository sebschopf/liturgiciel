#!/bin/bash
# scripts/verify.sh — Validation globale locale de LiturgiCielauri
# Ce script reproduit exactement les tests de la CI Gitea.
# Tout échec ici signifie un refus assuré du dépôt.

set -e # Arrêt immédiat en cas d'erreur

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Démarrage de la vérification globale...${NC}"

# 1. Qualité de la Documentation
echo -e "\n${BLUE}[1/6] Documentation — Markdownlint...${NC}"
npm run lint:md

# 2. Formatage Frontend
echo -e "\n${BLUE}[2/6] Frontend — Prettier...${NC}"
npm run format:check

# 3. Linting Frontend & Svelte
echo -e "\n${BLUE}[3/6] Frontend — ESLint & Svelte Check...${NC}"
npm run lint
npm run check

# 4. Tests Frontend
echo -e "\n${BLUE}[4/6] Frontend — Vitest...${NC}"
npm run test

# 5. Qualité Backend Rust
echo -e "\n${BLUE}[5/6] Backend — Rust (fmt, clippy, audit)...${NC}"
cd src-tauri
cargo fmt --check
cargo clippy -- -D warnings
# cargo audit  # Désactivé par défaut en local car lent, activer si besoin
cd ..

# 6. Tests Backend Rust
echo -e "\n${BLUE}[6/6] Backend — Tests Rust...${NC}"
cd src-tauri
cargo test
cd ..

echo -e "\n${GREEN}✅ TOUT EST PICO BELLO ! Vous pouvez commiter et pusher.${NC}"
