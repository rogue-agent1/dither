#!/usr/bin/env python3
"""dither - Image dithering algorithms (Floyd-Steinberg, ordered, random)."""
import sys, random

def floyd_steinberg(image, levels=2):
    h, w = len(image), len(image[0])
    out = [row[:] for row in image]
    step = 255 / (levels - 1)
    for y in range(h):
        for x in range(w):
            old = out[y][x]
            new = round(old / step) * step
            new = max(0, min(255, new))
            err = old - new
            out[y][x] = new
            if x + 1 < w: out[y][x+1] += err * 7/16
            if y + 1 < h:
                if x > 0: out[y+1][x-1] += err * 3/16
                out[y+1][x] += err * 5/16
                if x + 1 < w: out[y+1][x+1] += err * 1/16
    return out

def ordered_dither(image, matrix_size=4):
    bayer = {
        2: [[0,2],[3,1]],
        4: [[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]],
    }
    m = bayer.get(matrix_size, bayer[4])
    n = len(m)
    threshold_scale = 255 / (n * n)
    h, w = len(image), len(image[0])
    out = [[0]*w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            threshold = (m[y % n][x % n] + 0.5) * threshold_scale
            out[y][x] = 255 if image[y][x] > threshold else 0
    return out

def random_dither(image, seed=None):
    if seed is not None:
        random.seed(seed)
    h, w = len(image), len(image[0])
    return [[255 if image[y][x] > random.randint(0, 255) else 0 for x in range(w)] for y in range(h)]

def test():
    # gradient image
    img = [[x * 25 for x in range(11)] for _ in range(5)]
    fs = floyd_steinberg(img)
    assert all(v in range(-50, 300) for row in fs for v in row)
    od = ordered_dither(img)
    assert all(v in (0, 255) for row in od for v in row)
    rd = random_dither(img, seed=42)
    assert all(v in (0, 255) for row in rd for v in row)
    # black stays black
    black = [[0]*5 for _ in range(5)]
    assert all(v == 0 for row in ordered_dither(black) for v in row)
    # white stays white
    white = [[255]*5 for _ in range(5)]
    assert all(v == 255 for row in ordered_dither(white) for v in row)
    print("OK: dither")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        print("Usage: dither.py test")
