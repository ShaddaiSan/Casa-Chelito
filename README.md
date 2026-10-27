# Casa Chelito

Sitio web de **Casa Chelito**, tiendita mexicana en Montreal: pan artesanal, paletas artesanales, abarrotes, bebidas y antojitos.
En español, inglés y francés. Sitio estático, sin frameworks ni dependencias en el navegador.

Publicado con GitHub Pages desde la carpeta `docs/`: https://shaddaisan.github.io/Casa-Chelito/

## Estructura

```
src/                 ← aquí se edita
  config.json        teléfono, dirección, mapa, redes
  i18n/es|en|fr.json textos en cada idioma
  pages/             contenido de cada página
  partials/          encabezado/pie (layout), banda de pedido, temporada, raíz, 404
  css/styles.css     diseño (colores del logo)
  js/main.js         solo menú móvil y recordar idioma
  fonts/             fuentes WOFF2 alojadas localmente
  images/            fotos originales
tools/build.py       genera el sitio
docs/                ← sitio generado (no editar a mano)
  es/ en/ fr/        páginas por idioma
  assets/            css, js, fuentes, imágenes optimizadas
  index.html         elige idioma (redirige al del navegador)
  sitemap.xml, robots.txt, 404.html
```

## Generar el sitio

```
pip install pillow   # solo para optimizar fotos
python3 tools/build.py
```

Cada foto en `src/images/` se convierte a AVIF, WebP y JPEG en 400, 800, 1200 y 1600 px,
y el navegador descarga solo el tamaño y formato que necesita.

## Notas

- Todo el texto y los enlaces están en el HTML: el sitio funciona sin JavaScript.
- Los pedidos a domicilio son solo por teléfono (no hace falta backend).
- Si `telefono_confirmado` es `true` en `config.json`, el teléfono se agrega a los datos para Google.
