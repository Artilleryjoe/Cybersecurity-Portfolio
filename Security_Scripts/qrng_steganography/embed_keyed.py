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


def derive_key(passphrase: bytes, cover_path: str, info: bytes) -> bytes:
    cover_bytes = open(cover_path, "rb").read()
    salt = hashlib.sha256(cover_bytes).digest()
    hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=salt, info=info, backend=default_backend())
    return hkdf.derive(passphrase)


def embed_keyed(cover: str, secret_path: str, out: str, *, info: bytes, passphrase: bytes) -> None:
    key = derive_key(passphrase, cover, info)
    img = Image.open(cover).convert("RGB")
    arr = np.array(img)
    H, W, C = arr.shape
    N = H * W * C
    secret = open(secret_path, "rb").read()
    payload = MAGIC + len(secret).to_bytes(4, "big") + zlib.crc32(secret).to_bytes(4, "big") + secret
    need_bits = len(payload) * 8
    if need_bits > N:
        raise SystemExit(f"Payload too large: need {need_bits//8} bytes <= {N//8}")
    rng = np.random.default_rng(np.frombuffer(key, dtype=np.uint64))
    perm = np.arange(N, dtype=np.int64)
    rng.shuffle(perm)
    bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8)).astype(np.uint8)
    flat = arr.reshape(-1)
    sel = perm[: bits.size]
    flat[sel] = (flat[sel] & 0xFE) | bits
    Image.fromarray(flat.reshape(arr.shape), "RGB").save(out, optimize=True)
    print(f"[+] wrote {out} (keyed path, {len(payload)} bytes embedded)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Keyed LSB embedding")
    parser.add_argument("--cover", default="qrng.png")
    parser.add_argument("--secret", default="secret.txt")
    parser.add_argument("--output", default="stego.png")
    parser.add_argument("--info", default="stego-path", help="HKDF info string")
    parser.add_argument("--passphrase", help="Optional passphrase (otherwise prompted)")
    args = parser.parse_args()

    passphrase = (args.passphrase or getpass.getpass("Passphrase: ")).encode()
    embed_keyed(args.cover, args.secret, args.output, info=args.info.encode(), passphrase=passphrase)


if __name__ == "__main__":
    main()
