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
.numero {{ position: absolute; left: 48px; top: 48px; width: 140px; height: 140px; border-radius: 50%;
  background: #fffaf6; color: #a64033; font-family: "Lilita One"; font-size: 100px;
  display: grid; place-items: center; box-shadow: 0 6px 20px rgba(0,0,0,.3); padding-top: 6px; }}
"""


def pagina(cuerpo, ancho, alto):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>'
            f'<body><div class="lienzo" style="width:{ancho}px;height:{alto}px">{cuerpo}</div></body></html>')


def sello():
    return f'<img class="sello" src="{LOGO}" alt="">'


def publicacion(nombre_foto, pos, linea, titulo="", sub="", previa="", chips=None, numero=None, nota="",
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
    return pagina(f"""
      <img class="foto" src="{foto(nombre_foto)}" style="object-position:{pos}">
      {f'<div class="numero">{numero}</div>' if numero else ""}
      {sello() if logo else ""}
      <div class="etiquetas" style="bottom:{abajo}px">{"".join(partes)}</div>""", *tamano)


# ---------------------------------------------------------------- Piezas

def carrusel_paletas():
    """Jue 5 nov · C. Educativo · «Paletas 101»."""
    agua = [("Mango", "mangue"), ("Fresa", "fraise"), ("Tamarindo", "tamarin"), ("Piña", "ananas"), ("Limón", "lime")]
    crema = [("Coco", ""), ("Fresa", "fraise"), ("Rompope", ""), ("Nuez", "pacane"), ("Pistache", ""),
             ("Vainilla", "vanille"), ("Oreo", ""), ("Chocolate", "chocolat"), ("Mango", "mangue")]
    return {
        "paletas-101-1-portada": publicacion(
            "paletas-fila", "50% 60%", "Desliza y elige la tuya →",
            titulo="Paletas 101", sub="De agua, con chamoy o de crema · eau, chamoy ou crème", previa="¿Sabías que…?"),
        "paletas-101-2-agua": publicacion(
            "paleta-verde", "45% 50%", "Frutales y refrescantes · fruitées",
            titulo="De agua", sub="À base d'eau", previa="1 / 3", chips=agua),
        "paletas-101-3-chamoy": publicacion(
            "paletas-colores", "55% 55%", "Dulce, saladito y enchilado · sucré, salé, piquant",
            titulo="Con chamoy", sub="Avec chamoy", previa="2 / 3", chips=agua),
        "paletas-101-4-crema": publicacion(
            "paletas-sobre-congelador", "40% 50%", "Cremositas · onctueuses",
            titulo="De crema", sub="À la crème", previa="3 / 3", chips=crema),
        "paletas-101-5-cierre": publicacion(
            "paletas-acomodadas", "55% 50%", DIRECCION, nota=HORARIO_ES,
            titulo="¿Cuál vas a probar?", sub="Laquelle tu essaies ?"),
    }


def carrusel_conchas():
    """Jue 12 nov · D. Interacción · «¿Cuál agarras primero?»."""
    panes = [("concha-con-leche", "62% 70%", "Concha clásica · la classique"),
             ("concha-rosa", "35% 40%", "Concha de color · concha colorée"),
             ("pan-de-muerto-concha", "50% 45%", "Pan de muerto de concha · avec croûte de concha")]
    piezas = {
        "conchas-1-portada": publicacion(
            "pan-de-muerto-concha", "50% 40%", "Desliza y comenta 1, 2 o 3 →",
            titulo="¿Cuál agarras primero?", sub="Laquelle en premier ?", previa="Vota en comentarios"),
    }
    for i, (n, p, linea) in enumerate(panes, start=1):
        piezas[f"conchas-{i + 1}-opcion-{i}"] = publicacion(n, p, linea, numero=i)
    piezas["conchas-5-cierre"] = publicacion(
        "tienda-pan-estantes", "100% 50%", "El viernes contamos los votos en historias",
        titulo="Comenta 1, 2 o 3", sub="Commente ton numéro !")
    return piezas


def livraison():
    """Jue 19 nov · E. Promoción · «¡Te lo llevamos a casa!»."""
    comun = dict(titulo=f"¡Te lo llevamos a casa!<br>{TELEFONO}", sub="On livre ! Appelle-nous",
                 previa="Pedidos por teléfono")
    return {
        "livraison-feed": publicacion("tienda-mostrador", "50% 55%", HORARIO_ES, **comun),
        "livraison-historia": publicacion("tienda-mostrador", "45% 50%", HORARIO_ES, tamano=HISTORIA,
                                          abajo=320, **comun),
    }


def sueltas():
    """Banco: publicaciones de una sola foto."""
    return {
        "nostalgia-gansito": publicacion("gansito-marias", "40% 60%",
                                         "Si comiste esto de niño, eres de los nuestros",
                                         nota="FR · Les collations de notre enfance"),
        "nostalgia-carrito": publicacion("carrito-paletero", "62% 40%", "El carrito paletero también emigró",
                                         nota="FR · Le chariot à paletas, comme au Mexique"),
        "nostalgia-fabuloso": publicacion("hogar-limpieza", "55% 45%", "Si tu casa olía a Fabuloso los sábados…",
                                          nota="FR · Les incontournables d'une maison mexicaine"),
        "tamales": publicacion("tamal", "50% 4%", f"¡Hay tamales! · Apártalos al {TELEFONO}",
                               nota="FR · Il y a des tamales ! Appelle pour réserver", logo=False),
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
