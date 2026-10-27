#!/usr/bin/env python3
"""Genera el sitio estático de Casa Chelito en docs/ (carpeta que publica GitHub Pages).

Uso:  python3 tools/build.py

- Páginas: src/pages/*.html  (contenido)  +  src/partials/*.html  (encabezado, pie…)
- Textos:  src/i18n/{es,en,fr}.json  →  se genera una copia de cada página por idioma
- Datos:   src/config.json  (teléfono, dirección, mapa…)
- Fotos:   src/images/*  →  docs/assets/img en AVIF, WebP y JPEG a varios tamaños

Marcas en las plantillas:
  {{t.clave}}            texto traducido
  {{c.clave}}            dato de config.json
  {{base}}               ruta relativa a la raíz del sitio ("../" dentro de /es/)
  {{lang}}               idioma actual
  {{> parcial}}          inserta src/partials/parcial.html
  {{img nombre alt=clave sizes="…" class="…" eager}}   imagen responsiva
"""
import html
import json
import re
import shutil
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
SRC = RAIZ / "src"
OUT = RAIZ / "docs"
IDIOMAS = ["es", "en", "fr"]
NOMBRES_IDIOMA = {"es": "Español", "en": "English", "fr": "Français"}
LOCALES = {"es": "es_MX", "en": "en_CA", "fr": "fr_CA"}
ANCHOS = [400, 800, 1200, 1600]

PAGINAS = [
    # id, archivo, clave del título, clave de la descripción, mostrar banda de pedido
    ("inicio", "index.html", None, "meta.descInicio", True),
    ("pan", "pan.html", "nav.pan", "meta.descPan", True),
    ("paletas", "paletas.html", "nav.paletas", "meta.descPaletas", True),
    ("abarrotes", "abarrotes.html", "nav.abarrotes", "meta.descAbarrotes", True),
    ("contacto", "contacto.html", "nav.contacto", "meta.descContacto", False),
]

CONFIG = json.loads((SRC / "config.json").read_text())
TEXTOS = {l: json.loads((SRC / "i18n" / f"{l}.json").read_text()) for l in IDIOMAS}


# ---------- Imágenes ----------

DIMENSIONES = {}


def optimizar_imagenes():
    destino = OUT / "assets" / "img"
    destino.mkdir(parents=True, exist_ok=True)
    archivo_ajustes = SRC / "images" / "ajustes.json"
    ajustes = json.loads(archivo_ajustes.read_text()) if archivo_ajustes.exists() else {}
    for origen in sorted((SRC / "images").iterdir()):
        if origen.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
            continue
        nombre = origen.stem
        im = ImageOps.exif_transpose(Image.open(origen))
        if nombre == "logo":
            generar_logo(im, destino)
            continue
        im = im.convert("RGB")
        ajuste = ajustes.get(nombre, {})
        if "recorte" in ajuste:
            im = im.crop(tuple(ajuste["recorte"]))
        if "brillo" in ajuste:
            im = ImageEnhance.Brightness(im).enhance(ajuste["brillo"])
        if "contraste" in ajuste:
            im = ImageEnhance.Contrast(im).enhance(ajuste["contraste"])
        DIMENSIONES[nombre] = im.size
        for ancho in anchos_para(im.width):
            salidas = {fmt: destino / f"{nombre}-{ancho}.{fmt}" for fmt in ("avif", "webp", "jpg")}
            mas_reciente = max(origen.stat().st_mtime, archivo_ajustes.stat().st_mtime if ajuste else 0)
            if all(s.exists() and s.stat().st_mtime > mas_reciente for s in salidas.values()):
                continue
            alto = round(im.height * ancho / im.width)
            copia = im.resize((ancho, alto), Image.LANCZOS).filter(
                ImageFilter.UnsharpMask(radius=1, percent=60, threshold=2))
            copia.save(salidas["avif"], "AVIF", quality=60)
            copia.save(salidas["webp"], "WEBP", quality=80, method=6)
            copia.save(salidas["jpg"], "JPEG", quality=82, optimize=True, progressive=True)


def anchos_para(ancho_original):
    anchos = [a for a in ANCHOS if a < ancho_original]
    return anchos + [min(ancho_original, ANCHOS[-1])] if ancho_original <= ANCHOS[-1] else ANCHOS


