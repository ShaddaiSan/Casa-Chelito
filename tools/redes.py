#!/usr/bin/env python3
"""Genera las piezas de redes sociales de Casa Chelito como imágenes PNG.

Uso:  python3 tools/redes.py            → redes/<mes>/*.png
      python3 tools/redes.py paletas    → solo las piezas cuyo nombre contiene "paletas"

Cada pieza es la foto a pantalla completa con el texto encima (español primero, francés
debajo), hecha en HTML + CSS, capturada con
Chromium (Playwright) a 1080 × 1350 (feed 4:5) o 1080 × 1920 (historia 9:16).
"""
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SRC = RAIZ / "src"
MES = "2026-11"
SALIDA = RAIZ / "redes" / "salida" / MES  # ignorada en git: las imágenes se entregan aparte
TRABAJO = RAIZ / "redes" / ".html"

FEED = (1080, 1350)
HISTORIA = (1080, 1920)

TELEFONO = "(514) 237-0991"
DIRECCION = "7351 Rue Jarry Est, Montréal"
HORARIO_ES = "Lunes a sábado 10–20 h · Domingo 10–19 h"


def foto(nombre):
    return (SRC / "images" / f"{nombre}.jpg").as_uri()


LOGO = (SRC / "images" / "logo.png").as_uri()
FUENTES = (SRC / "fonts").as_uri()

