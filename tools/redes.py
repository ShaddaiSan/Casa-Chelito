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
SALIDA = RAIZ / "redes" / MES
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
    for grupo in (carrusel_paletas, carrusel_conchas, livraison, sueltas):
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
