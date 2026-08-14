#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Madocsa2 root.epk / root.eix packer (Python)
- Format verified against the live client packs + client source (CLZObject / tea.cpp / lzo.cpp).
- Entry type 2: TEA-encrypted (gLZOData2 key) + LZO1X compressed.
- EIX index: TEA-encrypted (gLZOData key) + LZO1X compressed, decompressed = EPKD v2 index.
Usage:
  python3 pack_root.py            # repack pack/root/* -> root.epk + root.eix
  python3 pack_root.py --verify   # list current pack contents
"""
import ctypes, struct, zlib, os, sys, argparse

LZO = ctypes.CDLL("liblzo2.so.2")
LZO1X_999_MEM_COMPRESS = 1024 * 1024
_LZOP = ctypes.POINTER(ctypes.c_size_t)
LZO.lzo1x_999_compress.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, _LZOP, ctypes.c_char_p]
LZO.lzo1x_999_compress.restype = ctypes.c_int
LZO.lzo1x_decompress_safe.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, _LZOP, ctypes.c_char_p]
LZO.lzo1x_decompress_safe.restype = ctypes.c_int

KEY_EIX = bytes([0xB9, 0x9E, 0xB0, 0x02, 0x6F, 0x69, 0x81, 0x05,
                 0x63, 0x98, 0x9B, 0x28, 0x79, 0x18, 0x1A, 0x00])
KEY_EPK = bytes([0x22, 0xB8, 0xB4, 0x04, 0x64, 0xB2, 0x6E, 0x1F,
                 0xAE, 0xEA, 0x18, 0x00, 0xA6, 0xF6, 0xFB, 0x1C])

DELTA = 0x9E3779B9
MASK = 0xFFFFFFFF

# ---------- TEA ----------
def _tea_rounds(y, z, k, decrypt):
    s = (DELTA * 32) & MASK if decrypt else 0
    for _ in range(32):
        if decrypt:
            z = (z - ((((y << 4) ^ (y >> 5)) + y) ^ (s + k[(s >> 11) & 3]))) & MASK
            s = (s - DELTA) & MASK
            y = (y - ((((z << 4) ^ (z >> 5)) + z) ^ (s + k[s & 3]))) & MASK
        else:
            y = (y + ((((z << 4) ^ (z >> 5)) + z) ^ (s + k[s & 3]))) & MASK
            s = (s + DELTA) & MASK
            z = (z + ((((y << 4) ^ (y >> 5)) + y) ^ (s + k[(s >> 11) & 3]))) & MASK
    return y, z

def tea_encrypt(data, key):
    k = struct.unpack('<4I', key)
    out = b''
    for i in range(0, len(data) - 7, 8):
        y, z = struct.unpack('<II', data[i:i+8])
        y2, z2 = _tea_rounds(y, z, k, False)
        out += struct.pack('<II', y2, z2)
    return out

def tea_decrypt(data, key):
    k = struct.unpack('<4I', key)
    out = b''
    for i in range(0, len(data) - 7, 8):
        y, z = struct.unpack('<II', data[i:i+8])
        y2, z2 = _tea_rounds(y, z, k, True)
        out += struct.pack('<II', y2, z2)
    return out

# ---------- LZO ----------
def lzo_compress(data):
    src = ctypes.create_string_buffer(data)
    out = ctypes.create_string_buffer(len(data) + len(data)//16 + 64 + 3)
    outlen = ctypes.c_size_t(len(out))
    work = ctypes.create_string_buffer(LZO1X_999_MEM_COMPRESS)
    r = LZO.lzo1x_999_compress(src, len(data), out, ctypes.byref(outlen), work)
    if r != 0:
        raise RuntimeError("lzo1x_999_compress failed: %d" % r)
    return out.raw[:outlen.value]

def lzo_decompress(data, outsize):
    dst = ctypes.create_string_buffer(outsize)
    out = ctypes.c_size_t(outsize)
    r = LZO.lzo1x_decompress_safe(data, len(data), dst, ctypes.byref(out), None)
    if r != 0:
        raise RuntimeError("lzo1x_decompress failed: %d" % r)
    return dst.raw[:out.value]

# ---------- container (CLZObject) ----------
def make_container(real, key):
    """real -> (bytes, encryptSize, compSize) stored block per CLZObject"""
    stream = lzo_compress(real)
    comp = len(stream)
    encrypt_size = (comp + 19 + 7) & ~7          # tea_encrypt(comp+19) padded to 8
    plain = b'MCOZ' + stream
    plain = plain + b'\x00' * (encrypt_size - len(plain)) if encrypt_size > len(plain) else plain
    cipher = tea_encrypt(plain[:encrypt_size], key)
    header = struct.pack('<4sIII', b'MCOZ', encrypt_size, comp, len(real))
    # GetSize() = 16 + 4 + encryptSize  (4 = the on-disk fourCC slot)
    stored = header + cipher + b'\x00' * 4
    return stored, 16 + 4 + encrypt_size

def read_container(block, key):
    four, enc, comp, real = struct.unpack('<4sIII', block[:16])
    dec = tea_decrypt(block[16:16+enc], key)
    assert dec[:4] == b'MCOZ'
    return lzo_decompress(dec[4:4+comp], real)

# ---------- pack ----------
ENTRY = 192
NAME = 160

def build_pack(files, root_dir, key):
    """files: list of names (order preserved). Returns (epk_bytes, eix_bytes)."""
    entries = []
    epk = b''
    offset = 0
    for i, name in enumerate(files):
        real = open(os.path.join(root_dir, name), 'rb').read()
        stored, src_size = make_container(real, key)
        aligned = (src_size + 255) & ~255
        epk += stored + b'\x00' * (aligned - src_size)
        crc_block = zlib.crc32(stored[:src_size]) & 0xFFFFFFFF
        crc_real = zlib.crc32(real) & 0xFFFFFFFF
        nb = name.encode('ascii')
        e = struct.pack('<I', i) + nb.ljust(NAME, b'\x00')
        # dw2 = crc32(fájlnév) — a kliens ezt ellenőrzi
        e += struct.pack('<IIIIII', 0, zlib.crc32(nb) & 0xFFFFFFFF, aligned, src_size, crc_block, offset)
        e += bytes([2, 0, 0, 0])
        entries.append(e)
        offset += aligned
    index = struct.pack('<4sII', b'EPKD', 2, len(entries)) + b''.join(entries)
    stored, src_size = make_container(index, KEY_EIX)
    return epk, stored[:src_size]

def get_order(eix_path, root_dir):
    """Fájl-sorrend: a meglevő eix-ből (ha olvasható), különben abc + új fájlok."""
    order = []
    if os.path.exists(eix_path):
        try:
            raw = open(eix_path, 'rb').read()
            four, enc, comp, real = struct.unpack('<4sIII', raw[:16])
            dec = tea_decrypt(raw[16:16+enc], KEY_EIX)
            index = lzo_decompress(dec[4:4+comp], real)
            count = struct.unpack('<4sII', index[:12])[2]
            order = [index[12+i*192+4:12+i*192+4+NAME].split(b'\0')[0].decode('ascii', 'replace') for i in range(count)]
        except Exception as ex:
            print("figyelem: eredeti eix olvasas sikertelen (%s), abc sorrend" % ex)
    disk = sorted(os.listdir(root_dir))
    for n in disk:
        if os.path.isfile(os.path.join(root_dir, n)) and n not in order:
            order.append(n)
    return order

def verify(files, root_dir, epk_path, key):
    idx_raw = open(epk_path.replace('.epk', '.eix'), 'rb').read()
    four, enc, comp, real = struct.unpack('<4sIII', idx_raw[:16])
    dec = tea_decrypt(idx_raw[16:16+enc], KEY_EIX)
    index = lzo_decompress(dec[4:4+comp], real)
    magic, ver, count = struct.unpack('<4sII', index[:12])
    print("eix: %s ver=%d count=%d" % (magic, ver, count))
    epk = open(epk_path, 'rb').read()
    for i in range(count):
        e = index[12+i*192:12+(i+1)*192]
        name = e[4:4+NAME].split(b'\0')[0].decode('ascii', 'replace')
        dw1, dw2, dw3, src, crc, off = struct.unpack('<IIIIII', e[164:188])
        ptype = e[188]
        print("%3d %-24s ptype=%d src=%d off=%d crc_ok=%s" % (
            i, name, ptype, src, off,
            (zlib.crc32(epk[off:off+src]) & 0xFFFFFFFF) == crc))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--verify', action='store_true')
    ap.add_argument('--outdir', default=os.path.dirname(os.path.abspath(__file__)))
    args = ap.parse_args()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.join(script_dir, 'root')
    out = args.outdir

    # sorrend az eredeti eix-ből (ha van), különben abc
    eix_path = os.path.join(out, 'root.eix')
    order = get_order(eix_path, root_dir)

    if args.verify:
        verify(order, root_dir, os.path.join(out, 'root.epk'), KEY_EPK)
        return

    epk, eix = build_pack(order, root_dir, KEY_EPK)
    open(os.path.join(out, 'root.epk'), 'wb').write(epk)
    open(os.path.join(out, 'root.eix'), 'wb').write(eix)
    print("root.epk: %d bájt | root.eix: %d bájt | %d fájl" % (len(epk), len(eix), len(order)))

if __name__ == '__main__':
    main()