CSS = f"""
@font-face {{ font-family: "Lilita One"; src: url("{FUENTES}/lilita-one-latin.woff2"); }}
@font-face {{ font-family: "Nunito"; src: url("{FUENTES}/nunito-latin.woff2"); font-weight: 400 800; }}
@font-face {{ font-family: "Pacifico"; src: url("{FUENTES}/pacifico-latin.woff2"); }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: #222; }}
.lienzo {{ position: relative; overflow: hidden; font-family: "Nunito", sans-serif; color: #fff; background: #222; }}
.foto {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover;
  filter: saturate(1.08) contrast(1.04) brightness(1.03); }}
.sello {{ position: absolute; right: 40px; top: 40px; width: 120px; height: 120px; border-radius: 50%;
  box-shadow: 0 4px 16px rgba(0,0,0,.3); }}
.etiquetas {{ position: absolute; left: 48px; right: 48px; bottom: 52px; display: flex; flex-direction: column;
  align-items: flex-start; gap: 14px; }}
.pastilla {{ display: inline-block; border-radius: 999px; box-shadow: 0 4px 14px rgba(0,0,0,.28); }}
.pastilla.verde {{ background: #47704c; color: #fff; font-weight: 800; font-size: 34px; padding: 14px 30px; }}
.pastilla.nota {{ background: rgba(255,250,246,.95); color: #47704c; font-weight: 700; font-size: 26px; padding: 8px 22px; }}
.pastilla.roja {{ background: #a64033; color: #fff; font-weight: 800; font-size: 28px; padding: 10px 24px; }}
.pastilla.titulo {{ background: #fffaf6; color: #a64033; font-family: "Lilita One"; font-size: 72px;
  line-height: 1.05; padding: 18px 40px 14px; border-radius: 40px; }}
.pastilla.titulo small {{ display: block; font-family: "Nunito"; font-weight: 700; font-size: 30px; color: #47704c; }}
.chips {{ display: flex; flex-wrap: wrap; gap: 12px; }}
.chips span {{ background: rgba(255,250,246,.96); color: #7a2e24; font-weight: 800; font-size: 32px;
  padding: 9px 22px; border-radius: 999px; box-shadow: 0 3px 10px rgba(0,0,0,.22); }}
.chips small {{ font-size: 21px; font-weight: 700; color: #47704c; margin-left: 8px; }}
.pastilla.cta {{ background: #e0a23b; color: #7a2e24; font-weight: 800; font-size: 32px; padding: 12px 28px; }}
.pastilla.cta b {{ font-family: "Lilita One"; font-weight: 400; color: #a64033; letter-spacing: 1px; }}
/* Estilo de impacto: titular grande con contorno, en colores de la marca */
.impacto {{ position: absolute; left: 52px; right: 52px; bottom: 60px; display: flex; flex-direction: column;
  align-items: flex-start; gap: 18px; }}
.grande {{ font-family: "Lilita One"; line-height: .95; letter-spacing: 1px; transform: rotate(-3deg);
  transform-origin: left bottom; margin-bottom: 14px;
  text-shadow: -4px -4px 0 #7a2e24, 4px -4px 0 #7a2e24, -4px 4px 0 #7a2e24, 4px 4px 0 #7a2e24,
    0 -5px 0 #7a2e24, 0 5px 0 #7a2e24, -5px 0 0 #7a2e24, 5px 0 0 #7a2e24, 10px 12px 0 rgba(122,46,36,.85); }}
.cinta {{ display: inline-block; background: #a64033; color: #fffaf6; font-family: "Lilita One"; font-size: 46px;
  padding: 10px 30px 6px; transform: rotate(-2deg); box-shadow: 6px 6px 0 #7a2e24; }}
.cinta.mostaza {{ background: #e0a23b; color: #7a2e24; box-shadow: 6px 6px 0 #a64033; }}
.cinta.verde {{ background: #47704c; box-shadow: 6px 6px 0 #2c4a30; }}
.chips-color {{ display: flex; flex-wrap: wrap; gap: 14px; }}
.chips-color span {{ font-family: "Lilita One"; font-size: 44px; color: #fff; padding: 10px 26px 6px;
  border-radius: 999px; box-shadow: 4px 4px 0 rgba(0,0,0,.35); }}
.chips-color span:nth-child(4n+1) {{ background: #a64033; transform: rotate(-2deg); }}
.chips-color span:nth-child(4n+2) {{ background: #47704c; transform: rotate(1.5deg); }}
.chips-color span:nth-child(4n+3) {{ background: #e9843e; transform: rotate(-1deg); }}
.chips-color span:nth-child(4n+4) {{ background: #c25a7c; transform: rotate(2deg); }}
.fr-nota {{ font-size: 28px; font-weight: 700; color: #fffaf6; background: rgba(28,10,6,.55);
  padding: 6px 18px; border-radius: 999px; }}
.numero-grande {{ position: absolute; left: 40px; top: 10px; font-family: "Lilita One"; font-size: 300px;
  color: #e0a23b; line-height: 1; transform: rotate(-6deg);
  text-shadow: -6px -6px 0 #7a2e24, 6px -6px 0 #7a2e24, -6px 6px 0 #7a2e24, 6px 6px 0 #7a2e24, 14px 16px 0 rgba(122,46,36,.85); }}
.numero {{ position: absolute; left: 48px; top: 48px; width: 140px; height: 140px; border-radius: 50%;
  background: #fffaf6; color: #a64033; font-family: "Lilita One"; font-size: 100px;
  display: grid; place-items: center; box-shadow: 0 6px 20px rgba(0,0,0,.3); padding-top: 6px; }}
"""


def pagina(cuerpo, ancho, alto):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>'
            f'<body><div class="lienzo" style="width:{ancho}px;height:{alto}px">{cuerpo}</div></body></html>')


def sello():
    return f'<img class="sello" src="{LOGO}" alt="">'


