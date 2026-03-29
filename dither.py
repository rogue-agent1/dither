#!/usr/bin/env python3
"""Floyd-Steinberg and ordered dithering for image quantization."""
import sys

def floyd_steinberg(pixels, w, h, levels=2):
    img = [[float(pixels[y][x]) for x in range(w)] for y in range(h)]
    step = 255.0 / (levels - 1)
    out = [[0]*w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            old = img[y][x]
            new = round(old / step) * step
            out[y][x] = int(max(0, min(255, new)))
            err = old - new
            if x+1 < w: img[y][x+1] += err * 7/16
            if y+1 < h:
                if x-1 >= 0: img[y+1][x-1] += err * 3/16
                img[y+1][x] += err * 5/16
                if x+1 < w: img[y+1][x+1] += err * 1/16
    return out

BAYER4 = [[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]

def ordered_dither(pixels, w, h, levels=2):
    n = len(BAYER4); step = 255.0 / (levels - 1)
    out = [[0]*w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            threshold = (BAYER4[y%n][x%n] / 16.0 - 0.5) * step
            out[y][x] = int(max(0, min(255, round((pixels[y][x] + threshold) / step) * step)))
    return out

def main():
    if len(sys.argv) < 2: print("Usage: dither.py <demo|test>"); return
    if sys.argv[1] == "test":
        # Gradient image
        w, h = 16, 8
        pixels = [[int(x/w*255) for x in range(w)] for _ in range(h)]
        fs = floyd_steinberg(pixels, w, h, 2)
        assert all(fs[y][x] in (0, 255) for y in range(h) for x in range(w))
        # Should have mix of black and white
        vals = set(fs[0][x] for x in range(w))
        assert 0 in vals and 255 in vals
        od = ordered_dither(pixels, w, h, 2)
        assert all(od[y][x] in (0, 255) for y in range(h) for x in range(w))
        # Multi-level
        fs4 = floyd_steinberg(pixels, w, h, 4)
        vals4 = set(fs4[y][x] for y in range(h) for x in range(w))
        assert all(v in (0, 85, 170, 255) for v in vals4)
        print("All tests passed!")
    else:
        w = 20; pixels = [[int(x/w*255) for x in range(w)] for _ in range(5)]
        fs = floyd_steinberg(pixels, w, 5, 2)
        for row in fs: print("".join("#" if v > 128 else "." for v in row))

if __name__ == "__main__": main()
