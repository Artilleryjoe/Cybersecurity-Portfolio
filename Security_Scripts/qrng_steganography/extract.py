#!/usr/bin/env python3

from PIL import Image


def bits_to_bytes(bits: list[int]) -> bytes:
    out = bytearray()
    for i in range(0, len(bits), 8):
        b = 0
        for bit in bits[i:i+8]:
            b = (b << 1) | bit
        out.append(b)
    return bytes(out)


def main() -> None:
    img = Image.open("stego.png").convert("RGB")
    flat_channels = [c for px in img.getdata() for c in px]
    lsb = [c & 1 for c in flat_channels]

    length = int.from_bytes(bits_to_bytes(lsb[:32]), "big")
    total_bits = 32 + length * 8
    secret = bits_to_bytes(lsb[32:total_bits])

    with open("recovered.txt", "wb") as f:
        f.write(secret)
    print("Wrote recovered.txt")


if __name__ == "__main__":
    main()
