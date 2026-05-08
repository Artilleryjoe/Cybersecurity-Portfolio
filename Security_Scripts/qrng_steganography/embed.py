#!/usr/bin/env python3

from PIL import Image


def bytes_to_bits(data: bytes) -> list[int]:
    bits: list[int] = []
    for b in data:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)
    return bits


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

    for i, bit in enumerate(bits):
        flat_channels[i] = (flat_channels[i] & 0xFE) | bit

    out_pixels = [tuple(flat_channels[i:i+3]) for i in range(0, len(flat_channels), 3)]
    out = Image.new("RGB", img.size)
    out.putdata(out_pixels)
    out.save("stego.png")
    print("Wrote stego.png")


if __name__ == "__main__":
    main()
