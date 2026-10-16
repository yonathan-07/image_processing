"""Generadores de ruido para los experimentos (no forman parte de la tarea evaluada)."""
import random
from .image import Image, clamp


def gaussian(img, sigma=20.0, seed=None):
    rnd = random.Random(seed)
    out = Image(img.w, img.h, img.c)
    for i, v in enumerate(img.data):
        out.data[i] = clamp(int(round(v + rnd.gauss(0, sigma))))
    return out


def uniform(img, amplitude=40.0, seed=None):
    rnd = random.Random(seed)
    out = Image(img.w, img.h, img.c)
    for i, v in enumerate(img.data):
        out.data[i] = clamp(int(round(v + rnd.uniform(-amplitude, amplitude))))
    return out


def salt_pepper(img, salt=0.05, pepper=0.05, seed=None):
    """Impulsivo: con prob. 'salt' el pixel pasa a 255, con prob. 'pepper' a 0 (todos los canales)."""
    rnd = random.Random(seed)
    out = img.copy()
    for y in range(img.h):
        for x in range(img.w):
            r = rnd.random()
            if r < salt:
                val = 255
            elif r < salt + pepper:
                val = 0
            else:
                continue
            for ch in range(img.c):
                out.set(x, y, ch, val)
    return out