"""G1-G5: operaciones geometricas con mapeo inverso (destino -> origen)."""
import math
from .image import Image, clamp


def hflip(img):
    """G1: out[y][x] = in[y][W-1-x]"""
    out = Image(img.w, img.h, img.c)
    for y in range(img.h):
        for x in range(img.w):
            for ch in range(img.c):
                out.set(x, y, ch, img.get(img.w - 1 - x, y, ch))
    return out


def vflip(img):
    """G2: out[y][x] = in[H-1-y][x]"""
    out = Image(img.w, img.h, img.c)
    for y in range(img.h):
        for x in range(img.w):
            for ch in range(img.c):
                out.set(x, y, ch, img.get(x, img.h - 1 - y, ch))
    return out


def dflip(img, mode="both"):
    """G3: volteo diagonal.
    both      : out[y][x] = in[H-1-y][W-1-x]  (hflip + vflip)  <- por defecto
    transpose : out[x][y] = in[y][x] (intercambia ancho y alto)
    ATENCION: comprobad con la figura del enunciado cual de las dos esperan."""
    if mode == "transpose":
        out = Image(img.h, img.w, img.c)
        for y in range(img.h):
            for x in range(img.w):
                for ch in range(img.c):
                    out.set(y, x, ch, img.get(x, y, ch))
        return out
    out = Image(img.w, img.h, img.c)
    for y in range(img.h):
        for x in range(img.w):
            for ch in range(img.c):
                out.set(x, y, ch, img.get(img.w - 1 - x, img.h - 1 - y, ch))
    return out


def shrink(img, factor=2.0, mode="average"):
    """G4: reduce el tamano dividiendo por 'factor' (>1).
    nearest: toma el pixel origen correspondiente.
    average: media del bloque origen (menos aliasing)."""
    if factor < 1:
        raise ValueError("factor debe ser >= 1 para shrink")
    nw, nh = max(1, int(img.w / factor)), max(1, int(img.h / factor))
    out = Image(nw, nh, img.c)
    for y in range(nh):
        y0 = int(y * factor)
        y1 = min(img.h, max(y0 + 1, int(math.ceil((y + 1) * factor))))
        for x in range(nw):
            x0 = int(x * factor)
            x1 = min(img.w, max(x0 + 1, int(math.ceil((x + 1) * factor))))
            for ch in range(img.c):
                if mode == "nearest":
                    v = img.get(min(x0, img.w - 1), min(y0, img.h - 1), ch)
                else:
                    s = 0
                    for yy in range(y0, y1):
                        for xx in range(x0, x1):
                            s += img.get(xx, yy, ch)
                    v = int(round(s / ((y1 - y0) * (x1 - x0))))
                out.set(x, y, ch, v)
    return out


def enlarge(img, factor=2.0, mode="bilinear"):
    """G5: aumenta el tamano multiplicando por 'factor' (>1), con mapeo inverso."""
    if factor < 1:
        raise ValueError("factor debe ser >= 1 para enlarge")
    nw, nh = int(img.w * factor), int(img.h * factor)
    out = Image(nw, nh, img.c)
    for y in range(nh):
        for x in range(nw):
            if mode == "nearest":
                sx, sy = min(int(x / factor), img.w - 1), min(int(y / factor), img.h - 1)
                for ch in range(img.c):
                    out.set(x, y, ch, img.get(sx, sy, ch))
            else:
                fx = clamp((x + 0.5) / factor - 0.5, 0, img.w - 1)
                fy = clamp((y + 0.5) / factor - 0.5, 0, img.h - 1)
                x0, y0 = int(fx), int(fy)
                x1, y1 = min(x0 + 1, img.w - 1), min(y0 + 1, img.h - 1)
                ax, ay = fx - x0, fy - y0
                for ch in range(img.c):
                    top = img.get(x0, y0, ch) * (1 - ax) + img.get(x1, y0, ch) * ax
                    bot = img.get(x0, y1, ch) * (1 - ax) + img.get(x1, y1, ch) * ax
                    out.set(x, y, ch, int(round(top * (1 - ay) + bot * ay)))
    return out