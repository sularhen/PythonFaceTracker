# FaceTrail

![FaceTrail banner](assets/banner.svg)

FaceTrail is a cross-platform tool for face extraction, clustering, visual reports, and privacy-safe media exports. It can scan a single file or a whole folder, save face crops automatically, group similar detections, create blurred copies for sharing, and now offers a modern pro engine based on official OpenCV Zoo models plus a local desktop GUI with preview and ZIP export for people who do not want to work from the terminal.

## Why this is useful

- Review who appears across a media folder without scrubbing files manually.
- Keep only the sharpest crop of each repeated face-like appearance.
- Generate HTML, JSON, and CSV outputs for audits, curation, or local datasets.
- Create privacy-safe exports before sharing footage publicly.
- Let non-technical users run the full pipeline from a desktop window.
- Use a stronger face engine automatically when the system can download the official models.

## Features

- Works with single images, folders, and videos.
- Uses an automatic `pro` backend with YuNet + SFace when available.
- Falls back to the classic Haar backend if the pro engine cannot be initialized.
- Adds temporal tracking across video frames to stabilize recurring faces.
- Extracts face crops and scores sharpness.
- Keeps the best face crop per detected person cluster instead of saving endless duplicates.
- Clusters similar detections into reusable groups.
- Exports `gallery.html`, `summary.json`, and `detections.csv`.
- Saves blurred privacy-safe image or video copies.
- Includes a desktop GUI with file pickers and one-click scan flow.
- Shows a visual preview of the selected image or the first video frame in the GUI.
- Creates a downloadable ZIP package of the generated result from the GUI.
- Can open the final report automatically in the browser.
- Downloads and caches the official OpenCV Zoo ONNX models automatically.

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
facetrail scan ./media --output ./output --save-redacted --open-report --engine auto
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
2. preview the selected media directly in the GUI
3. choose what you want FaceTrail to do
4. press Start Scan
5. get the result inside a dedicated output folder for that choice
6. receive a ZIP package of that output that you can share or move easily

Available actions in the GUI:

- `Extract faces + report`
- `Blur faces in the original media`
- `Full workspace: crops + report + blurred exports`

Available engines in the GUI:

- `Auto`: recommended, tries YuNet + SFace first
- `Pro`: forces YuNet + SFace
- `Classic`: forces Haar cascades

## What the GUI adds

- Choose files or folders with buttons instead of typing paths.
- Preview images and the first frame of videos before scanning.
- Pick the output folder visually.
- Choose the exact result type before scanning.
- Start the full scan with one click.
- Open the generated report again from the same window.
- Open the output folder or generated ZIP package directly from the same window.

## Output structure

- `output/extract_faces_YYYYMMDD-HHMMSS/`: face crops plus report files.
- Face crops are reduced to the best shot per detected face cluster.
- `output/privacy_blur_YYYYMMDD-HHMMSS/`: blurred image or video output.
- `output/full_workspace_YYYYMMDD-HHMMSS/`: crops, blurred copies, and report files.

Inside report-enabled modes:

- `faces/`: extracted face crops.
- `report/gallery.html`: visual review report.
- `report/summary.json`: machine-readable summary.
- `report/detections.csv`: spreadsheet-friendly manifest.

Inside blur-enabled modes:

- `redacted/`: privacy-safe image or video exports.

The GUI can also create:

- `output/<mode_timestamp>.zip`: a downloadable ZIP package of the generated result folder.

## Command reference

```text
facetrail scan INPUT [--output OUTPUT] [--sample-every N] [--min-face-size PX] [--cluster-threshold FLOAT|auto] [--engine auto|pro|classic] [--save-redacted] [--open-report]
facetrail gui [--start-input PATH]
facetrail-gui
```

Recommended defaults:

- `--sample-every 5` for balanced speed on videos.
- `--min-face-size 64` for everyday phone and webcam footage.
- `--cluster-threshold auto` to let FaceTrail choose the correct value per engine.
- `--engine auto` for the best balance between quality and compatibility.

