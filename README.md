# Portafolio FESNA — Nicolás Bolivar

Portafolio web estático, adaptable y sin dependencias externas. Los archivos de publicación están separados dentro de `web/`.

El examen final amplía el portafolio a **cuatro programas FESNA** (Administración de Empresas, Contaduría Pública, Ingeniería de Sistemas y Marketing y Publicidad), con 24 productos asignados, 6 productos interactivos y el catálogo SNIES verificado.

## Estructura

```text
web/
├── index.html            (sitio ampliado: + sección #interactivos, 12 tarjetas y 24 slots)
├── styles.css
├── app.js                (filtros + 6 widgets interactivos con reglas locales)
├── media-links.json      (24 productos)
├── media/
│   ├── audio/
│   │   └── voz/          (segmentos TTSMaker del examen final)
│   ├── video/
│   ├── infografias/
│   └── README.md
└── entregables/
    ├── guiones-prototipo.md        (+ sección "Examen final" con textos TTSMaker)
    └── bitacora-produccion.html    (24 productos: 01-24)
.github/workflows/deploy-pages.yml
scripts/
├── render_media.py              (piezas originales, segundo corte)
├── render_refreshed_media.py    (animaciones renovadas)
├── render_final_media.py        (examen final: IS + MKT)
├── render_final_audio.py        (mezcla de los 2 podcasts IS por segmentos)
├── check-media-links.mjs        (validador de 24 slots)
└── media-requirements.txt
iNSTRUCCIONES DE NUEVAS MEJORAS/
└── EXAMEN_FINAL.pdf
EXAMEN_SEGUNDO_CORTE.pdf
captura-portafolio-opera-gx.png
captura-actividades-opera-gx.png
captura-productos-opera-gx.png
captura-descargas-drive-opera-gx.png
captura-voz-ia-opera-gx.png
captura-dialogo-ttsmaker-opera-gx.png
captura-cuna-ttsmaker-opera-gx.png
captura-conoce-ttsmaker-opera-gx.png
captura-podcast-profesional-ttsmaker-opera-gx.png
captura-productos-movil-edge.png
```

## Abrir localmente

Abre `web/index.html` en un navegador (o sirve la carpeta con `python -m http.server` desde `web/`). La búsqueda y los filtros del catálogo funcionan con JavaScript local; los 6 widgets interactivos son HTML/CSS/JS propio sin servicios externos.

## Publicación gratuita

El workflow `.github/workflows/deploy-pages.yml` publica automáticamente `web/` en GitHub Pages al hacer push a `main`. El repositorio ya está configurado para desplegar mediante GitHub Actions. La dirección del sitio es:

https://supelanopro387.github.io/Fredy-Parcial/

Los siguientes pushes a `main` actualizan el sitio.

## Antes de entregar el examen

1. La campaña cubre los cuatro programas de la guía por sus tres ciclos propedéuticos (12 tarjetas de asignación y 24 productos: los 12 del segundo corte más las 12 nuevas piezas del examen final). Nicolás estudia Ingeniería de Sistemas; ese dato identifica al estudiante, no el tema de campaña.
2. Los MP4, MP3 y las PNG exportados están en `web/media/`; los guiones, prompts, transcripciones y textos TTSMaker están en `web/entregables/guiones-prototipo.md`; el proceso, las herramientas y las soluciones por producto están en `web/entregables/bitacora-produccion.html`.
3. Los enlaces directos a los medios están cargados en `web/media-links.json`. Solo agrega `driveFolderUrl` si además te piden una carpeta compartida de Drive.
4. Verifica nombres, SNIES, fuentes, identidades visuales, prompts y herramientas; revisa el sitio en computador y celular.
5. La guía del examen indica que la entrega debe realizarse presencialmente.

## Pendiente manual del estudiante (voces TTSMaker)

- **3 narraciones de video de Ingeniería de Sistemas:** copia cada texto de la sección "Examen final" de `web/entregables/guiones-prototipo.md` en [TTSMaker](https://ttsmaker.com/es), descarga el MP3 y guárdalo en `web/media/audio/voz/` como `isn-tp-reels-narracion.mp3`, `isn-tec-video-narracion.mp3` e `isn-pro-solucion-narracion.mp3`. Luego re-ejecuta `python scripts/render_final_media.py` para incrustar las voces en los videos.
- **2 podcasts de IS por segmentos:** genera los 8 segmentos del podcast técnico (`isn-tec-podcast-01…08.mp3`) y los 6 del prospectivo (`isn-pro-podcast-01…06.mp3`) en `web/media/audio/voz/` (Santiago = voz masculina, Valeria = voz femenina; ambos personajes ficticios rotulados). Ejecuta `python scripts/render_final_audio.py` y los episodios finales se concatenan automáticamente en `web/media/audio/`.

Para volver a renderizar los medios, instala `scripts/media-requirements.txt` con Python. Ejecuta `python scripts/render_media.py` para las piezas originales, `python scripts/render_refreshed_media.py` para las dos animaciones y mezclas radiales renovadas, y `python scripts/render_final_media.py` / `python scripts/render_final_audio.py` para las piezas del examen final. Se usaron TTS.ai, TTSMaker, Pillow y FFmpeg (instalado vía `imageio-ffmpeg`); las voces son sintéticas y los podcasts son diálogos de dos voces ficticias.

Valida los 24 enlaces y sus archivos locales con `node scripts/check-media-links.mjs`.

Las ilustraciones de la página se implementan con HTML/CSS/SVG con asistencia de IA. No se usan fotografías externas ni se reutiliza el archivo del logotipo institucional.
