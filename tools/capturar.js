// Captura cada HTML de tools/redes.py como PNG del tamaño de su lienzo.
const { chromium } = require('playwright');

(async () => {
  const trabajos = JSON.parse(process.argv[2]);
  const navegador = await chromium.launch();
  const pagina = await navegador.newPage({ viewport: { width: 1080, height: 1920 } });
  for (const { html, png } of trabajos) {
    await pagina.goto(html, { waitUntil: 'load' });
    await pagina.evaluate(() => document.fonts.ready);
    await pagina.evaluate(() => window.ajustar && window.ajustar());
    await pagina.locator('.lienzo').screenshot({ path: png });
  }
  await navegador.close();
})();
