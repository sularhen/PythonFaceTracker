# FaceTrail

![FaceTrail banner](assets/banner.svg)

FaceTrail is a cross-platform tool for face extraction, clustering, visual reports, and privacy-safe media exports. It can scan a single file or a whole folder, save face crops automatically, group similar detections, create blurred copies for sharing, and now also offers a local desktop GUI for people who do not want to work from the terminal.

## Why this is useful

- Review who appears across a media folder without scrubbing files manually.
- Keep the sharpest crop of repeated face-like appearances.
- Generate HTML, JSON, and CSV outputs for audits, curation, or local datasets.
- Create privacy-safe exports before sharing footage publicly.
- Let non-technical users run the full pipeline from a desktop window.

## Features

- Works with single images, folders, and videos.
- Uses OpenCV bundled Haar cascades automatically.
- Extracts face crops and scores sharpness.
- Clusters similar detections into reusable groups.
- Exports `gallery.html`, `summary.json`, and `detections.csv`.
- Saves blurred privacy-safe image or video copies.
- Includes a desktop GUI with file pickers and one-click scan flow.
- Can open the final report automatically in the browser.

## Installation

Linux and macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

## Fastest ways to use it

Terminal scan:

```bash
facetrail scan ./media --output ./output --save-redacted --open-report
```

Desktop GUI:

```bash
facetrail gui
```

or:

```bash
facetrail-gui
```

## GUI flow

Run the GUI with:

```bash
facetrail gui
```

Then the app will let you:

1. choose an image, video, or folder
2. choose what you want FaceTrail to do
3. press Start Scan
4. get the result inside a dedicated output folder for that choice

Available actions in the GUI:

- `Extract faces + report`
- `Blur faces in the original media`
- `Full workspace: crops + report + blurred exports`

## What the GUI adds

- Choose files or folders with buttons instead of typing paths.
- Pick the output folder visually.
- Choose the exact result type before scanning.
- Start the full scan with one click.
- Open the generated report again from the same window.

## Output structure

- `output/extract_faces_YYYYMMDD-HHMMSS/`: face crops plus report files.
- `output/privacy_blur_YYYYMMDD-HHMMSS/`: blurred image or video output.
- `output/full_workspace_YYYYMMDD-HHMMSS/`: crops, blurred copies, and report files.

Inside report-enabled modes:

- `faces/`: extracted face crops.
- `report/gallery.html`: visual review report.
- `report/summary.json`: machine-readable summary.
- `report/detections.csv`: spreadsheet-friendly manifest.

Inside blur-enabled modes:

- `redacted/`: privacy-safe image or video exports.

## Command reference

```text
facetrail scan INPUT [--output OUTPUT] [--sample-every N] [--min-face-size PX] [--cluster-threshold FLOAT] [--save-redacted] [--open-report]
facetrail gui [--start-input PATH]
facetrail-gui
```

Recommended defaults:

- `--sample-every 5` for balanced speed on videos.
- `--min-face-size 64` for everyday phone and webcam footage.
- `--cluster-threshold 0.92` for conservative grouping.

## Release packages

This repository includes a release packer that generates:

- `dist/facetrail-windows-vX.Y.Z.zip`
- `dist/facetrail-linux-vX.Y.Z.tar.gz`

Build them with:

```bash
python scripts/build_release.py
```

## Practical use cases

- Privacy pass before sending event footage to clients or friends.
- Media triage for creators, journalists, and researchers.
- Local photo review to find repeated people quickly.
- Lightweight preparation step before a more advanced vision pipeline.

## Limitations

- Clustering is appearance-based and lightweight. It is not a biometric identity system.
- Haar cascades are fast and portable, but they are not state-of-the-art detectors.
- Performance depends on lighting, face angle, and source quality.
- The desktop GUI uses Tkinter, which is included in most Python installs but can be missing in minimal Linux environments.

---

# FaceTrail en Espanol

![FaceTrail banner](assets/banner.svg)

FaceTrail es una herramienta multiplataforma para extraer rostros, agrupar apariciones similares, generar reportes visuales y exportar copias anonimizadas. Puede analizar un archivo o una carpeta completa, guardar recortes automaticamente, agrupar detecciones parecidas, crear copias con desenfoque para compartir y ahora tambien incluye una interfaz de escritorio para personas que no quieren usar terminal.

