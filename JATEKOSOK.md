# Madocsa2 QoL modok — útmutató játékosoknak

> Ez az oldal azoknak szól, akik **nem értenek a számítógéphez** a "bemásolok
> egy crack-et a játékfájlok közé" szintnél mélyebben. Pont annyit kell tudnod.

## Mi ez?

Pár apró kényelmi funkció a játékhoz (gombokkal ki-be kapcsolhatók):

| Gomb | Funkció |
|---|---|
| **F5** | karakter-nevek ki/be |
| **F7** | árnyék ki/be (több FPS sok mobnál) |
| **F8** | chat ablak ki/be |
| **F9** | kamera távolság (közel / távol) |
| **F10** | köd ciklus (több köd = kevesebb kirajzolt mob = több FPS) |
| **F11** | FPS kijelzés ki/be |
| **F12** | quest-gombok ki/be |

Ezen kívül: az item tooltipben megjelenik a tárgy vnum-a, a minimapon pedig
a koordinátád.

## Hol kapod meg?

**A kész zipet a szerverüzemeltetőtől kapod** (pl. Discord/weblink).
Ez a repo (ahol ezt az oldalt olvasod) csak a modok forrása — a játékosoknak
nem ebből kell telepíteniük, hanem a zipből.

## Telepítés (3 lépés)

1. **Töltsd le** a zipet (a `Madocsa2-QoL-....zip` fájlt).
2. **Csomagold ki**, és a zip **tartalmát** másold be a **játék mappájába** —
   oda, ahol a `Madocsa2.exe` van. (Ha kérdezi a Windows, hogy felülírja-e:
   engedd.)
3. **Kattints duplán** az `install_qol.bat` fájlra. A program magától
   biztonsági mentést készít, majd beállítja a modokat. Indíthatod a játékot.

Ennyi. Ha fekete ablak nyílik és "HIBA..."-t ír, az alábbi hibakeresés segít.

## Visszavonás (ha valami nem tetszik)

Kattints duplán az `uninstall_qol.bat` fájlra. Minden visszaáll az eredeti
állapotba.

## Hibakeresés (a leggyakoribb 3 eset)

| Amit látsz | Mit jelentsen | Megoldás |
|---|---|---|
| "HIBA: a Madocsa2.exe nem található" | a fájlok nem a játék mappájában vannak | másold a zip tartalmát a `Madocsa2.exe` **mellé** |
| "HIBA: a játék most fut" | a játék nyitva van | zárd be teljesen, majd futtasd újra a bat-ot |
| a játék nem indul a modokkal | valami nem fér össze ezzel a klienssel | futtasd az `uninstall_qol.bat`-ot, és jelezd az adminnak |

Bármi más: írj az adminnak, és írd le, mit ír a fekete ablak (vagy küldj róla
képet).
