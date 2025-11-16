#!/usr/bin/env python3

import argparse
import getpass
import hashlib

import numpy as np
from PIL import Image
import zlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

MAGIC = b"IDKT"


def derive_key(passphrase: bytes, stego_path: str, info: bytes) -> bytes:
    salt = hashlib.sha256(open(stego_path, "rb").read()).digest()
    hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=salt, info=info, backend=default_backend())
    return hkdf.derive(passphrase)


def extract_keyed(stego: str, out: str, *, info: bytes, passphrase: bytes) -> None:
    key = derive_key(passphrase, stego, info)
    img = Image.open(stego).convert("RGB")
    arr = np.array(img)
    H, W, C = arr.shape
    N = H * W * C
    rng = np.random.default_rng(np.frombuffer(key, dtype=np.uint64))
    perm = np.arange(N, dtype=np.int64)
    rng.shuffle(perm)
    flat = arr.reshape(-1)

    def read_bytes(nbytes: int) -> bytes:
        idx = read_bytes.idx
        need = nbytes * 8
        pos = perm[idx : idx + need]
        read_bytes.idx += need
        bits = (flat[pos] & 1).astype(np.uint8)
        return np.packbits(bits).tobytes()

    read_bytes.idx = 0  # type: ignore[attr-defined]

    header = read_bytes(12)
    if header[:4] != MAGIC:
        raise SystemExit("[-] wrong key or payload missing")
    length = int.from_bytes(header[4:8], "big")
    crc_ref = int.from_bytes(header[8:12], "big")
    secret = read_bytes(length)
    crc = zlib.crc32(secret)
    with open(out, "wb") as fh:
        fh.write(secret)
    print(f"[+] recovered {len(secret)} bytes (CRC {'OK' if crc==crc_ref else 'BAD'}) -> {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract keyed LSB payloads")
    parser.add_argument("--stego", default="stego.png")
    parser.add_argument("--output", default="recovered.txt")
    parser.add_argument("--info", default="stego-path")
    parser.add_argument("--passphrase", help="Optional passphrase (otherwise prompted)")
    args = parser.parse_args()

    passphrase = (args.passphrase or getpass.getpass("Passphrase: ")).encode()
    extract_keyed(args.stego, args.output, info=args.info.encode(), passphrase=passphrase)


if __name__ == "__main__":
    main()
