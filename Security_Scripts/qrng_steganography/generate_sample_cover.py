#!/usr/bin/env python3

import random
from PIL import Image


def main() -> None:
    w, h = 512, 512
    img = Image.new("RGB", (w, h))
    pixels = img.load()

    for y in range(h):
        for x in range(w):
            pixels[x, y] = (
                random.randrange(256),
                random.randrange(256),
                random.randrange(256),
            )

    img.save("qrng.png")
    print("Wrote qrng.png (synthetic pseudo-random test carrier)")


if __name__ == "__main__":
    main()
