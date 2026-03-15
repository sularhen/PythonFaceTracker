# FaceTrail

![FaceTrail banner](assets/banner.svg)

FaceTrail es una CLI multiplataforma para extraer rostros, agrupar apariciones similares, generar reportes visuales y exportar copias anonimizadas. Convierte una carpeta de imagenes o videos en un espacio de trabajo realmente util, y ahora suma un motor pro con modelos oficiales de OpenCV Zoo mas una GUI de escritorio para uso simple.

## Que hace

- Escanea imagenes individuales, carpetas completas o videos.
- Detecta rostros con un backend pro YuNet + SFace cuando esta disponible.
- Hace fallback a Haar si el motor pro no se puede inicializar.
- Extrae recortes automaticamente y agrupa apariciones parecidas.
- Calcula la mejor captura de cada grupo segun nitidez.
- Genera un reporte HTML, un `summary.json` y un `detections.csv`.
- Puede exportar copias anonimizadas con desenfoque facial.
- Descarga automaticamente los modelos oficiales ONNX en la cache del usuario.

## Instalacion

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

## Paquetes de Release

El repositorio ahora incluye un generador de paquetes que deja siempre:

- `dist/facetrail-windows-vX.Y.Z.zip`
- `dist/facetrail-linux-vX.Y.Z.tar.gz`

Se genera con:

```bash
python scripts/build_release.py
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

## Salidas

- `output/faces/`: recortes de rostros detectados.
- `output/redacted/`: imagenes o videos con rostros desenfocados.
- `output/report/gallery.html`: galeria visual.
- `output/report/summary.json`: resumen estructurado.
- `output/report/detections.csv`: manifest de detecciones.

## Idea del producto

FaceTrail sirve para:

- Curar material audiovisual antes de compartirlo.
- Revisar bibliotecas de fotos con personas repetidas.
- Preparar datasets pequenos o auditorias visuales.
- Crear una pasada rapida de privacidad sobre videos locales.

## Limitaciones

- El agrupamiento usa descriptores ligeros de apariencia y no pretende ser biometria.
- El detector esta optimizado para practicidad, no para vigilancia ni identificacion.

## Credito

Este repositorio parte de `PythonFaceTracker`, pero fue reconstruido como una utilidad mas utilizable, portable y documentada.
