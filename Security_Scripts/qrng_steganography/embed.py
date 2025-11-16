#!/usr/bin/env python3

"""Embed secrets inside qrng.png using modernized CLI controls."""

import argparse
import secrets

import numpy as np
from PIL import Image
import zlib


MAGIC = b"IDST"


def build_payload(secret: bytes) -> bytes:
    return MAGIC + len(secret).to_bytes(4, "big") + zlib.crc32(secret).to_bytes(4, "big") + secret


def embed(cover: str, secret_path: str, output: str, *, shuffle: bool = False, seed: int | None = None) -> None:
    img = Image.open(cover).convert("RGB")
    arr = np.array(img)
    secret = open(secret_path, "rb").read()
    payload = build_payload(secret)

    H, W, C = arr.shape
    capacity_bits = H * W * C
    required_bits = len(payload) * 8
    if required_bits > capacity_bits:
        raise SystemExit(f"Secret too large: need {required_bits//8} bytes <= {capacity_bits//8} bytes")

    flat = arr.reshape(-1)
    bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
    if shuffle:
        rng = np.random.default_rng(seed if seed is not None else secrets.randbits(64))
        indices = rng.choice(flat.size, size=bits.size, replace=False)
    else:
        indices = np.arange(bits.size)
    flat[indices] = (flat[indices] & 0xFE) | bits
    Image.fromarray(flat.reshape(arr.shape), "RGB").save(output, optimize=True)
    print(f"[+] Wrote {output} with {len(payload)} bytes embedded")


def main() -> None:
    parser = argparse.ArgumentParser(description="Embed secret data using LSB steganography")
    parser.add_argument("--cover", default="qrng.png", help="Cover image path")
    parser.add_argument("--secret", default="secret.txt", help="Secret file to embed")
    parser.add_argument("--output", default="stego.png", help="Output stego image path")
    parser.add_argument("--shuffle", action="store_true", help="Shuffle bit positions for added stealth")
    parser.add_argument("--seed", type=int, help="Optional RNG seed for reproducibility")
    args = parser.parse_args()

    embed(args.cover, args.secret, args.output, shuffle=args.shuffle, seed=args.seed)


if __name__ == "__main__":
    main()
