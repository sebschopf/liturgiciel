#!/bin/bash
# Lance LiturgiCiel correctement via Bottles/Wine
# Usage: bash launch_liturgiciel.sh

BOTTLE="$HOME/.var/app/com.usebottles.bottles/data/bottles/bottles/LiturgiCiel__153"
RUNNER="$HOME/.var/app/com.usebottles.bottles/data/bottles/runners/soda-9.0-1/bin/wine64"
STANDALONE="$BOTTLE/standalone"
APP_DIR="/home/mous_tik/Documents/LiturgiCiel 2010 WIN"

echo "🧹 Nettoyage des processus Wine résiduels..."
pkill -f "wineserver" 2>/dev/null
pkill -f "wine64" 2>/dev/null
pkill -f "LiturgiCiel" 2>/dev/null
sleep 2

echo "🔗 Vérification des DLLs..."
for dll in "$APP_DIR"/*.dll; do
  name=$(basename "$dll")
  target="$BOTTLE/drive_c/windows/system32/$name"
  [ -L "$target" ] || ln -sf "$dll" "$target"
done

echo "🚀 Lancement de LiturgiCiel..."
cd "$APP_DIR"
bash "$STANDALONE" "$RUNNER" "LiturgiCiel2010WIN.exe"
