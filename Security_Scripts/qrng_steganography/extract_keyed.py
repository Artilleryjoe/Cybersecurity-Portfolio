#!/usr/bin/env python3

import getpass
import hashlib
import random

from PIL import Image


def bits_to_bytes(bits: list[int]) -> bytes:
    out = bytearray()
    for i in range(0, len(bits), 8):
        b = 0
        for bit in bits[i:i+8]:
            b = (b << 1) | bit
        out.append(b)
    return bytes(out)


def seed_from_passphrase(passphrase: str) -> int:
    return int.from_bytes(hashlib.sha256(passphrase.encode()).digest(), "big")


def main() -> None:
    img = Image.open("stego.png").convert("RGB")
    flat_channels = [c for px in img.getdata() for c in px]

    passphrase = getpass.getpass("Passphrase: ")
    rng = random.Random(seed_from_passphrase(passphrase))
    positions = list(range(len(flat_channels)))
    rng.shuffle(positions)

    lsb = [flat_channels[p] & 1 for p in positions]
    length = int.from_bytes(bits_to_bytes(lsb[:32]), "big")
    total_bits = 32 + length * 8
    secret = bits_to_bytes(lsb[32:total_bits])

    with open("recovered.txt", "wb") as f:
        f.write(secret)
    print("Wrote recovered.txt (keyed)")


if __name__ == "__main__":
    main()