def publicacion(nombre_foto, pos, linea, titulo="", sub="", previa="", chips=None, numero=None, nota="", cta=False,
                tamano=FEED, logo=True, abajo=52):
    """La foto manda: imagen limpia a pantalla completa y etiquetas pequeñas encima.

    titulo/sub → tarjeta crema (español grande, francés pequeño); linea → pastilla verde;
    previa → pastilla roja arriba de todo; chips → sabores.
    """
    partes = []
    if previa:
        partes.append(f'<div class="pastilla roja">{previa}</div>')
    if titulo:
        partes.append(f'<div class="pastilla titulo">{titulo}' + (f"<small>{sub}</small>" if sub else "") + "</div>")
    if chips:
        partes.append('<div class="chips">' + "".join(
            f"<span>{es}" + (f"<small>{fr}</small>" if fr else "") + "</span>" for es, fr in chips) + "</div>")
    if linea:
        partes.append(f'<div class="pastilla verde">{linea}</div>')
    if nota:
        partes.append(f'<div class="pastilla nota">{nota}</div>')
    if cta:
        partes.append('<div class="pastilla cta">Comenta <b>CHELITO</b> para más info</div>')
    return pagina(f"""
      <img class="foto" src="{foto(nombre_foto)}" style="object-position:{pos}">
      {f'<div class="numero">{numero}</div>' if numero else ""}
      {sello() if logo else ""}
      <div class="etiquetas" style="bottom:{abajo}px">{"".join(partes)}</div>""", *tamano)


def impacto(nombre_foto, pos, titulo, color="#ead2df", tam=150, cinta="", cinta_color="", fr="",
            chips=None, numero=None, cta=False, previa="", tamano=FEED):
    """Titular grande con contorno sobre la foto, en los colores de la marca."""
    partes = []
    if previa:
        partes.append(f'<div class="cinta verde" style="font-size:34px">{previa}</div>')
    partes.append(f'<div class="grande" style="font-size:{tam}px;color:{color}">{titulo}</div>')
    if chips:
        partes.append('<div class="chips-color">' + "".join(f"<span>{c}</span>" for c in chips) + "</div>")
    if cinta:
        partes.append(f'<div class="cinta {cinta_color}">{cinta}</div>')
    if fr:
        partes.append(f'<div class="fr-nota">FR · {fr}</div>')
    if cta:
        partes.append('<div class="pastilla cta">Comenta <b>CHELITO</b> para más info</div>')
    return pagina(f"""
      <img class="foto" src="{foto(nombre_foto)}" style="object-position:{pos}">
      {f'<div class="numero-grande">{numero}</div>' if numero else ""}
      {sello()}
      <div class="impacto">{"".join(partes)}</div>""", *tamano)


FUENTES_REDES = (RAIZ / "redes" / "fuentes").as_uri()

CSS_FLYER = f"""
@font-face {{ font-family: "Kaushan Script"; src: url("{FUENTES_REDES}/kaushan-script.woff2"); }}
@font-face {{ font-family: "Permanent Marker"; src: url("{FUENTES_REDES}/permanent-marker.woff2"); }}
@font-face {{ font-family: "Caveat Brush"; src: url("{FUENTES_REDES}/caveat-brush.woff2"); }}
.velo {{ position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(20,8,4,.82) 0%, rgba(20,8,4,.45) 26%, rgba(20,8,4,0) 42%),
              linear-gradient(0deg, rgba(20,8,4,.55) 0%, rgba(20,8,4,0) 22%),
              radial-gradient(ellipse at 50% 55%, rgba(0,0,0,0) 55%, rgba(0,0,0,.35) 100%); }}
.logo-flyer {{ position: absolute; right: 40px; top: 40px; width: 210px; height: 210px; border-radius: 50%;
  border: 6px solid #fffaf6; box-shadow: 0 8px 24px rgba(0,0,0,.45); }}
.cabeza {{ position: absolute; left: 70px; top: 50px; width: 760px; transform: rotate(-6deg); transform-origin: left top; }}
.linea1 {{ font-family: "Kaushan Script"; color: #fff; font-size: 116px; line-height: 1; margin-left: 60px;
  text-shadow: 0 6px 18px rgba(0,0,0,.6); }}
.linea2 {{ font-family: "Kaushan Script"; color: #f4b731; font-size: 200px; line-height: .9; margin-top: -6px;
  text-shadow: 0 8px 22px rgba(0,0,0,.55); }}
.bajada {{ font-family: "Permanent Marker"; color: #fff; font-size: 40px; white-space: nowrap; margin-top: 10px; margin-left: 20px;
  text-shadow: 0 3px 10px rgba(0,0,0,.7); position: relative; display: inline-block; }}
.subrayado {{ position: absolute; left: 34%; bottom: -26px; width: 300px; height: 34px; }}
.chispas {{ position: absolute; inset: 0; pointer-events: none; }}
.banda {{ position: absolute; left: 60px; bottom: 250px; transform: rotate(-3deg); transform-origin: left center;
  padding: 26px 70px 30px 56px; }}
.banda svg {{ position: absolute; inset: 0; width: 100%; height: 100%; filter: drop-shadow(0 6px 10px rgba(0,0,0,.4)); }}
.banda span {{ position: relative; font-family: "Caveat Brush"; color: #fff; font-size: 56px; line-height: 1;
  white-space: nowrap; }}
.pie-flyer {{ position: absolute; left: 70px; right: 70px; bottom: 92px; display: flex; gap: 14px; align-items: center; flex-wrap: wrap; }}
.pie-flyer .fr {{ background: #fffaf6; color: #47704c; font-weight: 800; font-size: 28px; padding: 10px 26px; border-radius: 999px;
  box-shadow: 0 4px 12px rgba(0,0,0,.3); }}
.bordado {{ position: absolute; left: 0; right: 0; bottom: 0; height: 66px; }}
.trazos {{ position: absolute; right: 30px; bottom: 80px; width: 150px; height: 90px; }}
"""

