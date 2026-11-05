// Utilidades compartidas: voz en español, barajar y carga de datos.
const Aula = {
  voces: [],
  cargarVoces() {
    try { this.voces = speechSynthesis.getVoices().filter(v => v.lang && v.lang.startsWith('es')); } catch (e) {}
  },
  decir(texto) {
    try {
      speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(texto);
      u.lang = 'es-ES'; u.rate = 0.85;
      const v = this.voces.find(v => v.lang === 'es-ES') || this.voces[0];
      if (v) u.voice = v;
      speechSynthesis.speak(u);
    } catch (e) { /* sin voz: el juego sigue funcionando con texto */ }
  },
  barajar(lista) {
    const a = lista.slice();
    for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
    return a;
  },
  async datos() {
    const r = await fetch('datos.json');
    if (!r.ok) throw new Error('No se pudo cargar datos.json');
    return r.json();
  }
};
try { Aula.cargarVoces(); speechSynthesis.onvoiceschanged = () => Aula.cargarVoces(); } catch (e) {}