## Pro engine

The pro backend uses official OpenCV Zoo models:

- YuNet for face detection
- SFace for face embeddings and more reliable clustering

FaceTrail downloads these ONNX models automatically into your user cache the first time they are needed. If that step fails and you are using `--engine auto`, the app falls back to the classic Haar-based mode instead of crashing.

## Release packages

This repository includes a release packer that generates:

- `dist/facetrail-windows-vX.Y.Z.zip`
- `dist/facetrail-linux-vX.Y.Z.tar.gz`

Build them with:

```bash
python scripts/build_release.py
```

## Terminal walkthrough

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
facetrail scan .\media --output .\output --engine auto --save-redacted --open-report
facetrail gui
```

Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
facetrail scan ./media --output ./output --engine auto --save-redacted --open-report
facetrail gui
```

## Practical use cases

- Privacy pass before sending event footage to clients or friends.
- Media triage for creators, journalists, and researchers.
- Local photo review to find repeated people quickly.
- Lightweight preparation step before a more advanced vision pipeline.

## Limitations

- Clustering is appearance-based and lightweight. It is not a biometric identity system.
- The classic Haar backend is portable, but the pro backend is more reliable for real-world use.
- Performance depends on lighting, face angle, and source quality.
- The desktop GUI uses Tkinter, which is included in most Python installs but can be missing in minimal Linux environments.

---

# FaceTrail en Espanol

![FaceTrail banner](assets/banner.svg)

FaceTrail es una herramienta multiplataforma para extraer rostros, agrupar apariciones similares, generar reportes visuales y exportar copias anonimizadas. Puede analizar un archivo o una carpeta completa, guardar recortes automaticamente, agrupar detecciones parecidas, crear copias con desenfoque para compartir y ahora tambien incluye un motor pro basado en modelos oficiales de OpenCV Zoo, ademas de una interfaz de escritorio para personas que no quieren usar terminal.

## Por que es util

- Permite revisar quien aparece en una carpeta multimedia sin inspeccionar archivo por archivo.
- Conserva solo la mejor captura de apariciones repetidas segun nitidez.
- Genera salidas HTML, JSON y CSV para auditorias, curacion o datasets locales.
- Crea exportaciones anonimizadas antes de compartir material.
- Permite que personas no tecnicas ejecuten todo desde una ventana local.
- Usa automaticamente un motor facial mas moderno cuando logra descargar los modelos oficiales.

## Funciones

- Funciona con imagenes individuales, carpetas y videos.
- Usa un backend `pro` con YuNet + SFace cuando esta disponible.
- Hace fallback al backend clasico con Haar si el motor pro no se puede inicializar.
- Agrega tracking temporal entre frames de video para estabilizar rostros recurrentes.
- Extrae recortes de rostros y mide nitidez.
- Conserva la mejor imagen por cluster de rostro en vez de guardar duplicados sin fin.
- Agrupa detecciones similares en clusters reutilizables.
- Exporta `gallery.html`, `summary.json` y `detections.csv`.
- Guarda copias de imagen o video con desenfoque facial.
- Incluye una GUI de escritorio con selectores y flujo de un clic.
- Muestra una vista previa de la imagen o del primer frame del video elegido.
- Genera un ZIP descargable con el resultado final desde la GUI.
- Puede abrir automaticamente el reporte final en el navegador.
- Descarga y guarda en cache los modelos ONNX oficiales de OpenCV Zoo.

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
facetrail scan ./media --output ./output --save-redacted --open-report --engine auto
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
2. previsualizar el archivo elegido directamente en la GUI
3. elegir que quieres que haga FaceTrail
4. pulsar `Start Scan`
5. recibir el resultado dentro de una carpeta dedicada a esa eleccion
6. obtener tambien un ZIP del resultado para moverlo o compartirlo facil

Acciones disponibles en la GUI:

