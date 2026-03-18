#!/bin/bash
# Lance FileMaker Pro 21 avec le préfixe Wine dédié

WINEPREFIX="/home/mous_tik/.wine_fmp21"
APP_PATH="C:\Program Files\FileMaker\FileMaker Pro\FileMaker Pro.exe"

echo "🚀 Lancement de FileMaker Pro 21..."
WINEPREFIX="$WINEPREFIX" wine "$APP_PATH" "$@"