def generar_logo(im, destino):
    im = im.convert("RGBA")
    for lado in (112, 240, 500):
        copia = im.resize((lado, lado), Image.LANCZOS)
        copia.save(destino / f"logo-{lado}.webp", "WEBP", quality=88, method=6)
        copia.save(destino / f"logo-{lado}.png", "PNG", optimize=True)
    im.resize((180, 180), Image.LANCZOS).save(OUT / "apple-touch-icon.png", optimize=True)
    im.resize((48, 48), Image.LANCZOS).save(OUT / "favicon.png", optimize=True)
    # Imagen para compartir en redes (1200×630)
    lienzo = Image.new("RGB", (1200, 630), (234, 210, 223))
    logo = im.resize((560, 560), Image.LANCZOS)
    lienzo.paste(logo, (320, 35), logo)
    lienzo.save(destino / "compartir.jpg", "JPEG", quality=85, optimize=True)


def imagen(nombre, lang, base, alt=None, sizes="100vw", clase="", eager=False):
    ancho, alto = DIMENSIONES[nombre]
    anchos = anchos_para(ancho)
    texto_alt = html.escape(TEXTOS[lang][alt]) if alt else ""

    def srcset(fmt):
        return ", ".join(f"{base}assets/img/{nombre}-{a}.{fmt} {a}w" for a in anchos)

    medio = next((a for a in anchos if a >= 800), anchos[-1])
    carga = 'fetchpriority="high"' if eager else 'loading="lazy"'
    clase_attr = f' class="{clase}"' if clase else ""
    return (
        f'<picture{clase_attr}>'
        f'<source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}">'
        f'<source type="image/webp" srcset="{srcset("webp")}" sizes="{sizes}">'
        f'<img src="{base}assets/img/{nombre}-{medio}.jpg" srcset="{srcset("jpg")}" sizes="{sizes}" '
        f'width="{ancho}" height="{alto}" alt="{texto_alt}" decoding="async" {carga}>'
        f'</picture>'
    )


# ---------- Plantillas ----------

RE_IMG = re.compile(r'\{\{img (\S+)((?:\s+\w+(?:="[^"]*"|=\S+)?)*)\s*\}\}')
RE_ATTR = re.compile(r'(\w+)(?:="([^"]*)"|=(\S+))?')


def renderizar(plantilla, lang, base, pagina):
    t = TEXTOS[lang]
    for _ in range(5):  # parciales anidados
        nueva = re.sub(r"\{\{> (\w+)\}\}", lambda m: (SRC / "partials" / f"{m.group(1)}.html").read_text(), plantilla)
        if nueva == plantilla:
            break
        plantilla = nueva

    def img(m):
        attrs = {k: (v1 or v2 or True) for k, v1, v2 in RE_ATTR.findall(m.group(2))}
        return imagen(m.group(1), lang, base, alt=attrs.get("alt"), sizes=attrs.get("sizes", "100vw"),
                      clase=attrs.get("class", ""), eager="eager" in attrs)

    plantilla = RE_IMG.sub(img, plantilla)

    def traducir(m):
        clave = m.group(1)
        if clave not in t:
            raise KeyError(f"Falta la traducción '{clave}' en {lang}.json")
        return html.escape(t[clave], quote=False)

    plantilla = re.sub(r"\{\{t\.([\w.]+)\}\}", traducir, plantilla)
    plantilla = re.sub(r"\{\{c\.(\w+)\}\}", lambda m: html.escape(str(CONFIG[m.group(1)])), plantilla)

    variables = {
        "lang": lang,
        "base": base,
        "locale": LOCALES[lang],
        "nav": menu(lang, pagina),
        "idiomas": selector_idiomas(lang, pagina),
        "hreflang": hreflang(pagina),
        "anio": "2026",
        "redes": redes(),
    }
    return re.sub(r"\{\{(\w+)\}\}", lambda m: variables.get(m.group(1), m.group(0)), plantilla)


def archivo_de(pagina_id):
    return next(p[1] for p in PAGINAS if p[0] == pagina_id)


