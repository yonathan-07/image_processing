"""Estructura de datos interna + carga/guardado.

Pillow se usa UNICAMENTE para leer/escribir ficheros. Nada mas se delega en librerias:
la imagen se convierte enseguida a nuestra clase Image (lista plana de enteros 0..255).
"""
from PIL import Image as PILImage


class Image:
    """Imagen en memoria: data[(y * w + x) * c + ch], con c = 1 (grises) o 3 (RGB)."""

    def __init__(self, w, h, c, data=None):
        self.w, self.h, self.c = w, h, c
        self.data = data if data is not None else [0] * (w * h * c)

    def get(self, x, y, ch=0):
        return self.data[(y * self.w + x) * self.c + ch]

    def set(self, x, y, ch, value):
        self.data[(y * self.w + x) * self.c + ch] = value

    def copy(self):
        return Image(self.w, self.h, self.c, list(self.data))

    def planes(self):
        """Lista de c planos (uno por canal), cada uno una lista de w*h valores."""
        return [self.data[ch::self.c] for ch in range(self.c)]

    @staticmethod
    def from_planes(w, h, planes):
        c = len(planes)
        data = [0] * (w * h * c)
        for ch, p in enumerate(planes):
            data[ch::c] = p
        return Image(w, h, c, data)


def clamp(v, lo=0, hi=255):
    return lo if v < lo else hi if v > hi else v


def load_image(path):
    """Carga una imagen. Grises -> 1 canal; cualquier otra (incl. paleta) -> RGB 3 canales."""
    im = PILImage.open(path)
    if im.mode in ("L", "1"):
        im = im.convert("L")
        c = 1
    else:
        im = im.convert("RGB")
        c = 3
    return Image(im.width, im.height, c, list(im.tobytes()))


def save_image(img, path):
    mode = "L" if img.c == 1 else "RGB"
    PILImage.frombytes(mode, (img.w, img.h), bytes(img.data)).save(path)