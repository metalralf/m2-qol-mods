#!/usr/bin/env bash
# Metin2 kliens indító — wine + DXVK + GameMode + P-magos rögzítés
# Használat:
#   ./run-metin2.sh            # normál indítás
#   ./run-metin2.sh --hud      # MangoHud overlay (FPS/CPU/GPU)
#   ./run-metin2.sh --log      # rejtett naplózás CSV-be (Shift+F2 = ki/be)
#   ./run-metin2.sh --log --noesync   # esync nélküli teszt (ha gyanús)
set -e
cd "$(dirname "$(readlink -f "$0")")"

export WINEDEBUG=-all

# P-magokra rögzítés (egyszálú motor; az E/LPE magokon fullad).
# Hibrd CPU-n (P+E): P = 0-3, E = 4-11, LPE = 12-13 (példa Arrow Lake-re).
# Más CPU-n ellenőrizd az lscpu -e kimenetet.
PIN="0-3"
if command -v taskset >/dev/null && taskset -c "$PIN" true 2>/dev/null; then
    AFFINITY=(taskset -c "$PIN")
else
    echo "figyelem: taskset/P-mag rögzítés nem elérhető, pin nélkül indul"
    AFFINITY=()
fi

# esync alapból bekapcsolva, --noesync flaggel kikapcsolható
ESYNC=1
for arg in "$@"; do
    case "$arg" in
        --hud)
            # Csak MangoHud (Afterburner-stílusú); a DXVK_HUD külön overlay lenne
            export MANGOHUD=1
            ;;
        --log)
            # Rejtett naplózás: overlay elrejtve, CSV-t ír kilépéskor
            export MANGOHUD=1
            export MANGOHUD_CONFIG=no_display
            mkdir -p mangologs
            echo "Rejtett naplózás: mangologs/ (Shift+F2 = ki/be, CSV kilépéskor)"
            ;;
        --noesync)
            ESYNC=0
            ;;
    esac
done
if [[ "$ESYNC" == "1" ]]; then
    export WINEESYNC=1
fi

echo "CPU pin: ${PIN} (P-magok) | esync: $([ $ESYNC == 1 ] && echo ON || echo OFF)"
exec "${AFFINITY[@]}" gamemoderun wine ./Madocsa2.exe
