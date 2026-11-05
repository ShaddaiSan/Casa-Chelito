#!/usr/bin/env python3
"""Arma el Reel «Encontré México en Montreal» (1080 × 1920, 30 fps) con las fotos de src/images.

Uso:  python3 tools/reel.py   → redes/salida/reels/encontre-mexico-en-montreal.mp4

Cada escena es una foto con movimiento de cámara (zoom o paneo suave), su texto en español
(grande) y francés (pequeño), y un ajuste de color cálido. Los textos y la pantalla final se
dibujan en HTML con las fuentes de la marca y se capturan como PNG transparentes; también se
guardan sueltos para poder rehacer el Reel en CapCut.

Para cambiar el orden, la duración, el movimiento o los textos, se edita ESCENAS.
"""
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
FOTOS = RAIZ / "src" / "images"
SALIDA = RAIZ / "redes" / "salida" / "reels"
CAPAS = SALIDA / "capas"
ANCHO, ALTO, FPS = 1080, 1920, 30
NOMBRE = "encontre-mexico-en-montreal"

# foto, segundos, (centro x, centro y, zoom) al inicio y al final — coordenadas de la foto original
ESCENAS = [
    dict(foto="tienda-mostrador", dur=1.6, ini=(1000, 760, 1.00), fin=(1000, 760, 1.25),
         es="POV: encontraste<br>México en Montreal", fr="POV : tu trouves le Mexique à Montréal"),
    dict(foto="tienda-pan-estantes", dur=1.4, ini=(950, 667, 1.0), fin=(1450, 667, 1.0),
         es="Pan mexicano", fr="Pain mexicain"),
    dict(foto="pan-de-muerto-horneado", dur=1.2, ini=(1000, 667, 1.0), fin=(1000, 700, 1.13)),
    dict(foto="concha-con-leche", dur=1.2, ini=(1250, 700, 1.0), fin=(1330, 750, 1.1),
         es="Como en casa", fr="Comme à la maison"),
    dict(foto="paletas-fila", dur=1.2, ini=(1250, 760, 1.05), fin=(750, 760, 1.05),
         es="Paletas artesanales", fr="Paletas artisanales"),
    dict(foto="carrito-paletero", dur=1.2, ini=(700, 667, 1.0), fin=(560, 520, 1.2)),
    dict(foto="salsas-la-anita", dur=1.2, ini=(700, 760, 1.15), fin=(700, 590, 1.15),
         es="Salsas, chiles, dulces…", fr="Sauces, piments, bonbons…"),
    dict(foto="estante-abarrotes", dur=1.2, ini=(750, 667, 1.0), fin=(1250, 667, 1.0),
         es="Todo lo que extrañas", fr="Tout ce qui te manque"),
    dict(foto="tamal", dur=1.4, ini=(610, 1150, 1.26), fin=(620, 1170, 1.38),
         es="¡Y tamales!", fr="Et des tamales !", texto_abajo=True),
]
DUR_FINAL = 3.4
TRANSICION = 0.27  # barrido entre la escena 1 y 2, y zoom hacia la pantalla final

# Ajustes de luz que también usa el sitio
AJUSTES = json.loads((FOTOS / "ajustes.json").read_text())


# ---------------------------------------------------------------- Capas de texto (HTML → PNG)

FUENTES = (RAIZ / "src" / "fonts").as_uri()
FUENTES_REDES = (RAIZ / "redes" / "fuentes").as_uri()
LOGO = (FOTOS / "logo.png").as_uri()

