# Madocsa2 kliens — QoL modok

Kliensoldali (Python 2) minőségi javítások a Metin2 klienshez, saját repack
eszközzel. A modok a `pack/root/` script réteget módosítják, és a `root.epk`
újracsomagolásával élnek.

---

## Játékosoknak — letöltés és bemásolás (ez az egész)

> **Nem kell semmihez értened.** A kész csomagot a szerverüzemeltetőtől
> kapod, nem ebből a repóból. A repo csak a modok forrása.

A `Madocsa2-QoL-<verzió>.zip` telepítése 3 lépés (részletesen: `JATEKOSOK.md`,
a zipben pedig `TELEPITES.txt`):

1. **Letöltés** — a zip, amit az admin oszt ki.
2. **Bemásolás** — a zip tartalmát másold a játék mappájába (a `Madocsa2.exe` mellé).
3. **Kattintás** — futtasd az `install_qol.bat`-ot: magától biztonsági mentést
   készít és beállít mindent. Visszavonás: `uninstall_qol.bat`.

Az aktív modok (lásd lentebb a táblázatot) a játékban **F5–F12** gombokkal
kapcsolhatók.

---

## Szerverüzemeltetőnek — a játékosok zip előállítása (egyszer)

A kész zip a kliens `serverinfo.py`-ját tartalmazza, ezért **nem lehet a
repóban** — a saját gépeden kell előállítanod, és a játékosaidnak kiosztani
(Discord/weblink). Egy parancs:

```bash
# függőség: liblzo2 (a packer LZO1X tömörítést használ)
sudo pacman -S lzo   # Arch/EndeavourOS
# vagy: sudo apt install liblzo2-2  (Debian/Ubuntu)

# a kliens mappádra mutatva (ahol a Madocsa2.exe van):
python3 build_dist.py --client <a-kliens-mappaja>
```

A script a kliensed **teljes** `pack/root/`-jából dolgozik: ráírja a repó 4
módosított fájlját, újracsomagolja a `root.epk`/`root.eix`-et, CRC-vel
ellenőrzi, majd becsomagolja mindent a `dist/Madocsa2-QoL-<verzió>.zip`-be
(a telepítő/eltávolító `.bat`-okkal és a `TELEPITES.txt`-tel együtt).

> **Fontos**: a `--client` a **teljes kliens mappád** legyen (ahol a
> `pack/root/` minden fájlja megvan) — a repo `pack/root/`-ja csak a 4
> módosított fájlt tartalmazza, azzal önmagában nem lehet packot építeni.

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

## Adminoknak: a modok fájljai és a manuális repack

### Módosított fájlok (`pack/root/`)

| Fájl | Módosítás |
|---|---|
| `game.py` | F5/F7/F8/F9/F10/F11/F12 keybindek + a hozzájuk tartozó metódusok |
| `interfacemodule.py` | F12 quest-gomb kapcsoló (`ToggleQuestButtons`) |
| `uitooltip.py` | item vnum a tooltipben (`__SetNormalItemTitle`) |
| `constinfo.py` | `MINIMAP_POSITIONINFO_ENABLE = 1` |

A pontos eltérések az eredeti fájlokhoz képest a `patch/*.diff` fájlokban vannak.

### Manuális repack (Linux, Python 3)

A `build_dist.py` használata helyett kézzel is lehet packolni (pl. ha saját
módosításaid is vannak a `pack/root/`-ban):

```bash
# a repó pack/root/ 4 fájlját másold a saját kliensed pack/root/ mappájába
# (a SAJÁT serverinfo.py-dat NEM írod felül!)
cd <a-kliens-mappaja>/pack
python3 <repó>/pack_root.py      # generálja a root.epk + root.eix-et itt
python3 <repó>/pack_root.py --verify  # ellenőrzés (CRC-k listázása)
```

### A pack formátum (ha valaki mélyebben akarja)

- `.eix` = index: `MCOZ` konténer (TEA titkosítás `gLZOData` kulccsal + LZO1X tömörítés), kicsomagolva: `EPKD` v2 fejléc + 192 bájt/bejegyzés.
- `.epk` = adat: minden fájl = `THeader(MCOZ, encryptSize, compSize, realSize)` + TEA titkosított (`gLZOData2` kulcs) LZO stream, `packedType=2`.
- Bejegyzés mezők: `index, filename[160], dw1, dw2, dw3, srcSize, crc, offset, packedType` — **`dw2 = crc32(fájlnév)`**, amit a kliens ellenőriz (ennél a hibánál bukott el minden rossz packer).
- 256 bájtra igazított offsetek, `dw3 = align256(srcSize)`.

---

## Biztonság / szabályok

- **NE kerüljön a repóba**: a `credentials` fájl (fiókjelszavak), a `serverinfo.py` élő IP/port adatai, és a `dist/` kimenet (a zip tartalmazza a `serverinfo.py`-t a `root.epk`-ben). A játékosok a saját kliensük `serverinfo.py`-jét használják — azt NEM szabad felülírni a modokkal.
- A `root.epk` tartalma ehhez a szerverhez/klienshez kötött; más buildnél a `patch/` diff-eket kell újraalkalmazni.
- A Metin2 kliens a Ymir/Gameforge szellemi tulajdona — a modok csak script-szintű személyre szabások, a terjesztés a saját szervered játékosai körében történjen.

---

## Visszaállítás

- Játékos: futtasd az `uninstall_qol.bat`-ot (vagy kézzel: tedd vissza a mentett `root.epk`/`root.eix`-et a `pack/` mappába).
- Admin: `pack/root/` fájljait cseréld vissza az eredetiekre (vagy `patch/` diff-ek reverse alkalmazása), majd `python3 pack_root.py`.

---

## Kapcsolódó dokumentáció

- `JATEKOSOK.md` — a játékosoknak szóló útmutató (a zip nélkül is olvasható).
- `LINUX_TELEPITES.md` — teljes Linux/Wine beállítás: DXVK, GameMode, MangoHud mérés, `metin2.cfg` optimalizálás, P-mag pinning, a pack formátum bontása (10. szekció).
- `run-metin2.sh` — wine+DXVK+GameMode indító script (nem mod, de a futtatáshoz kell).
- `AGENTS.md` — a kódbázis elemzése (architektúra, gotchák).

**Futás közbeni diagnosztika** (ha egy mod nem viselkedik): a kliens
`syserr.txt`-je és `ErrorLog.txt`-je írja a Python tracebackeket; a
név-mangling buktató (dupla aláhúzású attribútumok) a leggyakoribb hibaforrás
a script-módosításoknál.

**A pack formátum megfejtéséhez használt források:**
- `git.old-metin2.com/metin2/client` — a 2014-es kliens forrása (EterPack, LZO/TEA, HybridCrypt)
- `git.old-metin2.com/metin2/server` — a szerver forrása (shop DB-séma, gamefiles)
- `github.com/NakiuS/Metin2Client` — klasszikus kliens-forrás (`EterPack.cpp`, `PythonBackground.cpp`, `CPythonSystem::SetShadowLevel` stb.)
- `github.com/christian-roggia/metin2-global-tools` — EIX/EPK kinyerő (formátum-referencia)
