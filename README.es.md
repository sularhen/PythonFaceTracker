# FaceTrail

![FaceTrail banner](assets/banner.svg)

FaceTrail es una CLI multiplataforma para extraer rostros, agrupar apariciones similares, generar reportes visuales y exportar copias anonimizadas. Ahora funciona mucho mas como una aplicacion real: ejecutas `facetrail`, se abre la GUI, eliges imagen o video, seleccionas el tipo de salida, y la misma app te deja el resultado en carpeta y tambien en ZIP.

## Que hace

- Escanea imagenes individuales, carpetas completas o videos.
- Detecta rostros con un backend pro YuNet + SFace cuando esta disponible.
- Hace fallback a Haar si el motor pro no se puede inicializar.
- Sigue rostros a traves del tiempo en video.
- Guarda solo la mejor foto por rostro detectado.
- Genera reportes HTML, JSON y CSV.
- Puede exportar copias anonimizadas.
- Genera paquetes ZIP del resultado desde la GUI.

## Como se usa ahora

Si ya instalaste el proyecto:

```bash
facetrail
```

Eso abre la GUI directamente.

Si descargaste un release o clonaste el repo:

- Windows: ejecuta `facetrail.bat` o `facetrail.ps1`
- Linux: ejecuta `bash facetrail.sh`

Esos launchers crean una `.venv`, instalan FaceTrail y abren la GUI automaticamente.

## Flujo de la GUI

1. eliges una imagen, video o carpeta
2. ves una preview del archivo
3. eliges el tipo de salida
4. pulsas `Start Scan`
5. FaceTrail guarda el resultado en una carpeta segun el modo
6. FaceTrail genera tambien un ZIP que puedes abrir, copiar o guardar en otra ruta

## Modos de salida

- `extract_faces`: guarda `faces/` y `report/`
- `privacy_blur`: guarda `redacted/`
- `full_workspace`: guarda `faces/`, `redacted/` y `report/`

La estructura queda asi:

- `output/extract_faces/YYYYMMDD-HHMMSS/`
- `output/privacy_blur/YYYYMMDD-HHMMSS/`
- `output/full_workspace/YYYYMMDD-HHMMSS/`

Y el ZIP queda junto a la ejecucion correspondiente.

## Motor pro

FaceTrail usa:

- YuNet para deteccion facial
- SFace para embeddings y clustering mas confiable

Los modelos se descargan automaticamente en la cache del usuario la primera vez. Si falla y estas usando `auto`, vuelve al backend clasico.

## Flujo por terminal

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
facetrail scan .\media --output .\output --engine auto --save-redacted --open-report
facetrail
```

Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
facetrail scan ./media --output ./output --engine auto --save-redacted --open-report
facetrail
```