CSS = f"""
@font-face {{ font-family: "Nunito"; src: url("{FUENTES}/nunito-latin.woff2"); font-weight: 400 800; }}
@font-face {{ font-family: "Lilita One"; src: url("{FUENTES}/lilita-one-latin.woff2"); }}
@font-face {{ font-family: "Kaushan Script"; src: url("{FUENTES_REDES}/kaushan-script.woff2"); }}
@font-face {{ font-family: "Caveat Brush"; src: url("{FUENTES_REDES}/caveat-brush.woff2"); }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ background: transparent; }}
.capa {{ position: relative; width: {ANCHO}px; height: {ALTO}px; overflow: hidden; }}
.texto {{ position: absolute; left: 70px; right: 150px; display: flex; flex-direction: column; align-items: flex-start; gap: 22px; }}
.es {{ font-family: "Kaushan Script"; color: #f4b731; font-size: 120px; line-height: 1.05; transform: rotate(-4deg);
  transform-origin: left center;
  text-shadow: -4px -4px 0 #7a2e24, 4px -4px 0 #7a2e24, -4px 4px 0 #7a2e24, 4px 4px 0 #7a2e24,
    0 -5px 0 #7a2e24, 0 5px 0 #7a2e24, -5px 0 0 #7a2e24, 5px 0 0 #7a2e24, 9px 11px 0 rgba(60,20,10,.75); }}
.es.blanco {{ color: #fff; }}
.fr {{ font-family: "Nunito"; font-weight: 800; font-size: 34px; color: #47704c; background: #fffaf6;
  padding: 10px 26px; border-radius: 999px; box-shadow: 0 4px 14px rgba(0,0,0,.35); }}
"""

GOTA = "M0,0 C9,-2 16,14 11,78 C10,90 -10,90 -11,78 C-15,24 -8,2 0,0 Z"


def html_texto(es, fr, abajo=False, blanco=False):
    pos = "top:1060px" if abajo else "top:300px"
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
            f'<div class="capa"><div class="texto" style="{pos}">'
            f'<div class="es{" blanco" if blanco else ""}">{es}</div><div class="fr">FR · {fr}</div></div></div></body></html>')


