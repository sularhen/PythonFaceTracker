# FaceTrail

![FaceTrail banner](assets/banner.svg)

FaceTrail es una CLI multiplataforma para extraer rostros, agrupar apariciones similares, generar reportes visuales y exportar copias anonimizadas. Convierte una carpeta de imagenes o videos en un espacio de trabajo realmente util, y ahora suma un motor pro con modelos oficiales de OpenCV Zoo, tracking temporal entre frames y una GUI de escritorio con preview y exportacion ZIP.

## Que hace

- Escanea imagenes individuales, carpetas completas o videos.
- Detecta rostros con un backend pro YuNet + SFace cuando esta disponible.
- Hace fallback a Haar si el motor pro no se puede inicializar.
- Sigue rostros a lo largo del tiempo en video para mejorar continuidad entre frames.
- Extrae recortes automaticamente y agrupa apariciones parecidas.
- Calcula la mejor captura de cada grupo segun nitidez.
- Genera un reporte HTML, un `summary.json` y un `detections.csv`.
- Puede exportar copias anonimizadas con desenfoque facial.
- Descarga automaticamente los modelos oficiales ONNX en la cache del usuario.

## Instalacion

Linux y macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

En Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

## Uso rapido

```bash
facetrail scan ./media --output ./output --save-redacted --engine auto
```

Opciones utiles:

- `--sample-every 10`: procesa uno de cada 10 frames en videos.
- `--min-face-size 96`: ignora rostros muy pequenos.
- `--cluster-threshold auto`: usa el valor correcto segun el motor.
- `--engine auto`: intenta usar el motor pro primero.

## Motor pro

FaceTrail puede usar:

- YuNet para deteccion facial
- SFace para embeddings y agrupamiento mas confiable

Si no logra inicializar ese motor y estas usando `--engine auto`, vuelve al modo clasico automaticamente.

## GUI

La GUI permite:

1. elegir una imagen, video o carpeta
2. previsualizar el archivo elegido directamente
3. elegir el tipo de salida
4. ejecutar el analisis con un clic
5. recibir una carpeta de salida dedicada
6. generar tambien un ZIP descargable del resultado

Tambien permite abrir:

- el reporte HTML
- la carpeta de salida
- el archivo ZIP generado

## Salidas

- `output/extract_faces_YYYYMMDD-HHMMSS/`: recortes de rostros y archivos de reporte.
- `output/privacy_blur_YYYYMMDD-HHMMSS/`: imagenes o videos anonimizados.
- `output/full_workspace_YYYYMMDD-HHMMSS/`: recortes, exportaciones difuminadas y reporte.
- `output/<modo_timestamp>.zip`: paquete ZIP descargable del resultado generado.

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

## Limitaciones

- El agrupamiento es ligero y basado en apariencia. No pretende ser biometria.
- El backend clasico con Haar es portable, pero el motor pro es bastante mas confiable en uso real.
- El rendimiento depende de la iluminacion, el angulo facial y la calidad del material.
- La GUI de escritorio usa Tkinter y Pillow; en instalaciones minimas puede requerir instalacion normal de Python.
