"""E1-E5: medidas de similitud. f = original SIN ruido, g = imagen comparada.
En imagenes de color se agregan todas las muestras (pixeles x canales)."""
import math


def _check(a, b):
    if (a.w, a.h, a.c) != (b.w, b.h, b.c):
        raise ValueError("las imagenes deben tener el mismo tamano y numero de canales")


def _sq_err(f, g):
    _check(f, g)
    return sum((a - b) ** 2 for a, b in zip(f.data, g.data))


def mse(f, g):
    """E1"""
    return _sq_err(f, g) / len(f.data)


def pmse(f, g):
    """E2: MSE / max(f)^2"""
    m = max(f.data)
    return mse(f, g) / (m * m) if m else float("inf")


def snr(f, g):
    """E3 [dB]: 10 log10( sum f^2 / sum (f-g)^2 )"""
    err = _sq_err(f, g)
    if err == 0:
        return float("inf")
    return 10 * math.log10(sum(v * v for v in f.data) / err)


def psnr(f, g):
    """E4 [dB]: 10 log10( sum max(f)^2 / sum (f-g)^2 )"""
    err = _sq_err(f, g)
    if err == 0:
        return float("inf")
    m = max(f.data)
    return 10 * math.log10(len(f.data) * m * m / err)


def md(f, g):
    """E5: max |f-g|"""
    _check(f, g)
    return max(abs(a - b) for a, b in zip(f.data, g.data))