## Por que es util

- Permite revisar quien aparece en una carpeta multimedia sin inspeccionar archivo por archivo.
- Conserva la mejor captura de apariciones repetidas segun nitidez.
- Genera salidas HTML, JSON y CSV para auditorias, curacion o datasets locales.
- Crea exportaciones anonimizadas antes de compartir material.
- Permite que personas no tecnicas ejecuten todo desde una ventana local.

## Funciones

- Funciona con imagenes individuales, carpetas y videos.
- Usa automaticamente las Haar cascades incluidas con OpenCV.
- Extrae recortes de rostros y mide nitidez.
- Agrupa detecciones similares en clusters reutilizables.
- Exporta `gallery.html`, `summary.json` y `detections.csv`.
- Guarda copias de imagen o video con desenfoque facial.
- Incluye una GUI de escritorio con selectores y flujo de un clic.
- Puede abrir automaticamente el reporte final en el navegador.

## Instalacion

Linux y macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

## Formas mas rapidas de usarlo

Analisis por terminal:

```bash
facetrail scan ./media --output ./output --save-redacted --open-report
```

GUI de escritorio:

```bash
facetrail gui
```

o:

```bash
facetrail-gui
```

## Flujo de la GUI

Ejecuta la GUI con:

```bash
facetrail gui
```

Luego la aplicacion te deja:

1. elegir una imagen, video o carpeta
2. elegir que quieres que haga FaceTrail
3. pulsar `Start Scan`
4. recibir el resultado dentro de una carpeta dedicada a esa eleccion

Acciones disponibles en la GUI:

- `Extract faces + report`
- `Blur faces in the original media`
- `Full workspace: crops + report + blurred exports`

## Que agrega la GUI

- Elegir archivos o carpetas con botones en vez de escribir rutas.
- Elegir visualmente la carpeta de salida.
- Elegir el tipo exacto de resultado antes de analizar.
- Iniciar todo el analisis con un clic.
- Reabrir el reporte desde la misma ventana.

## Estructura de salida

- `output/extract_faces_YYYYMMDD-HHMMSS/`: recortes de rostros y archivos de reporte.
- `output/privacy_blur_YYYYMMDD-HHMMSS/`: imagenes o videos anonimizados.
- `output/full_workspace_YYYYMMDD-HHMMSS/`: recortes, exportaciones difuminadas y reporte.

Dentro de los modos con reporte:

- `faces/`: recortes de rostros detectados.
- `report/gallery.html`: reporte visual.
- `report/summary.json`: resumen legible por maquinas.
- `report/detections.csv`: manifiesto facil de abrir en Excel o similares.

Dentro de los modos con anonimizado:

- `redacted/`: exportaciones seguras para compartir.

## Referencia de comandos

```text
facetrail scan INPUT [--output OUTPUT] [--sample-every N] [--min-face-size PX] [--cluster-threshold FLOAT] [--save-redacted] [--open-report]
facetrail gui [--start-input PATH]
facetrail-gui
```

Valores recomendados:

- `--sample-every 5` para equilibrar velocidad en videos.
- `--min-face-size 64` para metraje comun de webcam o celular.
- `--cluster-threshold 0.92` para agrupamiento conservador.

## Paquetes de release

Este repositorio incluye un empaquetador que genera:

- `dist/facetrail-windows-vX.Y.Z.zip`
- `dist/facetrail-linux-vX.Y.Z.tar.gz`

Se generan con:

```bash
python scripts/build_release.py
```

## Casos de uso

- Primera pasada de privacidad antes de entregar videos a clientes o amigos.
- Triaje de material para creadores, periodistas o investigadores.
- Revision local de fotos para encontrar personas repetidas rapidamente.
- Paso liviano previo a un pipeline de vision mas avanzado.

## Limitaciones

- El agrupamiento es ligero y basado en apariencia. No pretende ser biometria.
- Haar cascades es rapido y portable, pero no representa el estado del arte.
- El rendimiento depende de la iluminacion, el angulo facial y la calidad del material.
- La GUI de escritorio usa Tkinter, que suele venir con Python, pero puede faltar en instalaciones minimas de Linux.
