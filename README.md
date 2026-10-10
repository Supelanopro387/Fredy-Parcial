# Portafolio FESNA — Nicolás Boulevard

Portafolio web estático, adaptable y sin dependencias externas. Los archivos de publicación están separados dentro de `web/`.

## Estructura

```text
web/
├── index.html
├── styles.css
├── app.js
├── media-links.json
└── entregables/
    └── guiones-prototipo.md
.github/workflows/deploy-pages.yml
EXAMEN_SEGUNDO_CORTE.pdf
captura-portafolio-opera-gx.png
captura-actividades-opera-gx.png
captura-productos-opera-gx.png
captura-descargas-drive-opera-gx.png
```

## Abrir localmente

Abre `web/index.html` en un navegador. La búsqueda y los filtros del catálogo funcionan con JavaScript local.

## Publicación gratuita

El workflow `.github/workflows/deploy-pages.yml` publica automáticamente `web/` en GitHub Pages al hacer push a `main`. El repositorio ya está configurado para desplegar mediante GitHub Actions. La dirección del sitio es:

https://supelanopro387.github.io/Fredy-Parcial/

Los siguientes pushes a `main` actualizan el sitio.

## Antes de entregar el examen

1. La campaña se centra en **Administración de Empresas** y **Contaduría Pública**, con los tres ciclos propedéuticos de cada programa. Nicolás estudia Ingeniería de Sistemas en FESNA; ese dato identifica al estudiante, no el tema de campaña.
2. Las seis tarjetas contienen borradores de guiones/storyboards para los productos de la consigna; no son archivos finales de video, audio o animación.
3. Al exportar cada pieza, pega su enlace HTTPS en `web/media-links.json`, en el espacio con su identificador; pega también el enlace de la carpeta compartida de Drive en `driveFolderUrl`.
4. El chatbot local Fesnando define el cuatrimestre como un periodo de cuatro meses. El descanso de una semana entre periodos proviene de la información aportada por Nicolás y debe validarse con el calendario académico vigente.
5. Verifica SNIES, fuentes, créditos visuales, prompts y herramientas utilizadas; revisa el sitio en computador y celular.
6. La guía del examen indica que la entrega debe realizarse presencialmente.

Las ilustraciones de la página se implementan con HTML/CSS/SVG con asistencia de IA. No se usan fotografías externas ni se reutiliza el archivo del logotipo institucional.
