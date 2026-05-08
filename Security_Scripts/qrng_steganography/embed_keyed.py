#!/usr/bin/env python3

import getpass
import hashlib
import random

from PIL import Image


def bytes_to_bits(data: bytes) -> list[int]:
    bits: list[int] = []
    for b in data:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)
    return bits


def seed_from_passphrase(passphrase: str) -> int:
    return int.from_bytes(hashlib.sha256(passphrase.encode()).digest(), "big")


def main() -> None:
    img = Image.open("qrng.png").convert("RGB")
    pixels = list(img.getdata())

    with open("secret.txt", "rb") as f:
        secret = f.read()

    payload = len(secret).to_bytes(4, "big") + secret
    bits = bytes_to_bits(payload)

    flat_channels = [c for px in pixels for c in px]
    if len(bits) > len(flat_channels):
        raise SystemExit("Secret is too large for this image.")

    passphrase = getpass.getpass("Passphrase: ")
    rng = random.Random(seed_from_passphrase(passphrase))
    positions = list(range(len(flat_channels)))
    rng.shuffle(positions)

    for i, bit in enumerate(bits):
        p = positions[i]
        flat_channels[p] = (flat_channels[p] & 0xFE) | bit

    out_pixels = [tuple(flat_channels[i:i+3]) for i in range(0, len(flat_channels), 3)]
    out = Image.new("RGB", img.size)
    out.putdata(out_pixels)
    out.save("stego.png")
    print("Wrote stego.png (keyed)")


if __name__ == "__main__":
    main()
