// Casa Chelito — solo lo que necesita JavaScript: menú móvil y recordar el idioma.
(function () {
  var boton = document.querySelector(".boton-menu");
  var nav = document.getElementById("navegacion");

  if (boton && nav) {
    boton.addEventListener("click", function () {
      var abierto = boton.getAttribute("aria-expanded") === "true";
      boton.setAttribute("aria-expanded", String(!abierto));
      nav.classList.toggle("abierta", !abierto);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("abierta")) {
        boton.setAttribute("aria-expanded", "false");
        nav.classList.remove("abierta");
        boton.focus();
      }
    });
  }

  // Guarda el idioma para que la página principal lo recuerde.
  try { localStorage.setItem("idioma", document.documentElement.lang); } catch (e) {}
})();
