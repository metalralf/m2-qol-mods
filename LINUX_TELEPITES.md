# Metin2 kliens futtatása Linuxon (Wine + DXVK)

Teljes útmutató, hogyan fusson a kliens Linuxon **DLL-hiba nélkül**, jó FPS-sel.
Arch/EndeavourOS parancsokra írva (más disztrón a csomagkezelő neve más).

## 1. Telepítés (egyszer)

```bash
# Wine + GameMode + MangoHud (Arch repó)
sudo pacman -S wine gamemode mangohud

# DXVK (d3d9 -> Vulkan, nagy FPS-nyereség DX9 játékoknál)
# AUR-ból a stabil binárist ajánljuk:
yay -S dxvk-bin
```

DXVK telepítése a wine prefixbe (a wine 11.x wow64 buildhez DXVK >= 2.3 kell):

```bash
/usr/share/dxvk/setup_dxvk.sh install
```

Ellenőrzés: `ls -la ~/.wine/drive_c/windows/system32/d3d9.dll` — 7 MB körüli méret = a DXVK-é.

## 2. Indítás — és a "DLL hiba" elkerülése

**A leggyakoribb hiba**: `SpeedTreeRT.dll` (vagy más DLL) "nem található" — pedig a
fájl ott van a kliens mappájában. Oka: **nem a kliens mappájából indítottad a játékot**.
A kliens a saját könyvtárából tölti a DLL-eket, a `pack/` mappát és a `locale.cfg`-t.

Mindig így indíts (a launcher ezt már elvégzi):

```bash
cd <a-kliens-mappaja>
./run-metin2.sh            # normál
./run-metin2.sh --hud      # FPS overlay (MangoHud)
./run-metin2.sh --log      # rejtett CSV naplózás (Shift+F2 = ki/be)
```

A `run-metin2.sh` a repó gyökerében van — tedd a kliens mellé, és `chmod +x run-metin2.sh`.

## 3. Mit csinál a launcher

- **`taskset -c 0-3`** — a főszálat a P-magokra rögzíti. Az egyszálú motor egy
  E/LPE magon 400 MHz-en fullad, miközben a HUD "kihasználatlan" CPU-t mutat
  (ez a klasszikus "sehol nincs maxolva, mégis 14 FPS" jelenség).
- **`gamemoderun`** — GameMode: performance governor + nice a játéknak.
- **`WINEESYNC=1`** — esync (ha gondot okoz: `--noesync`).
- **`--hud`** — MangoHud overlay (FPS, CPU%, GPU%, hőmérséklet).
- **`--log`** — rejtett CSV naplózás a `mangologs/` mappába (kilépéskor íródik).

## 4. Ajánlott metin2.cfg (FPS vs minőség)

```ini
WIDTH 1440          ; a monitorod natív felbontása
HEIGHT 900
BPP 32
FREQUENCY 60
SOFTWARE_CURSOR 1   ; Wayland/XWayland alatt a hardverkurzor akad
OBJECT_CULLING 1
VISIBILITY 2        ; 1 = max FPS, 3 = max látótávolság
MUSIC_VOLUME 0.000  ; a zene CPU-t eszik
SHADOW_LEVEL 2      ; 0 = árnyék ki (max FPS), 3 = minőség
WINDOWED 1
```

> **Figyelem**: a kliens kilépéskor **felülírja a metin2.cfg-t** — csak zárt játék
> mellett szerkeszd, különben elvesznek a módosítások.

## 5. FPS tippek

| Mit | Mit ad |
|---|---|
| DXVK (`d3d9` → Vulkan) | 20-50% FPS-nyereség DX9 játékoknál a wined3d-hez képest |
| `SHADOW_LEVEL 0` | a legnagyobb egyetlen nyerő sok mobnál |
| `VISIBILITY 1` | kevesebb kirajzolt objektum |
| P-mag pin (`taskset`) | egyszálú motor nem vándorol E/LPE magra |
| `MUSIC_VOLUME 0` | kevesebb CPU a hangdekódolásra |
| `--hud` | nézd meg, CPU vagy GPU a szűk keresztmetszet |

A játék **engine-szinten 60 FPS-re korlátozott** — ezt csak C++ forrásból lehet
feloldani (a kliens forrása a git.old-metin2.com-on elérhető).

## 6. Ha mégis hiba lenne

- **`syserr.txt` / `ErrorLog.txt`** a kliens mappájában — ezt nézd, és küldd el a
  hibakeresőnek. A Python tracebackek is ide íródnak.
- Ismert ártalmatlan üzenetek: `CursorImage.__del__` hiba kilépéskor,
  `GRANNY: run-time type tag ... doesn't match` (régi modellek, auto-konverzió),
  `Cannot find item by 0` (item-tábla eltérés, csak logzaj).
- Ha a Miles (`mss32.dll`) hang crash-t okoz: `winecfg → Audio → Disabled`.
