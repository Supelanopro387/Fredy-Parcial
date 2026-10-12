# Portafolio FESNA — Nicolás Boulevard

Portafolio web estático, adaptable y sin dependencias externas. Los archivos de publicación están separados dentro de `web/`.

## Estructura

```text
web/
├── index.html
├── styles.css
├── app.js
├── media-links.json
├── media/
│   ├── audio/
│   │   └── voz/
│   ├── video/
│   ├── infografias/
│   └── README.md
└── entregables/
    ├── guiones-prototipo.md
    └── bitacora-produccion.html
.github/workflows/deploy-pages.yml
scripts/render_media.py
scripts/check-media-links.mjs
scripts/media-requirements.txt
EXAMEN_SEGUNDO_CORTE.pdf
captura-portafolio-opera-gx.png
captura-actividades-opera-gx.png
captura-productos-opera-gx.png
captura-descargas-drive-opera-gx.png
captura-voz-ia-opera-gx.png
```

## Abrir localmente

Abre `web/index.html` en un navegador. La búsqueda y los filtros del catálogo funcionan con JavaScript local.

## Publicación gratuita

El workflow `.github/workflows/deploy-pages.yml` publica automáticamente `web/` en GitHub Pages al hacer push a `main`. El repositorio ya está configurado para desplegar mediante GitHub Actions. La dirección del sitio es:

https://supelanopro387.github.io/Fredy-Parcial/

Los siguientes pushes a `main` actualizan el sitio.

## Antes de entregar el examen

1. La campaña se centra en **Administración de Empresas** y **Contaduría Pública**, con los tres ciclos propedéuticos de cada programa. Nicolás estudia Ingeniería de Sistemas en FESNA; ese dato identifica al estudiante, no el tema de campaña.
2. Los MP4, MP3 y la infografía PNG exportados están en `web/media/`; los guiones, prompts y transcripciones están en `web/entregables/guiones-prototipo.md`; el proceso, las herramientas y las soluciones por producto están en `web/entregables/bitacora-produccion.html`.
3. Los enlaces directos a los medios están cargados en `web/media-links.json`. Solo agrega `driveFolderUrl` si además te piden una carpeta compartida de Drive.
4. Verifica nombres, SNIES, fuentes, créditos visuales, prompts y herramientas; revisa el sitio en computador y celular.
5. La guía del examen indica que la entrega debe realizarse presencialmente.

Para volver a renderizar los medios, instala `scripts/media-requirements.txt` con Python y ejecuta `python scripts/render_media.py`. Los MP3 de voz sintética fuente están en `web/media/audio/voz/`; TTS.ai, Pillow y FFmpeg se usaron para generar y exportar los productos.

Valida los 12 enlaces y sus archivos locales con `node scripts/check-media-links.mjs`.

Las ilustraciones de la página se implementan con HTML/CSS/SVG con asistencia de IA. No se usan fotografías externas ni se reutiliza el archivo del logotipo institucional.