GOTA = "M0,0 C9,-2 16,14 11,78 C10,90 -10,90 -11,78 C-15,24 -8,2 0,0 Z"


def chispas(lista):
    """Salpicaduras de pincel: (x, y, ángulo, escala, color)."""
    return '<svg class="chispas" viewBox="0 0 1080 1350">' + "".join(
        f'<path d="{GOTA}" fill="{c}" transform="translate({x} {y}) rotate({r}) scale({e})"/>'
        for x, y, r, e, c in lista) + "</svg>"


BORDADO = """<svg class="bordado" viewBox="0 0 1080 66" preserveAspectRatio="none">
  <defs><pattern id="b" width="96" height="66" patternUnits="userSpaceOnUse">
    <rect width="96" height="66" fill="#2a120c"/>
    <path d="M0,8 L12,0 L24,8 L36,0 L48,8 L60,0 L72,8 L84,0 L96,8" stroke="#e0a23b" stroke-width="4" fill="none"/>
    <path d="M0,58 L12,66 L24,58 L36,66 L48,58 L60,66 L72,58 L84,66 L96,58" stroke="#e0a23b" stroke-width="4" fill="none"/>
    <path d="M48,18 L60,33 L48,48 L36,33 Z" fill="#c8321e"/><circle cx="48" cy="33" r="5" fill="#f4b731"/>
    <path d="M10,33 C16,22 26,22 30,33 C26,44 16,44 10,33 Z" fill="#2f8a43"/>
    <path d="M66,33 C70,22 80,22 86,33 C80,44 70,44 66,33 Z" fill="#2f8a43"/>
    <circle cx="0" cy="33" r="6" fill="#e9843e"/><circle cx="96" cy="33" r="6" fill="#e9843e"/>
  </pattern></defs><rect width="1080" height="66" fill="url(#b)"/></svg>"""

TRAZOS = """<svg class="trazos" viewBox="0 0 150 90">
  <path d="M10,80 C50,55 95,30 145,8" stroke="#c8321e" stroke-width="9" stroke-linecap="round" fill="none"/>
  <path d="M22,88 C60,64 100,42 146,24" stroke="#f4b731" stroke-width="8" stroke-linecap="round" fill="none"/>
  <path d="M40,90 C72,72 108,56 146,40" stroke="#2f8a43" stroke-width="8" stroke-linecap="round" fill="none"/>
</svg>"""

BANDA = """<svg viewBox="0 0 1000 120" preserveAspectRatio="none">
  <path d="M18,14 C200,4 600,10 985,6 L965,34 L998,58 L972,84 L992,114 C640,118 300,112 12,118 L30,92 L4,64 L26,40 Z" fill="#2f7a3f"/>
  <path d="M60,22 L930,16 M80,104 L900,108" stroke="#3f9150" stroke-width="5" stroke-linecap="round" opacity=".7"/>
</svg>"""


