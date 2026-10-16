"""N3: filtro alpha-trimmed (--alpha) y filtro media contraarmonica (--cmean).

Ventana cuadrada size x size (size impar). Bordes: se replica el pixel del borde.
Cada canal se filtra de forma independiente."""
from .image import Image, clamp


def _apply(img, size, fn):
    if size < 3 or size % 2 == 0:
        raise ValueError("size debe ser impar y >= 3")
    r = size // 2
    w, h = img.w, img.h
    planes = img.planes()
    out_planes = []
    for p in planes:
        res = [0] * (w * h)
        for y in range(h):
            for x in range(w):
                vals = []
                for j in range(y - r, y + r + 1):
                    jj = 0 if j < 0 else (h - 1 if j >= h else j)
                    base = jj * w
                    for i in range(x - r, x + r + 1):
                        ii = 0 if i < 0 else (w - 1 if i >= w else i)
                        vals.append(p[base + ii])
                res[y * w + x] = fn(vals)
        out_planes.append(res)
    return Image.from_planes(w, h, out_planes)


def alpha_trimmed(img, size=3, d=2):
    """N3a: descarta los d/2 valores menores y d/2 mayores y promedia los mn-d restantes.
    d=0 -> media aritmetica; d=mn-1 -> mediana. d debe ser par y 0 <= d < mn."""
    mn = size * size
    if d % 2 != 0 or d < 0 or d >= mn:
        raise ValueError("d debe ser par y cumplir 0 <= d < size*size (=%d)" % mn)
    t = d // 2

    def fn(vals):
        s = sorted(vals)
        kept = s[t:len(s) - t]
        return clamp(int(round(sum(kept) / len(kept))))

    return _apply(img, size, fn)


def contraharmonic(img, size=3, Q=1.5):
    """N3b: sum(f^(Q+1)) / sum(f^Q).
    Q>0 elimina pepper (oscuro); Q<0 elimina salt (claro); Q=0 media aritmetica; Q=-1 armonica.
    Los valores 0 se sustituyen por un epsilon para evitar division por cero con Q<0."""
    eps = 1e-3

    def fn(vals):
        num = den = 0.0
        for v in vals:
            f = v if v > 0 else eps
            p = f ** Q
            num += p * f
            den += p
        return clamp(int(round(num / den)))

    return _apply(img, size, fn)