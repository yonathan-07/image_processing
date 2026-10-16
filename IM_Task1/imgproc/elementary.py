"""B1-B3: operaciones elementales (pixel a pixel, por canal)."""
from .image import Image, clamp


def brightness(img, value=0):
    """B1: suma 'value' (negativo = oscurecer) con saturacion a [0,255]."""
    out = Image(img.w, img.h, img.c)
    for i, v in enumerate(img.data):
        out.data[i] = clamp(v + value)
    return out


def contrast(img, value=1.0, mode="linear"):
    """B2: contraste.
    linear: f = a*(v-128)+128      (a>1 sube, 0<a<1 baja)
    exp:    f = 255*(v/255)^gamma  (gamma<1 aclara, gamma>1 oscurece)
    Se precalcula una LUT de 256 entradas y se aplica a cada pixel."""
    if mode == "linear":
        lut = [clamp(int(round(value * (v - 128) + 128))) for v in range(256)]
    elif mode == "exp":
        lut = [clamp(int(round(255 * (v / 255.0) ** value))) for v in range(256)]
    else:
        raise ValueError("mode debe ser 'linear' o 'exp'")
    out = Image(img.w, img.h, img.c)
    for i, v in enumerate(img.data):
        out.data[i] = lut[v]
    return out


def negative(img):
    """B3: 255 - v en cada componente."""
    out = Image(img.w, img.h, img.c)
    for i, v in enumerate(img.data):
        out.data[i] = 255 - v
    return out