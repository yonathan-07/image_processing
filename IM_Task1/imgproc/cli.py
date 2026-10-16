"""Parser de linea de comandos propio.  Formato:  main.py --comando [-argumento=valor ...]

Para anadir un comando nuevo en las proximas tareas basta con registrarlo en COMMANDS."""
import sys
import time

from . import elementary, geometric, noise_filters, metrics, noise_gen
from .image import load_image, save_image


class Arg:
    def __init__(self, name, desc, type=str, default=None, required=False):
        self.name, self.desc, self.type, self.default, self.required = name, desc, type, default, required


class Command:
    def __init__(self, name, desc, kind, fn, args):
        self.name, self.desc, self.kind, self.fn, self.args = name, desc, kind, fn, args


IN_OUT = [Arg("input", "ruta de la imagen de entrada", required=True),
          Arg("output", "ruta de la imagen de salida", required=True)]
PAIR = [Arg("original", "imagen original SIN ruido", required=True),
        Arg("processed", "imagen a comparar (con ruido o filtrada)", required=True)]


def _img(name, desc, fn, extra=()):
    return Command(name, desc, "image", fn, IN_OUT + list(extra))


def _met(name, desc, fn):
    return Command(name, desc, "metric", fn, PAIR)


COMMANDS = {c.name: c for c in [
    # --- B: elementales
    _img("brightness", "B1 Modifica el brillo sumando una constante (con saturacion 0..255).",
         elementary.brightness, [Arg("value", "constante a sumar; negativa oscurece", int, 0)]),
    _img("contrast", "B2 Modifica el contraste.", elementary.contrast,
         [Arg("value", "linear: factor a (>1 sube); exp: gamma", float, 1.0),
          Arg("mode", "linear | exp", str, "linear")]),
    _img("negative", "B3 Negativo (255 - v en cada componente).", elementary.negative),
    # --- G: geometricas
    _img("hflip", "G1 Volteo horizontal.", geometric.hflip),
    _img("vflip", "G2 Volteo vertical.", geometric.vflip),
    _img("dflip", "G3 Volteo diagonal.", geometric.dflip,
         [Arg("mode", "both (hflip+vflip) | transpose", str, "both")]),
    _img("shrink", "G4 Reduce la imagen dividiendo sus dimensiones por 'factor'.", geometric.shrink,
         [Arg("factor", "factor >= 1", float, 2.0), Arg("mode", "average | nearest", str, "average")]),
    _img("enlarge", "G5 Amplia la imagen multiplicando sus dimensiones por 'factor'.", geometric.enlarge,
         [Arg("factor", "factor >= 1", float, 2.0), Arg("mode", "bilinear | nearest", str, "bilinear")]),
    # --- N3: filtros de ruido
    _img("alpha", "N3 Filtro de media alpha-recortada.", noise_filters.alpha_trimmed,
         [Arg("size", "lado de la ventana (impar >= 3)", int, 3),
          Arg("d", "valores a descartar (par, 0 <= d < size*size)", int, 2)]),
    _img("cmean", "N3 Filtro de media contraarmonica.", noise_filters.contraharmonic,
         [Arg("size", "lado de la ventana (impar >= 3)", int, 3),
          Arg("Q", "orden: Q>0 quita pepper, Q<0 quita salt", float, 1.5)]),
    # --- E: medidas
    _met("mse", "E1 Error cuadratico medio.", metrics.mse),
    _met("pmse", "E2 Error cuadratico medio de pico.", metrics.pmse),
    _met("snr", "E3 Relacion senal/ruido [dB].", metrics.snr),
    _met("psnr", "E4 Relacion senal/ruido de pico [dB].", metrics.psnr),
    _met("md", "E5 Diferencia maxima.", metrics.md),
    # --- auxiliares para experimentos
    _img("noise-gauss", "(aux) Anade ruido gaussiano.", noise_gen.gaussian,
         [Arg("sigma", "desviacion tipica", float, 20.0), Arg("seed", "semilla aleatoria", int, None)]),
    _img("noise-uniform", "(aux) Anade ruido uniforme.", noise_gen.uniform,
         [Arg("amplitude", "amplitud +-", float, 40.0), Arg("seed", "semilla aleatoria", int, None)]),
    _img("noise-sp", "(aux) Anade ruido sal y pimienta.", noise_gen.salt_pepper,
         [Arg("salt", "probabilidad de sal", float, 0.05), Arg("pepper", "probabilidad de pimienta", float, 0.05),
          Arg("seed", "semilla aleatoria", int, None)]),
]}


def print_help():
    print("Uso: python main.py --comando [-argumento=valor ...]\n")
    print("Comandos disponibles:\n")
    print("  --help\n      Muestra esta ayuda.\n")
    for c in COMMANDS.values():
        print("  --%s\n      %s" % (c.name, c.desc))
        for a in c.args:
            extra = "obligatorio" if a.required else "por defecto: %s" % a.default
            print("      -%s=<%s>  %s (%s)" % (a.name, a.type.__name__, a.desc, extra))
        print()


def parse(tokens):
    if not tokens or not tokens[0].startswith("--"):
        raise ValueError("el primer argumento debe ser un comando (--help para ver la lista)")
    name = tokens[0][2:]
    params = {}
    for t in tokens[1:]:
        if not t.startswith("-") or "=" not in t:
            raise ValueError("argumento mal formado: %r (formato -clave=valor)" % t)
        k, v = t.lstrip("-").split("=", 1)
        params[k] = v
    return name, params


def run(argv):
    try:
        name, raw = parse(argv)
        if name == "help":
            print_help()
            return 0
        if name not in COMMANDS:
            raise ValueError("comando desconocido: --%s" % name)
        cmd = COMMANDS[name]
        known = {a.name for a in cmd.args}
        for k in raw:
            if k not in known:
                raise ValueError("argumento desconocido para --%s: -%s" % (name, k))
        vals = {}
        for a in cmd.args:
            if a.name in raw:
                try:
                    vals[a.name] = a.type(raw[a.name])
                except ValueError:
                    raise ValueError("-%s debe ser de tipo %s" % (a.name, a.type.__name__))
            elif a.required:
                raise ValueError("falta el argumento obligatorio -%s" % a.name)
            else:
                vals[a.name] = a.default

        t0 = time.perf_counter()
        if cmd.kind == "image":
            img = load_image(vals.pop("input"))
            save_path = vals.pop("output")
            result = cmd.fn(img, **vals)
            save_image(result, save_path)
            print("OK -> %s (%dx%d, %d canal(es)) en %.3f s"
                  % (save_path, result.w, result.h, result.c, time.perf_counter() - t0))
        else:
            f, g = load_image(vals["original"]), load_image(vals["processed"])
            print("%s = %s" % (name.upper(), cmd.fn(f, g)))
        return 0
    except (ValueError, OSError) as e:
        print("Error: %s" % e, file=sys.stderr)
        return 1