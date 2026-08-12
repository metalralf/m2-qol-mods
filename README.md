# Madocsa2 kliens — QoL modok

Kliensoldali (Python 2) minőségi javítások a Metin2 klienshez, saját repack eszközzel.
Minden mod a `pack/root/` script réteget módosítja + a `root.epk` újracsomagolásával él.

---

## Telepítés játékosoknak (nem kell semmihez érteni)

A kész `root.epk`/`root.eix` párt **a szerverüzemeltetőtől kapod** (nem a repóból —
az tartalmazza a szerver `serverinfo.py`-ját, az nem publikus). Telepítés:

1. **Biztonsági mentés**: másold ki a meglévő `pack/root.epk` és `pack/root.eix` fájlokat (a kliens mappában, a `pack/` almappában).
2. **Csere**: a kapott `root.epk` és `root.eix` fájlokat másold be a kliens `pack/` mappájába (a régiek helyére).
3. **Indítás**: indítsd a klienst a szokásos módon. Kész.

> **Fontos**: a modok ehhez a kliens-buildhez készültek. Másik szerver/kliens esetén a `patch/` diff-eket kell használni (lásd lentebb).

### Szerverüzemeltetőnek: a játékosok packet előállítani

```bash
# a repó pack/root/ fájljait másold a saját kliensed pack/root/ mappájába
# (a SAJÁT serverinfo.py-dat NEM írod felül!)
python3 pack_root.py      # a pack/ mappában: generálja a root.epk + root.eix-et
```
A kapott `root.epk`/`root.eix` terjeszthető a játékosoknak.

---

## Aktív modok és gombok

| Gomb | Funkció |
|---|---|
| **F5** | karakter-nevek tartós ki/be |
| **F7** | árnyék ki/be (FPS-nyerő sok mobnál) |
| **F8** | chat ablak ki/be |
| **F9** | kamera távolság (közel 1550 / távol 2300) |
| **F10** | köd ciklus 0/1/2 (több köd = kevesebb kirajzolt mob = több FPS) |
| **F11** | FPS/debug overlay (UFPS/RFPS) ki/be |
| **F12** | quest-gombok (az oldalsó levél-ikonok) ki/be |
| — | **Tooltip**: az item vnum megjelenik a normál item tooltipben |
| — | **MiniMap**: koordináta kijelzés a minimapon |

---

## Adminoknak: a modok fájljai és a repack

### Módosított fájlok (`pack/root/`)

| Fájl | Módosítás |
|---|---|
| `game.py` | F5/F7/F8/F9/F10/F11/F12 keybindek + a hozzájuk tartozó metódusok |
| `interfacemodule.py` | F12 quest-gomb kapcsoló (`ToggleQuestButtons`) |
| `uitooltip.py` | item vnum a tooltipben (`__SetNormalItemTitle`) |
| `constinfo.py` | `MINIMAP_POSITIONINFO_ENABLE = 1` |

A pontos eltérések az eredeti fájlokhoz képest a `patch/*.diff` fájlokban vannak.

### Repack (Linux, Python 3)

A packer a **`pack/root/` mappából** építi a `root.epk`-t és `root.eix`-et:

```bash
# függőség: liblzo2 (a packer LZO1X tömörítést használ)
sudo pacman -S lzo   # Arch/EndeavourOS
# vagy: sudo apt install liblzo2-2  (Debian/Ubuntu)

# szerkesztés után:
python3 pack_root.py          # újragenerálja a pack/root.epk + root.eix fájlokat
python3 pack_root.py --verify # ellenőrzés (CRC-k listázása)
```

### A pack formátum (ha valaki mélyebben akarja)

- `.eix` = index: `MCOZ` konténer (TEA titkosítás `gLZOData` kulccsal + LZO1X tömörítés), kicsomagolva: `EPKD` v2 fejléc + 192 bájt/bejegyzés.
- `.epk` = adat: minden fájl = `THeader(MCOZ, encryptSize, compSize, realSize)` + TEA titkosított (`gLZOData2` kulcs) LZO stream, `packedType=2`.
- Bejegyzés mezők: `index, filename[160], dw1, dw2, dw3, srcSize, crc, offset, packedType` — **`dw2 = crc32(fájlnév)`**, amit a kliens ellenőriz (ennél a hibánál bukott el minden rossz packer).
- 256 bájtra igazított offsetek, `dw3 = align256(srcSize)`.

---

## Biztonság / szabályok

- **NE kerüljön a repóba**: a `credentials` fájl (fiókjelszavak) és a `serverinfo.py` élő IP/port adatai. (A játékosok a saját kliensük `serverinfo.py`-jét használják — azt NEM szabad felülírni a modokkal.)
- A `root.epk` tartalma ehhez a szerverhez/klienshez kötött; más buildnél a `patch/` diff-eket kell újraalkalmazni.
- A Metin2 kliens a Ymir/Gameforge szellemi tulajdona — a modok csak script-szintű személyre szabások, a terjesztés a saját szervered játékosai körében történjen.

---

## Visszaállítás

- Játékos: tedd vissza a mentett `root.epk`/`root.eix`-et.
- Admin: `pack/root/` fájljait cseréld vissza az eredetiekre (vagy `patch/` diff-ek reverse alkalmazása), majd `python3 pack_root.py`.

---

## Referenciák és kapcsolódó dokumentáció

**A pack formátum megfejtéséhez használt források:**
- `git.old-metin2.com/metin2/client` — a 2014-es kliens forrása (EterPack, LZO/TEA, HybridCrypt)
- `git.old-metin2.com/metin2/server` — a szerver forrása (shop DB-séma, gamefiles)
- `github.com/NakiuS/Metin2Client` — klasszikus kliens-forrás (`EterPack.cpp`, `PythonBackground.cpp`, `CPythonSystem::SetShadowLevel` stb.)
- `github.com/christian-roggia/metin2-global-tools` — EIX/EPK kinyerő (formátum-referencia)

**Kapcsolódó doksik a projekt gyökerében (`~/Dokumentumok/madocsa2/`):**
- `OPTIMALIZALAS.md` — teljes Linux/Wine beállítás: DXVK, GameMode, MangoHud mérés, `metin2.cfg` optimalizálás, P-mag pinning, a pack formátum bontása (10. szekció)
- `Madocsa2/run-metin2.sh` — a wine+DXVK+GameMode indító script (nem mod, de a futtatáshoz kell)
- `AGENTS.md` — a kódbázis elemzése (architektúra, gotchák)

**Futás közbeni diagnosztika** (ha egy mod nem viselkedik): a kliens `syserr.txt`-je és `ErrorLog.txt`-je írja a Python tracebackeket; a név-mangling buktató (dupla aláhúzású attribútumok) a leggyakoribb hibaforrás a script-módosításoknál.