def menu(lang, actual):
    items = []
    for pid, archivo, _, _, _ in PAGINAS:
        aria = ' aria-current="page"' if pid == actual else ""
        href = "./" if archivo == "index.html" else archivo
        items.append(f'<li><a href="{href}"{aria}>{html.escape(TEXTOS[lang]["nav." + pid])}</a></li>')
    return "\n".join(items)


def selector_idiomas(lang, pagina):
    archivo = "" if archivo_de(pagina) == "index.html" else archivo_de(pagina)
    enlaces = []
    for l in IDIOMAS:
        actual = ' aria-current="true"' if l == lang else ""
        enlaces.append(f'<a href="../{l}/{archivo}" hreflang="{l}" lang="{l}" data-idioma="{l}"{actual} '
                       f'title="{NOMBRES_IDIOMA[l]}">{l.upper()}</a>')
    return "".join(enlaces)


def url_absoluta(lang, pagina):
    archivo = archivo_de(pagina)
    return CONFIG["url"] + f"{lang}/" + ("" if archivo == "index.html" else archivo)


def hreflang(pagina):
    lineas = [f'<link rel="alternate" hreflang="{l}" href="{url_absoluta(l, pagina)}">' for l in IDIOMAS]
    lineas.append(f'<link rel="alternate" hreflang="x-default" href="{url_absoluta(CONFIG["idioma_por_defecto"], pagina)}">')
    return "\n  ".join(lineas)


ICONOS = {
    "instagram": '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="currentColor" d="M12 2.2c3.2 0 3.6 0 4.8.1 1.2.1 1.8.2 2.2.4.6.2 1 .5 1.4.9.4.4.7.8.9 1.4.2.4.4 1.1.4 2.2.1 1.3.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 1.2-.2 1.8-.4 2.2-.2.6-.5 1-.9 1.4-.4.4-.8.7-1.4.9-.4.2-1.1.4-2.2.4-1.3.1-1.6.1-4.8.1s-3.6 0-4.8-.1c-1.2-.1-1.8-.2-2.2-.4-.6-.2-1-.5-1.4-.9-.4-.4-.7-.8-.9-1.4-.2-.4-.4-1.1-.4-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8c.1-1.2.2-1.8.4-2.2.2-.6.5-1 .9-1.4.4-.4.8-.7 1.4-.9.4-.2 1.1-.4 2.2-.4C8.4 2.2 8.8 2.2 12 2.2zm0 1.8c-3.1 0-3.5 0-4.7.1-1 0-1.6.2-2 .3-.5.2-.8.4-1.2.8-.4.4-.6.7-.8 1.2-.1.4-.3.9-.3 2C3 9.5 3 9.9 3 12s0 3.5.1 4.7c0 1 .2 1.6.3 2 .2.5.4.8.8 1.2.4.4.7.6 1.2.8.4.1.9.3 2 .3 1.2.1 1.6.1 4.7.1s3.5 0 4.7-.1c1 0 1.6-.2 2-.3.5-.2.8-.4 1.2-.8.4-.4.6-.7.8-1.2.1-.4.3-.9.3-2 .1-1.2.1-1.6.1-4.7s0-3.5-.1-4.7c0-1-.2-1.6-.3-2-.2-.5-.4-.8-.8-1.2-.4-.4-.7-.6-1.2-.8-.4-.1-.9-.3-2-.3C15.5 4 15.1 4 12 4zm0 3.1a4.9 4.9 0 1 1 0 9.8 4.9 4.9 0 0 1 0-9.8zm0 8a3.1 3.1 0 1 0 0-6.2 3.1 3.1 0 0 0 0 6.2zm6.2-8.2a1.1 1.1 0 1 1-2.3 0 1.1 1.1 0 0 1 2.3 0z"/></svg>',
    "facebook": '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="currentColor" d="M22 12a10 10 0 1 0-11.6 9.9v-7H7.9V12h2.5V9.8c0-2.5 1.5-3.9 3.8-3.9 1.1 0 2.2.2 2.2.2v2.5h-1.3c-1.2 0-1.6.8-1.6 1.6V12h2.8l-.4 2.9h-2.3v7A10 10 0 0 0 22 12z"/></svg>',
}