def html_final():
    chispas = "".join(
        f'<path d="{GOTA}" fill="{c}" transform="translate({x} {y}) rotate({r}) scale({e})"/>'
        for x, y, r, e, c in [(250, 330, -60, 1.0, "#f4b731"), (190, 450, -100, .9, "#2f8a43"),
                              (230, 570, -135, .8, "#c8321e"), (830, 330, 60, 1.0, "#c8321e"),
                              (890, 450, 100, .9, "#f4b731"), (850, 570, 135, .8, "#2f8a43")])
    bordado = """<svg style="position:absolute;left:0;right:0;bottom:0;height:90px;width:100%" viewBox="0 0 1080 90" preserveAspectRatio="none">
      <defs><pattern id="b" width="120" height="90" patternUnits="userSpaceOnUse">
        <rect width="120" height="90" fill="#2a120c"/>
        <path d="M0,10 L15,0 L30,10 L45,0 L60,10 L75,0 L90,10 L105,0 L120,10" stroke="#e0a23b" stroke-width="5" fill="none"/>
        <path d="M0,80 L15,90 L30,80 L45,90 L60,80 L75,90 L90,80 L105,90 L120,80" stroke="#e0a23b" stroke-width="5" fill="none"/>
        <path d="M60,25 L76,45 L60,65 L44,45 Z" fill="#c8321e"/><circle cx="60" cy="45" r="7" fill="#f4b731"/>
        <path d="M12,45 C20,30 32,30 38,45 C32,60 20,60 12,45 Z" fill="#2f8a43"/>
        <path d="M82,45 C88,30 100,30 108,45 C100,60 88,60 82,45 Z" fill="#2f8a43"/>
      </pattern></defs><rect width="1080" height="90" fill="url(#b)"/></svg>"""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
      .final {{ position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; text-align: center;
        padding-top: 250px; color: #fff; }}
      .final img {{ width: 400px; height: 400px; border-radius: 50%; border: 10px solid #fffaf6; box-shadow: 0 14px 40px rgba(0,0,0,.5); }}
      .lema {{ font-family: "Kaushan Script"; font-size: 96px; color: #f4b731; margin-top: 60px; line-height: 1.05;
        text-shadow: 0 6px 18px rgba(0,0,0,.6); }}
      .dir {{ font-family: "Lilita One"; font-size: 62px; margin-top: 46px; letter-spacing: 1px; text-shadow: 0 4px 12px rgba(0,0,0,.6); }}
      .hor {{ font-family: "Nunito"; font-weight: 800; font-size: 38px; margin-top: 14px; color: #f6d9e6; }}
      .cta {{ margin-top: 54px; background: #e0a23b; color: #7a2e24; font-family: "Nunito"; font-weight: 800; font-size: 46px;
        padding: 20px 46px; border-radius: 999px; box-shadow: 0 8px 0 #a64033; }}
      .cta b {{ font-family: "Lilita One"; font-weight: 400; color: #a64033; letter-spacing: 1px; }}
      .fr2 {{ margin-top: 34px; font-family: "Nunito"; font-weight: 700; font-size: 32px; color: #fffaf6; opacity: .9; }}
    </style></head><body><div class="capa">
      <svg style="position:absolute;inset:0" viewBox="0 0 1080 1920">{chispas}</svg>
      <div class="final">
        <img src="{LOGO}" alt="">
        <div class="lema">El sabor de casa,<br>aquí en Montreal</div>
        <div class="dir">7351 Rue Jarry E</div>
        <div class="hor">Lun–sáb 10–20 h · Dom 10–19 h</div>
        <div class="cta">Comenta <b>CHELITO</b> para más info</div>
        <div class="fr2">FR · Le goût de la maison, ici à Montréal</div>
      </div>{bordado}</div></body></html>"""


def capturar_capas():
    CAPAS.mkdir(parents=True, exist_ok=True)
    trabajos = []
    for i, e in enumerate(ESCENAS, start=1):
        if "es" in e:
            archivo = CAPAS / f"texto-{i:02d}.html"
            archivo.write_text(html_texto(e["es"], e["fr"], e.get("texto_abajo", False), blanco=(i == 1)))
            trabajos.append({"html": archivo.as_uri(), "png": str(CAPAS / f"texto-{i:02d}.png")})
    archivo = CAPAS / "final.html"
    archivo.write_text(html_final())
    trabajos.append({"html": archivo.as_uri(), "png": str(CAPAS / "final.png")})
    script = """
const { chromium } = require('playwright');
(async () => {
  const t = JSON.parse(process.argv[1]);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: %d, height: %d } });
  for (const { html, png } of t) {
    await p.goto(html, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: png, omitBackground: true });
  }
  await b.close();
})();""" % (ANCHO, ALTO)
    subprocess.run(["node", "-e", script, json.dumps(trabajos)], check=True)
    for t in trabajos:
        Path(t["html"].replace("file://", "")).unlink()


# ---------------------------------------------------------------- Imagen de cada cuadro

def cargar(nombre):
    im = ImageOps.exif_transpose(Image.open(FOTOS / f"{nombre}.jpg")).convert("RGB")
    a = AJUSTES.get(nombre, {})
    if "brillo" in a:
        im = ImageEnhance.Brightness(im).enhance(a["brillo"])
    if "contraste" in a:
        im = ImageEnhance.Contrast(im).enhance(a["contraste"])
    return im


def encuadre(im, cx, cy, zoom):
    """Recorte 9:16 centrado en (cx, cy) con el zoom dado, sin salir de la foto."""
    w, h = im.size
    alto = min(h, w * ALTO / ANCHO) / zoom
    ancho = alto * ANCHO / ALTO
    x0 = min(max(cx - ancho / 2, 0), w - ancho)
    y0 = min(max(cy - alto / 2, 0), h - alto)
    return im.transform((ANCHO, ALTO), Image.EXTENT, (x0, y0, x0 + ancho, y0 + alto), Image.BICUBIC)


def suave(t):
    return t * t * (3 - 2 * t)


def viñeta():
    m = Image.new("L", (ANCHO, ALTO), 0)
    d = ImageDraw.Draw(m)
    d.ellipse((-260, -200, ANCHO + 260, ALTO + 200), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(220))
    return Image.merge("RGB", [m.point(lambda v: 150 + v * 105 // 255)] * 3)


VIÑETA = None


def color(im):
    """Tono cálido y de cine: calidez, saturación, contraste y viñeta suave."""
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.045 + 3)))
    b = b.point(lambda v: int(v * 0.95))
    im = Image.merge("RGB", (r, g, b))
    im = ImageEnhance.Color(im).enhance(1.12)
    im = ImageEnhance.Contrast(im).enhance(1.06)
    return ImageChops.multiply(im, VIÑETA)


def capa_animada(capa, t):
    """Entrada tipo «pop»: crece de 85 % a 100 % y aparece en 0.3 s."""
    if t >= 0.3:
        return capa
    k = suave(t / 0.3)
    escala = 0.85 + 0.15 * k
    w, h = int(ANCHO * escala), int(ALTO * escala)
    c = capa.resize((w, h), Image.BICUBIC)
    lienzo = Image.new("RGBA", (ANCHO, ALTO), (0, 0, 0, 0))
    lienzo.paste(c, ((ANCHO - w) // 6, (ALTO - h) // 3))
    alfa = lienzo.getchannel("A").point(lambda v: int(v * k))
    lienzo.putalpha(alfa)
    return lienzo


def main():
    global VIÑETA
    SALIDA.mkdir(parents=True, exist_ok=True)
    capturar_capas()
    VIÑETA = viñeta()
    fotos = {e["foto"]: cargar(e["foto"]) for e in ESCENAS}
    capas = {i: Image.open(CAPAS / f"texto-{i:02d}.png").convert("RGBA")
             for i in range(1, len(ESCENAS) + 1) if (CAPAS / f"texto-{i:02d}.png").exists()}
    final_capa = Image.open(CAPAS / "final.png").convert("RGBA")
    fondo_final = encuadre(fotos["tienda-mostrador"], 1000, 760, 1.1).filter(ImageFilter.GaussianBlur(24))
    fondo_final = ImageEnhance.Brightness(fondo_final).enhance(0.42)
    fondo_final.paste(final_capa, (0, 0), final_capa)

    def cuadro_escena(i, t):
        e = ESCENAS[i]
        k = suave(min(t / e["dur"], 1))
        cx, cy, z = (a + (b - a) * k for a, b in zip(e["ini"], e["fin"]))
        im = color(encuadre(fotos[e["foto"]], cx, cy, z))
        if (i + 1) in capas:
            c = capa_animada(capas[i + 1], t)
            im.paste(c, (0, 0), c)
        return im

    inicios, acumulado = [], 0.0
    for e in ESCENAS:
        inicios.append(acumulado)
        acumulado += e["dur"]
    total = acumulado + DUR_FINAL

    salida = SALIDA / f"{NOMBRE}.mp4"
    ffmpeg = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{ANCHO}x{ALTO}",
         "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
         "-shortest", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
         "-profile:v", "high", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "128k", str(salida)],
        stdin=subprocess.PIPE)

    for n in range(round(total * FPS)):
        t = n / FPS
        if t >= acumulado:  # pantalla final, con zoom de entrada
            tf = t - acumulado
            if tf < TRANSICION:
                k = suave(tf / TRANSICION)
                a = cuadro_escena(len(ESCENAS) - 1, ESCENAS[-1]["dur"] + tf)
                s = 1 + 0.35 * k
                a = a.resize((int(ANCHO * s), int(ALTO * s)), Image.BICUBIC).crop(
                    (int((ANCHO * s - ANCHO) / 2), int((ALTO * s - ALTO) / 2),
                     int((ANCHO * s - ANCHO) / 2) + ANCHO, int((ALTO * s - ALTO) / 2) + ALTO))
                im = Image.blend(a, fondo_final, k)
            else:
                im = fondo_final
        else:
            i = max(j for j, s in enumerate(inicios) if s <= t)
            t_local = t - inicios[i]
            im = cuadro_escena(i, t_local)
            # barrido (whip pan) entre la escena 1 y la 2
            fin1 = inicios[1]
            if i == 0 and t_local > ESCENAS[0]["dur"] - TRANSICION / 2 or i == 1 and t_local < TRANSICION / 2:
                k = (t - (fin1 - TRANSICION / 2)) / TRANSICION
                a = cuadro_escena(0, min(t, ESCENAS[0]["dur"]))
                b = cuadro_escena(1, max(t - fin1, 0))
                desplazo = int(ANCHO * suave(k))
                lienzo = Image.new("RGB", (ANCHO, ALTO))
                lienzo.paste(a, (-desplazo, 0))
                lienzo.paste(b, (ANCHO - desplazo, 0))
                im = lienzo.filter(ImageFilter.BoxBlur(18)).resize((ANCHO // 4, ALTO)).resize((ANCHO, ALTO))
        ffmpeg.stdin.write(im.tobytes())
    ffmpeg.stdin.close()
    ffmpeg.wait()
    (SALIDA / "guion.json").write_text(json.dumps(
        {"escenas": ESCENAS, "pantalla_final_seg": DUR_FINAL, "total_seg": total}, ensure_ascii=False, indent=2))
    print(f"Listo: {salida.relative_to(RAIZ)} ({total:.1f} s)")


if __name__ == "__main__":
    main()