- `Extract faces + report`
- `Blur faces in the original media`
- `Full workspace: crops + report + blurred exports`

Motores disponibles en la GUI:

- `Auto`: recomendado, intenta YuNet + SFace primero
- `Pro`: fuerza YuNet + SFace
- `Classic`: fuerza Haar cascades

## Que agrega la GUI

- Elegir archivos o carpetas con botones en vez de escribir rutas.
- Previsualizar imagenes y el primer frame de videos antes de analizar.
- Elegir visualmente la carpeta de salida.
- Elegir el tipo exacto de resultado antes de analizar.
- Iniciar todo el analisis con un clic.
- Reabrir el reporte desde la misma ventana.
- Abrir directamente la carpeta de salida o el ZIP generado.

## Estructura de salida

- `output/extract_faces_YYYYMMDD-HHMMSS/`: recortes de rostros y archivos de reporte.
- Los recortes quedan reducidos a la mejor foto por cluster de rostro detectado.
- `output/privacy_blur_YYYYMMDD-HHMMSS/`: imagenes o videos anonimizados.
- `output/full_workspace_YYYYMMDD-HHMMSS/`: recortes, exportaciones difuminadas y reporte.

Dentro de los modos con reporte:

- `faces/`: recortes de rostros detectados.
- `report/gallery.html`: reporte visual.
- `report/summary.json`: resumen legible por maquinas.
- `report/detections.csv`: manifiesto facil de abrir en Excel o similares.

Dentro de los modos con anonimizado:

- `redacted/`: exportaciones seguras para compartir.

La GUI tambien puede crear:

- `output/<modo_timestamp>.zip`: paquete ZIP descargable del resultado generado.

## Referencia de comandos

```text
facetrail scan INPUT [--output OUTPUT] [--sample-every N] [--min-face-size PX] [--cluster-threshold FLOAT|auto] [--engine auto|pro|classic] [--save-redacted] [--open-report]
facetrail gui [--start-input PATH]
facetrail-gui
```

Valores recomendados:

- `--sample-every 5` para equilibrar velocidad en videos.
- `--min-face-size 64` para metraje comun de webcam o celular.
- `--cluster-threshold auto` para que FaceTrail elija el valor correcto segun el motor.
- `--engine auto` para el mejor equilibrio entre calidad y compatibilidad.

## Motor pro

El backend pro usa modelos oficiales de OpenCV Zoo:

- YuNet para deteccion facial
- SFace para embeddings y agrupamiento mas confiable

FaceTrail descarga esos modelos ONNX automaticamente en la cache del usuario la primera vez que los necesita. Si eso falla y estas usando `--engine auto`, la aplicacion hace fallback al modo clasico con Haar en vez de romperse.

## Paquetes de release

Este repositorio incluye un empaquetador que genera:

- `dist/facetrail-windows-vX.Y.Z.zip`
- `dist/facetrail-linux-vX.Y.Z.tar.gz`

Se generan con:

```bash
python scripts/build_release.py
```

## Flujo por terminal

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
facetrail scan .\media --output .\output --engine auto --save-redacted --open-report
facetrail gui
```

Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
facetrail scan ./media --output ./output --engine auto --save-redacted --open-report
facetrail gui
```

## Casos de uso

- Primera pasada de privacidad antes de entregar videos a clientes o amigos.
- Triaje de material para creadores, periodistas o investigadores.
- Revision local de fotos para encontrar personas repetidas rapidamente.
- Paso liviano previo a un pipeline de vision mas avanzado.

## Limitaciones

- El agrupamiento es ligero y basado en apariencia. No pretende ser biometria.
- El backend clasico con Haar es portable, pero el motor pro es bastante mas confiable en uso real.
- El rendimiento depende de la iluminacion, el angulo facial y la calidad del material.
- La GUI de escritorio usa Tkinter, que suele venir con Python, pero puede faltar en instalaciones minimas de Linux.
