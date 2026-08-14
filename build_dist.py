#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Madocsa2 QoL - terjesztesi csomag keszitese (szerveruzemeltetoi eszkoz).

A jatekosoknak NEM ezt kell futtatniuk - ok csak egy zipet toltenek le
es bemassolnak (lasd JATEKOSOK.md / a zipben levo TELEPITES.txt).

Hasznalat (Linux, Python 3 + liblzo2):
  python3 build_dist.py --client <a-kliens-mappaja> [--version 1.0]

A <a-kliens-mappaja> az, ahol a Madocsa2.exe van (benne a pack/root/ es
a pack/root.eix). A script:
  1. kimassolja a kliens TELJES pack/root/ tartalmat egy ideiglenes mappaba,
  2. rairja a repoban levo 4 modositott fajlt (pack/root/),
  3. ujracsomagolja a root.epk + root.eix-et (a kliens eredeti sorrendjet tartva),
  4. CRC-vel ellenorzi a kesz packot,
  5. a dist/ mappaba teszi: root.epk, root.eix, install_qol.bat, uninstall_qol.bat,
     TELEPITES.txt,
  6. mindezt becsomagolja: dist/Madocsa2-QoL-<verzio>.zip

FIGYELEM: a zip a kliens serverinfo.py-jat tartalmazza a root.epk-ben.
Ezek a jatekosok sajat adatai (ok ugyis ezt a klienst hasznaljak), de a zip
NE keruljon publikus repoba - csak a sajat jatekosaidnak add ki.
"""
import argparse
import os
import shutil
import struct
import sys
import tempfile
import zipfile

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
MOD_DIR = os.path.join(REPO_DIR, 'pack', 'root')
MOD_FILES = ['constinfo.py', 'game.py', 'interfacemodule.py', 'uitooltip.py']
EXTRA_FILES = ['install_qol.bat', 'uninstall_qol.bat', 'TELEPITES.txt']
MIN_FILES = 20  # ennel kevesebb fajl = biztos nem a teljes pack/root


def die(msg):
    print("HIBA: %s" % msg, file=sys.stderr)
    sys.exit(1)


def index_names(eix_bytes):
    four, enc, comp, real = struct.unpack('<4sIII', eix_bytes[:16])
    dec = pack_root.tea_decrypt(eix_bytes[16:16 + enc], pack_root.KEY_EIX)
    index = pack_root.lzo_decompress(dec[4:4 + comp], real)
    count = struct.unpack('<4sII', index[:12])[2]
    return [index[12 + i * 192 + 4:12 + i * 192 + 4 + 160].split(b'\0')[0].decode('ascii', 'replace')
            for i in range(count)]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--client', required=True,
                    help='a kliens mappaja (ahol a Madocsa2.exe van)')
    ap.add_argument('--version', default='1.0', help='verzio a zip nevehez (alap: 1.0)')
    ap.add_argument('--out', default=os.path.join(REPO_DIR, 'dist'),
                    help='kimeneti mappa (alap: dist/)')
    args = ap.parse_args()

    client = os.path.abspath(args.client)
    root_dir = os.path.join(client, 'pack', 'root')
    eix_path = os.path.join(client, 'pack', 'root.eix')
    if not os.path.isdir(root_dir):
        die("nincs %s - a --client a kliens mappaja kell, ahol a pack/root/ van" % root_dir)

    nfiles = len([f for f in os.listdir(root_dir)
                  if os.path.isfile(os.path.join(root_dir, f))])
    if nfiles < MIN_FILES:
        die("a %s csak %d fajlt tartalmaz, ez nem teljes kliens pack/root. "
            "Masold a repobol a 4 modositott fajlt a TELJES kliensed pack/root "
            "mappajaba, es arra mutass a --client-tel." % (root_dir, nfiles))
    missing = [f for f in MOD_FILES if not os.path.isfile(os.path.join(MOD_DIR, f))]
    if missing:
        die("hianyzik a repobol: %s" % ', '.join(missing))

    global pack_root
    try:
        import pack_root
    except OSError as ex:
        die("a packer nem indul (%s). Telepitsd a liblzo2-t: "
            "sudo pacman -S lzo (Arch) / sudo apt install liblzo2-2 (Debian/Ubuntu)" % ex)

    order = pack_root.get_order(eix_path, root_dir)

    tmp = tempfile.mkdtemp(prefix='qol_dist_')
    try:
        tmp_root = os.path.join(tmp, 'root')
        shutil.copytree(root_dir, tmp_root)
        for f in MOD_FILES:
            shutil.copy2(os.path.join(MOD_DIR, f), os.path.join(tmp_root, f))
        missing_in_root = [n for n in order if not os.path.isfile(os.path.join(tmp_root, n))]
        if missing_in_root:
            die("a kliens pack/root nem teljes a root.eix-hez kepest, hianyzik: %s"
                % ', '.join(missing_in_root[:5]))
        epk, eix = pack_root.build_pack(order, tmp_root, pack_root.KEY_EPK)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    epk_path = os.path.join(out, 'root.epk')
    eix_out = os.path.join(out, 'root.eix')
    open(epk_path, 'wb').write(epk)
    open(eix_out, 'wb').write(eix)

    # ellenorzes: a pack tartalma egyezzen a vart listaval, a CRC-k stimmeljenek
    built = index_names(open(eix_out, 'rb').read())
    if built != order:
        die("hiba: a kesz pack tartalma elter a varttol (%d vs %d fajl)"
            % (len(built), len(order)))
    print("--- CRC ellenorzes ---")
    pack_root.verify(order, None, epk_path, pack_root.KEY_EPK)
    print("--- minden rendben, %d fajl ---" % len(order))

    for f in EXTRA_FILES:
        src = os.path.join(REPO_DIR, f)
        if not os.path.isfile(src):
            die("hianyzik a repobol: %s" % f)
        shutil.copy2(src, os.path.join(out, f))

    zipname = os.path.join(out, 'Madocsa2-QoL-%s.zip' % args.version)
    with zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in ['root.epk', 'root.eix'] + EXTRA_FILES:
            zf.write(os.path.join(out, f), f)

    print()
    print("KESZ: %s" % zipname)
    print()
    print("Jatekosoknak: a zip tartalmat (5 fajl) masoljak a kliens mappajaba")
    print("(a Madocsa2.exe melle), majd kattintsanak duplan az install_qol.bat-ra.")
    print("A script biztositasi mentest keszit es mindent magatol csinal.")
    print("Visszavonas: uninstall_qol.bat.")
    print()
    print("FIGYELEM: ez a zip a kliens serverinfo.py-jat tartalmazza -")
    print("NE tedd publikus repoba, csak a sajat jatekosaidnak add ki!")


if __name__ == '__main__':
    main()
