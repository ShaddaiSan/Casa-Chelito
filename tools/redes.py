#!/usr/bin/env python3
"""Genera las piezas de redes sociales de Casa Chelito como imágenes PNG.

Uso:  python3 tools/redes.py            → redes/<mes>/*.png
      python3 tools/redes.py paletas    → solo las piezas cuyo nombre contiene "paletas"

Cada pieza es HTML + CSS con las fuentes, colores y fotos del sitio, capturada con
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
DIRECCION = "7351, rue Jarry Est · Montréal"
HORARIO_FR = "Lun–sam 10 h–20 h · dim 10 h–19 h"
HORARIO_ES = "Lun–sáb 10–20 h · dom 10–19 h"


def foto(nombre):
    return (SRC / "images" / f"{nombre}.jpg").as_uri()


LOGO = (SRC / "images" / "logo.png").as_uri()
PICADO = (SRC / "css" / "papel-picado.svg").as_uri()
FUENTES = (SRC / "fonts").as_uri()

CSS = f"""
@font-face {{ font-family: "Lilita One"; src: url("{FUENTES}/lilita-one-latin.woff2"); }}
@font-face {{ font-family: "Nunito"; src: url("{FUENTES}/nunito-latin.woff2"); font-weight: 400 800; }}
@font-face {{ font-family: "Pacifico"; src: url("{FUENTES}/pacifico-latin.woff2"); }}
:root {{
  --rosa: #ead2df; --rosa-claro: #f7ecf2; --crema: #fffaf6;
  --rojo: #a64033; --rojo-oscuro: #7a2e24; --verde: #47704c;
  --mostaza: #e0a23b; --naranja: #e9843e; --naranja-texto: #a84b14; --texto: #4a2620;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: #333; }}
.lienzo {{ position: relative; overflow: hidden; font-family: "Nunito", sans-serif; color: var(--texto); }}
.foto {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
.picado {{ position: absolute; left: 0; right: 0; top: 0; height: 96px;
  background: url("{PICADO}") repeat-x top left / auto 96px; z-index: 3; }}
.pill {{ position: absolute; left: 64px; top: 140px; z-index: 4; display: inline-block;
  background: var(--verde); color: var(--crema); font-weight: 800; font-size: 30px;
  padding: 12px 28px; border-radius: 999px; letter-spacing: .3px; }}
.sello {{ position: absolute; right: 44px; bottom: 44px; width: 132px; height: 132px; border-radius: 50%;
  z-index: 5; box-shadow: 0 6px 18px rgba(0,0,0,.25); background: var(--rosa); }}
.titulo {{ font-family: "Lilita One", sans-serif; color: var(--rojo); line-height: 1.02; letter-spacing: .5px; }}
.es {{ font-weight: 700; color: var(--verde); }}
.script {{ font-family: "Pacifico", cursive; color: var(--naranja-texto); }}
.puntos {{ width: 180px; height: 14px; margin: 26px 0;
  background: radial-gradient(circle at 7px 7px, var(--rojo) 6px, transparent 7px) 0 0 / 28px 14px repeat-x; }}
.panel {{ position: absolute; left: 0; right: 0; bottom: 0; background: var(--rosa); padding: 56px 64px 60px; z-index: 2; }}
.panel::before {{ content: ""; position: absolute; left: 0; right: 0; top: -1px; height: 0; }}
.datos {{ font-size: 28px; font-weight: 700; color: var(--rojo-oscuro); }}
.numero {{ position: absolute; left: 64px; top: 64px; z-index: 4; width: 170px; height: 170px; border-radius: 50%;
  background: var(--crema); color: var(--rojo); font-family: "Lilita One"; font-size: 120px;
  display: grid; place-items: center; box-shadow: 0 8px 24px rgba(0,0,0,.3); padding-top: 6px; }}
.etiqueta {{ position: absolute; left: 64px; bottom: 64px; z-index: 4; background: var(--crema);
  border-radius: 24px; padding: 22px 32px; box-shadow: 0 8px 24px rgba(0,0,0,.25); }}
.lista {{ list-style: none; }}
.lista li {{ display: flex; align-items: baseline; gap: 18px; font-size: 44px; font-weight: 800;
  padding: 14px 0; border-bottom: 3px dashed rgba(166,64,51,.25); }}
.lista li span {{ font-size: 30px; font-weight: 700; color: var(--verde); }}
.marco {{ border: 12px solid var(--crema); border-radius: 36px; overflow: hidden; box-shadow: 0 12px 30px rgba(0,0,0,.2); }}
"""


def pagina(cuerpo, ancho, alto, fondo="var(--crema)"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>'
            f'<body><div class="lienzo" style="width:{ancho}px;height:{alto}px;background:{fondo}">{cuerpo}</div></body></html>')


def sello():
    return f'<img class="sello" src="{LOGO}" alt="">'


# ---------------------------------------------------------------- Piezas

def carrusel_paletas():
    """Jue 5 nov · C. Educational · «Les paletas, 101»."""
    piezas = {}
    piezas["paletas-101-1-portada"] = pagina(f"""
      <img class="foto" src="{foto('paletas-fila')}" style="height:880px;object-position:50% 62%">
      <div class="picado"></div>
      <div class="pill">Le saviez-vous? · ¿Sabías que…?</div>
      <div class="panel" style="height:500px">
        <div class="titulo" style="font-size:132px">Les paletas,<br>101</div>
        <div class="puntos"></div>
        <div class="script" style="font-size:46px">Agua, chamoy o crema</div>
      </div>
      {sello()}""", *FEED)

    def lamina(n, color, fr, es, nota_fr, nota_es, sabores, foto_nombre, pos):
        filas = "".join(f"<li>{a}<span>{b}</span></li>" for a, b in sabores)
        return pagina(f"""
          <div style="position:absolute;inset:0 0 auto 0;height:14px;background:{color}"></div>
          <div style="position:absolute;left:64px;top:84px;font-family:'Lilita One';font-size:40px;color:{color}">{n} / 3</div>
          <div class="titulo" style="position:absolute;left:64px;top:140px;font-size:92px;color:{color}">{fr}</div>
          <div class="es" style="position:absolute;left:66px;top:248px;font-size:40px">{es}</div>
          <div style="position:absolute;left:66px;top:318px;width:600px;font-size:31px;line-height:1.35">{nota_fr}<br>
            <span class="es" style="font-size:27px">{nota_es}</span></div>
          <ul class="lista" style="position:absolute;left:64px;top:500px;width:560px">{filas}</ul>
          <div class="marco" style="position:absolute;right:-60px;top:420px;width:470px;height:640px;transform:rotate(3deg)">
            <img src="{foto(foto_nombre)}" style="width:100%;height:100%;object-fit:cover;object-position:{pos}"></div>
          {sello()}""", *FEED)

    piezas["paletas-101-2-agua"] = lamina(
        1, "var(--verde)", "À base d'eau", "Base de agua",
        "Fruitées et rafraîchissantes.", "Frutales y refrescantes.",
        [("Mangue", "Mango"), ("Fraise", "Fresa"), ("Tamarin", "Tamarindo"), ("Ananas", "Piña"), ("Lime", "Limón")],
        "paleta-verde", "45% 50%")
    piezas["paletas-101-3-chamoy"] = lamina(
        2, "var(--rojo)", "Avec chamoy", "Con chamoy",
        "Le chamoy : une sauce sucrée, salée et piquante.", "Dulce, saladito y enchilado.",
        [("Mangue", "Mango"), ("Ananas", "Piña"), ("Fraise", "Fresa"), ("Tamarin", "Tamarindo"), ("Lime", "Limón")],
        "paletas-colores", "60% 60%")
    crema = [("Coco", "Coco"), ("Fraise", "Fresa"), ("Rompope", "Rompope"), ("Pacane", "Nuez"), ("Pistache", "Pistache"),
             ("Vanille", "Vainilla"), ("Oreo", "Oreo"), ("Chocolat", "Chocolate"), ("Mangue", "Mango")]
    filas = "".join(f'<li style="font-size:38px;padding:9px 0">{a}<span>{b}</span></li>' for a, b in crema)
    piezas["paletas-101-4-crema"] = pagina(f"""
      <div style="position:absolute;inset:0 0 auto 0;height:14px;background:#c25a7c"></div>
      <div style="position:absolute;left:64px;top:84px;font-family:'Lilita One';font-size:40px;color:#c25a7c">3 / 3</div>
      <div class="titulo" style="position:absolute;left:64px;top:140px;font-size:92px;color:#b04a6c">À la crème</div>
      <div class="es" style="position:absolute;left:66px;top:248px;font-size:40px">Base de crema</div>
      <div style="position:absolute;left:66px;top:318px;width:900px;font-size:31px;line-height:1.35">Onctueuses, comme une crème glacée sur bâton.<br>
        <span class="es" style="font-size:27px">Cremositas, para los golosos.</span></div>
      <ul class="lista" style="position:absolute;left:64px;top:470px;width:520px">{filas}</ul>
      <div class="marco" style="position:absolute;right:-50px;top:470px;width:450px;height:600px;transform:rotate(-3deg)">
        <img src="{foto('paletas-sobre-congelador')}" style="width:100%;height:100%;object-fit:cover;object-position:35% 50%"></div>
      {sello()}""", *FEED, fondo="var(--rosa-claro)")
    piezas["paletas-101-5-cierre"] = pagina(f"""
      <img class="foto" src="{foto('paletas-acomodadas')}" style="object-position:55% 50%">
      <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,0) 35%,rgba(122,46,36,.92) 75%)"></div>
      <div style="position:absolute;left:64px;right:64px;bottom:96px;z-index:2;color:var(--crema)">
        <div class="titulo" style="color:var(--crema);font-size:104px">Laquelle<br>tu essaies?</div>
        <div style="font-size:44px;font-weight:800;margin:14px 0 30px;color:var(--rosa)">¿Cuál vas a probar?</div>
        <div style="font-size:30px;font-weight:700">{DIRECCION}<br>{HORARIO_FR}</div>
      </div>
      {sello()}""", *FEED)
    return piezas


def carrusel_conchas():
    """Jue 12 nov · D. Engagement · «Laquelle en premier?»."""
    panes = [("concha-con-leche", "62% 70%", "Concha", "classique · clásica"),
             ("concha-rosa", "35% 40%", "Concha rose", "concha de color"),
             ("pan-de-muerto-concha", "50% 45%", "Pan de muerto", "con cubierta de concha")]
    piezas = {}
    tiras = "".join(f'<div class="marco" style="flex:1;height:620px;transform:rotate({r}deg)">'
                    f'<img src="{foto(n)}" style="width:100%;height:100%;object-fit:cover;object-position:{p}"></div>'
                    for (n, p, _, _), r in zip(panes, (-3, 1.5, -1)))
    piezas["conchas-1-portada"] = pagina(f"""
      <div class="picado"></div>
      <div class="pill" style="background:var(--rojo)">Vote · Vota</div>
      <div class="titulo" style="position:absolute;left:64px;top:230px;font-size:120px">Laquelle<br>en premier?</div>
      <div class="es" style="position:absolute;left:68px;top:500px;font-size:48px">¿Cuál agarras primero?</div>
      <div style="position:absolute;left:44px;right:44px;top:610px;display:flex;gap:26px">{tiras}</div>
      {sello()}""", *FEED, fondo="var(--rosa)")
    for i, (n, p, fr, es) in enumerate(panes, start=1):
        piezas[f"conchas-{i + 1}-opcion-{i}"] = pagina(f"""
          <img class="foto" src="{foto(n)}" style="object-position:{p}">
          <div class="numero">{i}</div>
          <div class="etiqueta"><div class="titulo" style="font-size:64px">{fr}</div>
            <div class="es" style="font-size:32px">{es}</div></div>
          {sello()}""", *FEED)
    piezas["conchas-5-cierre"] = pagina(f"""
      <div class="picado"></div>
      <div style="position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:0 80px">
        <div class="script" style="font-size:52px">Ton café t'attend</div>
        <div class="titulo" style="font-size:118px;margin:20px 0">Commente<br>1, 2 ou 3</div>
        <div class="es" style="font-size:46px">Comenta tu número</div>
        <div class="puntos" style="margin:40px auto"></div>
        <div class="datos">Résultats vendredi en story · Resultados el viernes</div>
      </div>
      {sello()}""", *FEED, fondo="var(--crema)")
    return piezas


def livraison():
    """Jue 19 nov · E. Promotional · «On livre!»."""
    def cuerpo(alto_foto, tam):
        return f"""
          <img class="foto" src="{foto('tienda-mostrador')}" style="height:{alto_foto}px;object-position:50% 60%">
          <div class="picado"></div>
          <div class="pill">Livraison · A domicilio</div>
          <div class="panel" style="top:{alto_foto - 40}px;border-radius:40px 40px 0 0">
            <div class="titulo" style="font-size:{tam}px">On livre!</div>
            <div class="es" style="font-size:{int(tam * .42)}px;margin-top:6px">¡Te lo llevamos! · We deliver!</div>
            <div class="puntos"></div>
            <div style="font-size:30px;font-weight:700;margin-bottom:10px">Appelle-nous · Llámanos</div>
            <div class="titulo" style="font-size:{int(tam * .9)}px;color:var(--rojo-oscuro)">{TELEFONO}</div>
            <div class="datos" style="margin-top:22px">{HORARIO_FR}<br>{DIRECCION}</div>
          </div>
          {sello()}"""
    return {
        "livraison-feed": pagina(cuerpo(660, 116), *FEED),
        "livraison-historia": pagina(cuerpo(860, 150), *HISTORIA),
    }


def sueltas():
    """Banco: publicaciones de una sola foto."""
    def suelta(nombre_foto, pos, pill, titulo, es, color_pill="var(--verde)", alto=900):
        return pagina(f"""
          <img class="foto" src="{foto(nombre_foto)}" style="height:{alto}px;object-position:{pos}">
          <div class="pill" style="background:{color_pill}">{pill}</div>
          <div class="panel" style="top:{alto - 40}px;border-radius:40px 40px 0 0">
            <div class="titulo" style="font-size:70px">{titulo}</div>
            <div class="es" style="font-size:36px;margin-top:12px">{es}</div>
          </div>
          {sello()}""", *FEED)

    return {
        "nostalgia-gansito": suelta("gansito-marias", "40% 70%", "Nostalgia",
                                    "Si comiste esto de niño,<br>eres de los nuestros",
                                    "Les collations de notre enfance sont ici.", "var(--rojo)"),
        "nostalgia-carrito": suelta("carrito-paletero", "60% 40%", "Nostalgia",
                                    "El carrito paletero<br>también emigró",
                                    "Au Mexique, le chariot à paletas passe dans la rue.", "var(--rojo)"),
        "nostalgia-fabuloso": suelta("hogar-limpieza", "55% 45%", "Nostalgia",
                                     "Si tu casa olía a Fabuloso<br>los sábados…",
                                     "Les incontournables d'une maison mexicaine.", "var(--rojo)"),
        "tamales": pagina(f"""
          <img class="foto" src="{foto('tamal')}" style="object-position:50% 4%">
          <div class="pill" style="top:auto;bottom:64px">Tamales · Appelle pour réserver · {TELEFONO}</div>""", *FEED),
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
