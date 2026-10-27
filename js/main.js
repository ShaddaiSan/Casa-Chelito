// Encabezado, pie, cambio de idioma y menú móvil (compartidos por todas las páginas).
(function () {
  var N = window.NEGOCIO;
  var T = window.TRADUCCIONES;
  var IDIOMAS = ["es", "en", "fr"];
  var pagina = document.body.dataset.pagina;

  var paginas = [
    { id: "inicio", href: "index.html", clave: "nav.inicio" },
    { id: "pan", href: "pan.html", clave: "nav.pan" },
    { id: "paletas", href: "paletas.html", clave: "nav.paletas" },
    { id: "abarrotes", href: "abarrotes.html", clave: "nav.abarrotes" },
    { id: "contacto", href: "contacto.html", clave: "nav.contacto" }
  ];

  function enlaces() {
    return paginas.map(function (p) {
      var actual = p.id === pagina ? ' aria-current="page"' : "";
      return '<li><a href="' + p.href + '"' + actual + ' data-i18n="' + p.clave + '"></a></li>';
    }).join("");
  }

  var encabezado = document.getElementById("encabezado");
  if (encabezado) {
    encabezado.className = "encabezado";
    encabezado.innerHTML =
      '<div class="contenedor">' +
        '<a class="marca" href="index.html"><img src="assets/logo.png" alt="" width="56" height="56"><span>Casa Chelito</span></a>' +
        '<button class="boton-menu" type="button" aria-expanded="false" data-i18n-aria="nav.abrir">☰</button>' +
        '<nav class="navegacion">' +
          '<ul class="menu">' + enlaces() + '</ul>' +
          '<div class="idiomas" role="group" aria-label="Language">' +
            IDIOMAS.map(function (l) {
              return '<button type="button" data-idioma="' + l + '">' + l.toUpperCase() + '</button>';
            }).join("") +
          '</div>' +
        '</nav>' +
      '</div>';
  }

  var pie = document.getElementById("pie");
  if (pie) {
    pie.className = "pie";
    pie.innerHTML =
      '<div class="contenedor">' +
        '<div><h3>Casa Chelito</h3><p data-i18n="pie.texto"></p></div>' +
        '<div><h3 data-i18n="pie.paginas"></h3><ul>' + enlaces() + '</ul></div>' +
        '<div><h3 data-i18n="pie.contacto"></h3><ul>' +
          '<li>📞 <a href="tel:' + N.telefonoLink + '">' + N.telefono + '</a></li>' +
          '<li>📍 ' + N.direccion + '</li>' +
          (N.instagram ? '<li><a href="' + N.instagram + '">Instagram</a></li>' : "") +
          (N.facebook ? '<li><a href="' + N.facebook + '">Facebook</a></li>' : "") +
        '</ul></div>' +
        '<p class="derechos">© ' + new Date().getFullYear() + ' Casa Chelito · <span data-i18n="pie.derechos"></span></p>' +
      '</div>';
  }

  // Botón flotante para llamar en móvil
  var flotante = document.createElement("a");
  flotante.className = "llamar-flotante";
  flotante.href = "tel:" + N.telefonoLink;
  flotante.textContent = "📞";
  flotante.setAttribute("data-i18n-aria", "llamar");
  document.body.appendChild(flotante);

  // Teléfono, dirección y mapa en cualquier página
  document.querySelectorAll("[data-telefono]").forEach(function (el) {
    el.textContent = N.telefono;
    if (el.tagName === "A") el.href = "tel:" + N.telefonoLink;
  });
  document.querySelectorAll("[data-tel-link]").forEach(function (el) {
    el.href = "tel:" + N.telefonoLink;
  });
  document.querySelectorAll("[data-direccion]").forEach(function (el) {
    el.textContent = N.direccion;
  });
  document.querySelectorAll("[data-mapa]").forEach(function (el) {
    el.src = N.mapa;
  });

  // ----- Idioma -----
  function leerIdioma() {
    try {
      var guardado = localStorage.getItem("idioma");
      if (IDIOMAS.indexOf(guardado) !== -1) return guardado;
    } catch (e) {}
    var nav = (navigator.language || "fr").slice(0, 2);
    return IDIOMAS.indexOf(nav) !== -1 ? nav : "fr";
  }

  function aplicarIdioma(idioma) {
    var dic = T[idioma];
    document.documentElement.lang = idioma;
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var texto = dic[el.dataset.i18n];
      if (texto !== undefined) el.textContent = texto;
    });
    document.querySelectorAll("[data-i18n-aria]").forEach(function (el) {
      var texto = dic[el.dataset.i18nAria];
      if (texto !== undefined) el.setAttribute("aria-label", texto);
    });
    var titulo = document.body.dataset.titulo;
    document.title = (titulo && dic[titulo] ? dic[titulo] + " · " : "") + dic["meta.titulo"];
    document.querySelectorAll("[data-idioma]").forEach(function (b) {
      b.setAttribute("aria-pressed", b.dataset.idioma === idioma ? "true" : "false");
    });
    try { localStorage.setItem("idioma", idioma); } catch (e) {}
  }

  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-idioma]");
    if (b) aplicarIdioma(b.dataset.idioma);
  });

  // ----- Menú móvil -----
  var botonMenu = document.querySelector(".boton-menu");
  if (botonMenu) {
    botonMenu.addEventListener("click", function () {
      var nav = document.querySelector(".navegacion");
      var abierta = nav.classList.toggle("abierta");
      botonMenu.setAttribute("aria-expanded", abierta ? "true" : "false");
    });
  }

  aplicarIdioma(leerIdioma());
})();