def flyer(nombre_foto, pos, linea1, linea2, bajada, banda, fr, cta=True, salpicaduras=None, subrayado=True):
    """Estilo flyer: titular de pincel, salpicaduras, banda verde y borde bordado."""
    salpicaduras = salpicaduras or [
        (70, 150, -60, .8, "#f4b731"), (52, 250, -95, .75, "#2f8a43"), (60, 345, -125, .65, "#c8321e"),
        (880, 300, 60, .7, "#c8321e"), (905, 375, 95, .65, "#f4b731"), (850, 395, 130, .55, "#2f8a43")]
    sub = ('<svg class="subrayado" viewBox="0 0 300 34"><path d="M4,24 C80,10 200,6 296,14 C200,16 90,22 10,32 Z" '
           'fill="#f4b731"/></svg>') if subrayado else ""
    cta_html = '<div class="pastilla cta">Comenta <b>CHELITO</b> para más info</div>' if cta else ""
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}{CSS_FLYER}</style></head><body>'
            f'<div class="lienzo" style="width:1080px;height:1350px">'
            f'<img class="foto" src="{foto(nombre_foto)}" style="object-position:{pos}">'
            f'<div class="velo"></div>{chispas(salpicaduras)}'
            f'<div class="cabeza"><div class="linea1">{linea1}</div><div class="linea2">{linea2}</div>'
            f'<div class="bajada">{bajada}{sub}</div></div>'
            f'<img class="logo-flyer" src="{LOGO}" alt="">'
            f'<div class="banda">{BANDA}<span>{banda}</span></div>'
            f'<div class="pie-flyer"><div class="fr">FR · {fr}</div>{cta_html}</div>'
            f'{TRAZOS}{BORDADO}</div></body></html>')


def flyers():
    return {
        "flyer-gansito": flyer("gansito-marias", "4% 75%", "El antojo de", "Siempre",
                               "EL SABOR DE MÉXICO EN CADA BOCADO",
                               "Si comiste esto de niño, eres de los nuestros",
                               "Les collations de notre enfance"),
    }


# ---------------------------------------------------------------- Piezas

def carrusel_paletas():
    """Jue 5 nov · C. Educativo · «Paletas 101»."""
    agua = ["Mango", "Fresa", "Tamarindo", "Piña", "Limón"]
    crema = ["Coco", "Fresa", "Rompope", "Nuez", "Pistache", "Vainilla", "Oreo", "Chocolate", "Mango"]
    return {
        "paletas-101-1-portada": impacto(
            "paletas-fila", "50% 60%", "PALETAS", "#ead2df", 190, previa="¿Sabías que…?",
            cinta="De agua, con chamoy o de crema", fr="Les paletas : eau, chamoy ou crème"),
        "paletas-101-2-agua": impacto(
            "paleta-verde", "45% 50%", "DE AGUA", "#e0a23b", 170, chips=agua,
            cinta="Frutales y refrescantes", cinta_color="verde", fr="À base d'eau, fruitées"),
        "paletas-101-3-chamoy": impacto(
            "paletas-colores", "55% 55%", "CON<br>CHAMOY", "#e9843e", 160, chips=agua,
            cinta="Dulce, saladito y enchilado", fr="Avec chamoy : sucré, salé, piquant"),
        "paletas-101-4-crema": impacto(
            "paletas-sobre-congelador", "40% 50%", "DE CREMA", "#ead2df", 160, chips=crema,
            cinta="Cremositas", cinta_color="mostaza", fr="À la crème, onctueuses"),
        "paletas-101-5-cierre": impacto(
            "paletas-acomodadas", "55% 50%", "¿CUÁL VAS<br>A PROBAR?", "#e0a23b", 130,
            cinta=DIRECCION, cinta_color="verde", fr="Laquelle tu essaies ?", cta=True),
    }