def redes(clase=""):
    items = []
    for red in ("instagram", "facebook"):
        if CONFIG.get(red):
            items.append(f'<li><a class="red {red}" href="{html.escape(CONFIG[red])}" rel="noopener" target="_blank">'
                         f'{ICONOS[red]}<span>{red.capitalize()}</span></a></li>')
    return "".join(items)


def datos_estructurados(lang):
    datos = {
        "@context": "https://schema.org",
        "@type": ["GroceryStore", "Bakery"],
        "name": CONFIG["nombre"],
        "url": CONFIG["url"] + f"{lang}/",
        "image": CONFIG["url"] + "assets/img/logo-500.png",
        "description": TEXTOS[lang]["meta.descInicio"],
        "servesCuisine": "Mexican",
        "address": {"@type": "PostalAddress", "streetAddress": CONFIG["calle"],
                    "addressLocality": CONFIG["ciudad"], "addressRegion": CONFIG["region"],
                    "postalCode": CONFIG["codigo_postal"], "addressCountry": CONFIG["pais"]},
        "sameAs": [CONFIG[r] for r in ("facebook", "instagram") if CONFIG.get(r)],
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": dias, "opens": abre, "closes": cierra}
            for dias, abre, cierra in CONFIG["horario"]
        ],
    }
    if CONFIG["telefono_confirmado"]:
        datos["telephone"] = CONFIG["telefono_link"]
    return '<script type="application/ld+json">' + json.dumps(datos, ensure_ascii=False) + "</script>"


# ---------- Construcción ----------

def construir():
    for l in IDIOMAS:
        shutil.rmtree(OUT / l, ignore_errors=True)
    for carpeta in ("css", "js", "fonts"):
        shutil.rmtree(OUT / "assets" / carpeta, ignore_errors=True)
    OUT.mkdir(exist_ok=True)
    optimizar_imagenes()

    for carpeta in ("css", "js", "fonts"):
        shutil.copytree(SRC / carpeta, OUT / "assets" / carpeta)
    (OUT / ".nojekyll").write_text("")

    layout = (SRC / "partials" / "layout.html").read_text()
    for lang in IDIOMAS:
        (OUT / lang).mkdir(parents=True)
        t = TEXTOS[lang]
        for pid, archivo, clave_titulo, clave_desc, pedido in PAGINAS:
            titulo = (t[clave_titulo] + " · " if clave_titulo else "") + t["meta.titulo"]
            pagina = (layout
                      .replace("{{contenido}}", (SRC / "pages" / archivo).read_text())
                      .replace("{{pedido}}", "{{> pedido}}" if pedido else "")
                      .replace("{{titulo}}", html.escape(titulo))
                      .replace("{{descripcion}}", html.escape(t[clave_desc]))
                      .replace("{{canonica}}", url_absoluta(lang, pid))
                      .replace("{{jsonld}}", datos_estructurados(lang) if pid == "inicio" else "")
                      .replace("{{pagina}}", pid))
            (OUT / lang / archivo).write_text(renderizar(pagina, lang, "../", pid))

    # Raíz: elegir idioma (funciona sin JS; con JS redirige al idioma guardado o del navegador)
    raiz = renderizar((SRC / "partials" / "raiz.html").read_text(), CONFIG["idioma_por_defecto"], "", "inicio")
    (OUT / "index.html").write_text(raiz)
    (OUT / "404.html").write_text(renderizar((SRC / "partials" / "404.html").read_text(),
                                             CONFIG["idioma_por_defecto"], CONFIG["url"], "inicio"))

    urls = "\n".join(
        f"  <url><loc>{url_absoluta(l, pid)}</loc></url>" for l in IDIOMAS for pid, *_ in PAGINAS)
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "\n</urlset>\n")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {CONFIG['url']}sitemap.xml\n")

    # Borrar imágenes generadas que ya no tienen original
    nombres = set(DIMENSIONES) | {"logo", "compartir"}
    for f in (OUT / "assets" / "img").iterdir():
        if re.sub(r"-\d+$", "", f.stem) not in nombres:
            f.unlink()
    print(f"Listo: {len(PAGINAS) * len(IDIOMAS)} páginas en {OUT.relative_to(RAIZ)}/")


if __name__ == "__main__":
    construir()