def carrusel_conchas():
    """Jue 12 nov · D. Interacción · «¿Cuál agarras primero?»."""
    panes = [("concha-con-leche", "62% 70%", "CONCHA<br>CLÁSICA", "#ead2df", "La classique"),
             ("concha-rosa", "35% 40%", "CONCHA<br>DE COLOR", "#e0a23b", "Concha colorée"),
             ("pan-de-muerto-concha", "50% 45%", "PAN DE MUERTO<br>DE CONCHA", "#ead2df", "Pan de muerto avec croûte de concha")]
    piezas = {
        "conchas-1-portada": publicacion(
            "pan-de-muerto-concha", "50% 40%", "Desliza →",
            titulo="¿Cuál agarras primero?", sub="Laquelle en premier ?", cta=True),
    }
    for i, (n, p, titulo, color, fr) in enumerate(panes, start=1):
        piezas[f"conchas-{i + 1}-opcion-{i}"] = impacto(n, p, titulo, color, 120, fr=fr, cta=True)
    piezas["conchas-5-cierre"] = impacto(
        "tienda-pan-estantes", "100% 50%", "¿CUÁL ES TU<br>FAVORITA?", "#e0a23b", 140,
        cinta="Pan mexicano todos los días", cinta_color="verde", fr="Laquelle est ta préférée ?", cta=True)
    return piezas


def livraison():
    """Jue 19 nov · E. Promoción · «¡Te lo llevamos a casa!»."""
    comun = dict(titulo=f"¡Te lo llevamos a casa!<br>{TELEFONO}", sub="On livre ! Appelle-nous",
                 previa="Pedidos por teléfono")
    return {
        "livraison-feed": publicacion("tienda-mostrador", "50% 55%", HORARIO_ES, cta=True, **comun),
        "livraison-historia": publicacion("tienda-mostrador", "45% 50%", HORARIO_ES, tamano=HISTORIA,
                                          abajo=320, cta=True, **comun),
    }


def sueltas():
    """Banco: publicaciones de una sola foto."""
    return {
        "nostalgia-gansito": publicacion("gansito-marias", "40% 60%",
                                         "Si comiste esto de niño, eres de los nuestros",
                                         nota="FR · Les collations de notre enfance", cta=True),
        "nostalgia-carrito": publicacion("carrito-paletero", "62% 40%", "El carrito paletero también emigró",
                                         nota="FR · Le chariot à paletas, comme au Mexique", cta=True),
        "nostalgia-fabuloso": publicacion("hogar-limpieza", "55% 45%", "Si tu casa olía a Fabuloso los sábados…",
                                          nota="FR · Les incontournables d'une maison mexicaine", cta=True),
        "tamales": publicacion("tamal", "50% 4%", f"¡Hay tamales! · Apártalos al {TELEFONO}",
                               nota="FR · Il y a des tamales ! Appelle pour réserver", logo=False, cta=True),
    }


# ---------------------------------------------------------------- Captura

def main():
    filtro = sys.argv[1] if len(sys.argv) > 1 else ""
    piezas = {}
    for grupo in (carrusel_paletas, carrusel_conchas, livraison, sueltas, flyers):
        piezas.update(grupo())
    piezas = {k: v for k, v in piezas.items() if filtro in k}
    SALIDA.mkdir(parents=True, exist_ok=True)
    TRABAJO.mkdir(parents=True, exist_ok=True)
    trabajos = []
    for nombre, html in piezas.items():
        archivo = TRABAJO / f"{nombre}.html"
        archivo.write_text(html)
        trabajos.append({"html": archivo.as_uri(), "png": str(SALIDA / f"{nombre}.png")})
    subprocess.run(["node", str(RAIZ / "tools" / "capturar.js"), json.dumps(trabajos)], check=True)
    print(f"{len(trabajos)} imágenes en {SALIDA.relative_to(RAIZ)}/")


if __name__ == "__main__":
    main()
