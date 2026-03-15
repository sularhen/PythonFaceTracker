from __future__ import annotations

import json
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np
from platformdirs import user_cache_dir


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".m4v"}

MODEL_URLS = {
    "yunet": "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    "sface": "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx",
}

DEFAULT_CLUSTER_THRESHOLDS = {
    "opencv_yunet_sface": 0.363,
    "haar_legacy": 0.92,
}


@dataclass
class Detection:
    source_path: str
    source_kind: str
    frame_index: int
    timestamp_seconds: float
    bbox: tuple[int, int, int, int]
    sharpness: float
    confidence: float
    cluster_id: int = -1
    crop_path: str = ""
    redacted_path: str = ""


class FaceTrailAnalyzer:
    def __init__(
        self,
        output_dir: Path,
        *,
        sample_every: int = 5,
        min_face_size: int = 64,
        cluster_threshold: float | None = None,
        save_redacted: bool = False,
        save_crops: bool = True,
        save_report: bool = True,
        engine: str = "auto",
    ) -> None:
        self.output_dir = output_dir
        self.sample_every = max(1, sample_every)
        self.min_face_size = min_face_size
        self.cluster_threshold_override = cluster_threshold
        self.save_redacted = save_redacted
        self.save_crops = save_crops
        self.save_report = save_report
        self.requested_engine = engine
        self.backend_name = ""
        self.face_cascades: list[cv2.CascadeClassifier] = []
        self.face_detector_yn: cv2.FaceDetectorYN | None = None
        self.face_recognizer_sf: cv2.FaceRecognizerSF | None = None
        self.crops_dir = output_dir / "faces"
        self.redacted_dir = output_dir / "redacted"
        self.report_dir = output_dir / "report"
        self._ensure_dirs()
        self._setup_backend()
        self.cluster_threshold = (
            cluster_threshold
            if cluster_threshold is not None
            else DEFAULT_CLUSTER_THRESHOLDS[self.backend_name]
        )

    def _ensure_dirs(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if self.save_crops:
            self.crops_dir.mkdir(parents=True, exist_ok=True)
        if self.save_report:
            self.report_dir.mkdir(parents=True, exist_ok=True)
        if self.save_redacted:
            self.redacted_dir.mkdir(parents=True, exist_ok=True)

    def _setup_backend(self) -> None:
        if self.requested_engine in {"auto", "pro"}:
            try:
                self._setup_pro_backend()
                self.backend_name = "opencv_yunet_sface"
                return
            except Exception as exc:
                if self.requested_engine == "pro":
                    raise RuntimeError(f"Unable to initialize pro engine: {exc}") from exc
        self._setup_classic_backend()
        self.backend_name = "haar_legacy"

    def _setup_pro_backend(self) -> None:
        if not hasattr(cv2, "FaceDetectorYN") or not hasattr(cv2, "FaceRecognizerSF"):
            raise RuntimeError("OpenCV build does not expose FaceDetectorYN/FaceRecognizerSF.")
        model_dir = Path(user_cache_dir("facetrail", "sularhen")) / "models"
        model_dir.mkdir(parents=True, exist_ok=True)
        yunet_path = self._download_model_if_needed(MODEL_URLS["yunet"], model_dir / "face_detection_yunet_2023mar.onnx")
        sface_path = self._download_model_if_needed(MODEL_URLS["sface"], model_dir / "face_recognition_sface_2021dec.onnx")
        self.face_detector_yn = cv2.FaceDetectorYN_create(str(yunet_path), "", (320, 320), 0.87, 0.3, 5000)
        self.face_recognizer_sf = cv2.FaceRecognizerSF_create(str(sface_path), "")

    def _setup_classic_backend(self) -> None:
        cascade_root = Path(cv2.data.haarcascades)
        cascade_names = [
            "haarcascade_frontalface_default.xml",
            "haarcascade_profileface.xml",
        ]
        self.face_cascades = []
        for name in cascade_names:
            cascade = cv2.CascadeClassifier(str(cascade_root / name))
            if cascade.empty():
                raise RuntimeError(f"Unable to load cascade: {name}")
            self.face_cascades.append(cascade)

    def _download_model_if_needed(self, url: str, destination: Path) -> Path:
        if destination.exists():
            return destination
        request = urllib.request.Request(url, headers={"User-Agent": "FaceTrail"})
        with urllib.request.urlopen(request, timeout=60) as response:
            destination.write_bytes(response.read())
        return destination

    def collect_inputs(self, input_path: Path) -> tuple[list[Path], list[Path]]:
        if not input_path.exists():
            raise FileNotFoundError(f"Input path does not exist: {input_path}")
        if input_path.is_file():
            return self._split_by_type([input_path])
        files = [path for path in input_path.rglob("*") if path.is_file()]
        return self._split_by_type(files)

    def _split_by_type(self, files: Iterable[Path]) -> tuple[list[Path], list[Path]]:
        images = [path for path in files if path.suffix.lower() in IMAGE_EXTENSIONS]
        videos = [path for path in files if path.suffix.lower() in VIDEO_EXTENSIONS]
        return images, videos

    def analyze(self, input_path: Path) -> dict:
        images, videos = self.collect_inputs(input_path)
        detections: list[Detection] = []
        embeddings: list[np.ndarray] = []
        media_stats: dict[str, dict[str, int]] = {}

        for image_path in images:
            image_detections, image_embeddings = self._process_image(image_path)
            detections.extend(image_detections)
            embeddings.extend(image_embeddings)
            media_stats[str(image_path)] = {"faces": len(image_detections), "frames": 1}

        for video_path in videos:
            video_detections, video_embeddings, frame_count = self._process_video(video_path)
            detections.extend(video_detections)
            embeddings.extend(video_embeddings)
            media_stats[str(video_path)] = {"faces": len(video_detections), "frames": frame_count}

        self._cluster_detections(detections, embeddings)
        if self.save_crops:
            self._retain_best_crops(detections)
        summary = self._build_summary(detections, media_stats, images, videos)
        if self.save_report:
            self._write_outputs(summary, detections)
        return summary

    def _process_image(self, image_path: Path) -> tuple[list[Detection], list[np.ndarray]]:
        frame = cv2.imread(str(image_path))
        if frame is None:
            return [], []
        detections, embeddings = self._detect_faces(frame, image_path, "image", 0, 0.0)
        if self.save_redacted and detections:
            redacted = self._redact_frame(frame, detections)
            output_path = self.redacted_dir / f"{image_path.stem}_redacted{image_path.suffix.lower()}"
            cv2.imwrite(str(output_path), redacted)
            for detection in detections:
                detection.redacted_path = str(output_path)
        return detections, embeddings

    def _process_video(self, video_path: Path) -> tuple[list[Detection], list[np.ndarray], int]:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return [], [], 0

        fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        writer = None
        output_path = self.redacted_dir / f"{video_path.stem}_redacted.mp4"
        if self.save_redacted and frame_width > 0 and frame_height > 0 and fps > 0:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(str(output_path), fourcc, fps, (frame_width, frame_height))

        frame_index = 0
        detections: list[Detection] = []
        embeddings: list[np.ndarray] = []
        effective_sample_every = 1 if writer is not None else self.sample_every
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            current_detections: list[Detection] = []
            current_embeddings: list[np.ndarray] = []
            if frame_index % effective_sample_every == 0:
                timestamp_seconds = frame_index / fps if fps > 0 else 0.0
                current_detections, current_embeddings = self._detect_faces(
                    frame,
                    video_path,
                    "video",
                    frame_index,
                    timestamp_seconds,
                )
                detections.extend(current_detections)
                embeddings.extend(current_embeddings)

            if writer is not None:
                redacted_frame = self._redact_frame(frame, current_detections)
                writer.write(redacted_frame)
                for detection in current_detections:
                    detection.redacted_path = str(output_path)
            frame_index += 1

        cap.release()
        if writer is not None:
            writer.release()
        return detections, embeddings, frame_index

    def _detect_faces(
        self,
        frame: np.ndarray,
        source_path: Path,
        source_kind: str,
        frame_index: int,
        timestamp_seconds: float,
    ) -> tuple[list[Detection], list[np.ndarray]]:
        if self.backend_name == "opencv_yunet_sface":
            return self._detect_faces_pro(frame, source_path, source_kind, frame_index, timestamp_seconds)
        return self._detect_faces_classic(frame, source_path, source_kind, frame_index, timestamp_seconds)

    def _detect_faces_pro(
        self,
        frame: np.ndarray,
        source_path: Path,
        source_kind: str,
        frame_index: int,
        timestamp_seconds: float,
    ) -> tuple[list[Detection], list[np.ndarray]]:
        assert self.face_detector_yn is not None
        assert self.face_recognizer_sf is not None

        height, width = frame.shape[:2]
        self.face_detector_yn.setInputSize((width, height))
        _, faces = self.face_detector_yn.detect(frame)
        if faces is None:
            return [], []

        detections: list[Detection] = []
        embeddings: list[np.ndarray] = []
        base_name = source_path.stem.replace(" ", "_")

        for box_index, face in enumerate(faces):
            face_row = np.asarray(face, dtype=np.float32)
            x, y, w, h = self._clamp_box(face_row[:4], width, height)
            if w <= 0 or h <= 0:
                continue
            crop = frame[y : y + h, x : x + w]
            if crop.size == 0:
                continue

            aligned = self.face_recognizer_sf.alignCrop(frame, face_row)
            embedding = np.asarray(self.face_recognizer_sf.feature(aligned), dtype=np.float32).flatten()
            norm = float(np.linalg.norm(embedding))
            if norm > 0:
                embedding /= norm

            sharpness = self._sharpness_score(crop)
            confidence = float(face_row[14])
            crop_path = self._save_crop_if_needed(base_name, frame_index, box_index, crop)

            detections.append(
                Detection(
                    source_path=str(source_path),
                    source_kind=source_kind,
                    frame_index=frame_index,
                    timestamp_seconds=timestamp_seconds,
                    bbox=(x, y, w, h),
                    sharpness=sharpness,
                    confidence=confidence,
                    crop_path=crop_path,
                )
            )
            embeddings.append(embedding)

        return detections, embeddings

    def _detect_faces_classic(
        self,
        frame: np.ndarray,
        source_path: Path,
        source_kind: str,
        frame_index: int,
        timestamp_seconds: float,
    ) -> tuple[list[Detection], list[np.ndarray]]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        raw_boxes: list[tuple[int, int, int, int]] = []
        for cascade in self.face_cascades:
            boxes = cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(self.min_face_size, self.min_face_size),
            )
            raw_boxes.extend(tuple(int(value) for value in box) for box in boxes)

        boxes = self._deduplicate_boxes(raw_boxes)
        detections: list[Detection] = []
        embeddings: list[np.ndarray] = []
        base_name = source_path.stem.replace(" ", "_")

        for box_index, (x, y, w, h) in enumerate(boxes):
            crop = frame[y : y + h, x : x + w]
            if crop.size == 0:
                continue
            embedding = self._create_embedding_legacy(crop)
            sharpness = self._sharpness_score(crop)
            confidence = min(0.99, 0.55 + min(0.4, sharpness / 1000.0))
            crop_path = self._save_crop_if_needed(base_name, frame_index, box_index, crop)

            detections.append(
                Detection(
                    source_path=str(source_path),
                    source_kind=source_kind,
                    frame_index=frame_index,
                    timestamp_seconds=timestamp_seconds,
                    bbox=(x, y, w, h),
                    sharpness=sharpness,
                    confidence=confidence,
                    crop_path=crop_path,
                )
            )
            embeddings.append(embedding)

        return detections, embeddings

    def _save_crop_if_needed(self, base_name: str, frame_index: int, box_index: int, crop: np.ndarray) -> str:
        if not self.save_crops:
            return ""
        crop_name = f"{base_name}_f{frame_index:06d}_face{box_index:02d}.jpg"
        crop_file = self.crops_dir / crop_name
        cv2.imwrite(str(crop_file), crop)
        return str(crop_file)

    def _clamp_box(self, box: np.ndarray, frame_width: int, frame_height: int) -> tuple[int, int, int, int]:
        x, y, w, h = [int(round(float(value))) for value in box]
        x = max(0, x)
        y = max(0, y)
        w = min(w, frame_width - x)
        h = min(h, frame_height - y)
        return x, y, w, h

    def _deduplicate_boxes(self, boxes: list[tuple[int, int, int, int]]) -> list[tuple[int, int, int, int]]:
        unique: list[tuple[int, int, int, int]] = []
        for candidate in boxes:
            if not any(self._iou(candidate, existing) > 0.35 for existing in unique):
                unique.append(candidate)
        return unique

    def _iou(self, a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> float:
        ax1, ay1, aw, ah = a
        bx1, by1, bw, bh = b
        ax2, ay2 = ax1 + aw, ay1 + ah
        bx2, by2 = bx1 + bw, by1 + bh
        inter_x1 = max(ax1, bx1)
        inter_y1 = max(ay1, by1)
        inter_x2 = min(ax2, bx2)
        inter_y2 = min(ay2, by2)
        if inter_x2 <= inter_x1 or inter_y2 <= inter_y1:
            return 0.0
        inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
        area_a = aw * ah
        area_b = bw * bh
        return inter_area / float(area_a + area_b - inter_area)

    def _create_embedding_legacy(self, crop: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        normalized = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA)
        vector = normalized.astype(np.float32).reshape(-1)
        vector -= vector.mean()
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector /= norm
        histogram = cv2.calcHist([gray], [0], None, [32], [0, 256]).flatten().astype(np.float32)
        histogram_norm = np.linalg.norm(histogram)
        if histogram_norm > 0:
            histogram /= histogram_norm
        return np.concatenate([vector, histogram])

    def _sharpness_score(self, crop: np.ndarray) -> float:
        return float(cv2.Laplacian(crop, cv2.CV_64F).var())

    def _cluster_detections(self, detections: list[Detection], embeddings: list[np.ndarray]) -> None:
        clusters: list[np.ndarray] = []
        counts: list[int] = []
        for index, embedding in enumerate(embeddings):
            assigned_cluster = -1
            best_score = -1.0
            for cluster_id, centroid in enumerate(clusters):
                score = self._match_similarity(embedding, centroid)
                if score > best_score:
                    best_score = score
                    assigned_cluster = cluster_id
            if best_score >= self.cluster_threshold and assigned_cluster >= 0:
                count = counts[assigned_cluster]
                clusters[assigned_cluster] = (clusters[assigned_cluster] * count + embedding) / (count + 1)
                counts[assigned_cluster] += 1
                detections[index].cluster_id = assigned_cluster
            else:
                clusters.append(embedding.copy())
                counts.append(1)
                detections[index].cluster_id = len(clusters) - 1

    def _match_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        if self.backend_name == "opencv_yunet_sface" and self.face_recognizer_sf is not None:
            feature_a = a.reshape(1, -1).astype(np.float32)
            feature_b = b.reshape(1, -1).astype(np.float32)
            return float(self.face_recognizer_sf.match(feature_a, feature_b, cv2.FaceRecognizerSF_FR_COSINE))
        denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
        if denominator == 0:
            return 0.0
        return float(np.dot(a, b) / denominator)

    def _redact_frame(self, frame: np.ndarray, detections: list[Detection]) -> np.ndarray:
        redacted = frame.copy()
        for detection in detections:
            x, y, w, h = detection.bbox
            face = redacted[y : y + h, x : x + w]
            if face.size == 0:
                continue
            redacted[y : y + h, x : x + w] = cv2.GaussianBlur(face, (35, 35), 18)
        return redacted

    def _retain_best_crops(self, detections: list[Detection]) -> None:
        best_by_cluster: dict[int, Detection] = {}
        for detection in detections:
            if not detection.crop_path:
                continue
            current_best = best_by_cluster.get(detection.cluster_id)
            if current_best is None or (detection.sharpness, detection.confidence) > (
                current_best.sharpness,
                current_best.confidence,
            ):
                best_by_cluster[detection.cluster_id] = detection

        keep_paths = {detection.crop_path for detection in best_by_cluster.values() if detection.crop_path}
        for detection in detections:
            if detection.crop_path and detection.crop_path not in keep_paths:
                crop_file = Path(detection.crop_path)
                if crop_file.exists():
                    crop_file.unlink()
                detection.crop_path = ""

    def _build_summary(
        self,
        detections: list[Detection],
        media_stats: dict[str, dict[str, int]],
        images: list[Path],
        videos: list[Path],
    ) -> dict:
        clusters: dict[int, list[Detection]] = {}
        for detection in detections:
            clusters.setdefault(detection.cluster_id, []).append(detection)

        people = []
        for cluster_id, cluster_detections in sorted(clusters.items()):
            best = max(cluster_detections, key=lambda item: (item.sharpness, item.confidence))
            people.append(
                {
                    "cluster_id": cluster_id,
                    "detections": len(cluster_detections),
                    "best_face": best.crop_path,
                    "avg_sharpness": round(
                        sum(item.sharpness for item in cluster_detections) / len(cluster_detections),
                        2,
                    ),
                    "sources": sorted({item.source_path for item in cluster_detections}),
                }
            )

        return {
            "engine": self.backend_name,
            "input_images": len(images),
            "input_videos": len(videos),
            "media": media_stats,
            "faces_detected": len(detections),
            "people_clustered": len(people),
            "cluster_threshold": self.cluster_threshold,
            "people": people,
            "detections": [asdict(detection) for detection in detections],
        }

    def _write_outputs(self, summary: dict, detections: list[Detection]) -> None:
        summary_path = self.report_dir / "summary.json"
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

        html_path = self.report_dir / "gallery.html"
        html_path.write_text(self._build_html(summary), encoding="utf-8")

        manifest_path = self.report_dir / "detections.csv"
        rows = [
            "cluster_id,source_kind,source_path,frame_index,timestamp_seconds,sharpness,confidence,crop_path,redacted_path"
        ]
        for detection in detections:
            rows.append(
                ",".join(
                    [
                        str(detection.cluster_id),
                        detection.source_kind,
                        self._csv_escape(detection.source_path),
                        str(detection.frame_index),
                        f"{detection.timestamp_seconds:.3f}",
                        f"{detection.sharpness:.3f}",
                        f"{detection.confidence:.3f}",
                        self._csv_escape(detection.crop_path),
                        self._csv_escape(detection.redacted_path),
                    ]
                )
            )
        manifest_path.write_text("\n".join(rows), encoding="utf-8")

    def _csv_escape(self, value: str) -> str:
        escaped = value.replace('"', '""')
        return f'"{escaped}"'

    def _build_html(self, summary: dict) -> str:
        cards = []
        for person in summary["people"]:
            sources = "<br>".join(person["sources"][:3]) or "No sources"
            best_face = ""
            if person["best_face"]:
                best_face = Path(person["best_face"]).resolve().as_uri()
            image_markup = (
                f'<img src="{best_face}" alt="Cluster {person["cluster_id"]}">'
                if best_face
                else '<div class="placeholder">No face crop saved for this mode</div>'
            )
            cards.append(
                f"""
                <article class="card">
                  {image_markup}
                  <div class="meta">
                    <h3>Cluster {person['cluster_id']}</h3>
                    <p>{person['detections']} detections</p>
                    <p>Avg sharpness: {person['avg_sharpness']}</p>
                    <p>{sources}</p>
                  </div>
                </article>
                """
            )
        media_rows = []
        for source_path, data in summary["media"].items():
            media_rows.append(
                f"<tr><td>{source_path}</td><td>{data['frames']}</td><td>{data['faces']}</td></tr>"
            )
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>FaceTrail Report</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f5f1e8;
      --panel: #fffdf8;
      --ink: #1d2a33;
      --accent: #0d7c66;
      --border: #d9cfbf;
      --muted: #52616c;
    }}
    body {{
      margin: 0;
      font-family: "Segoe UI", sans-serif;
      background: radial-gradient(circle at top, #fff8ed, var(--bg));
      color: var(--ink);
    }}
    main {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }}
    .hero {{
      background: linear-gradient(135deg, #143d52, #0d7c66);
      color: white;
      padding: 24px;
      border-radius: 22px;
      box-shadow: 0 20px 60px rgba(20, 61, 82, 0.18);
    }}
    .hero p {{
      max-width: 700px;
      color: #e6f0f5;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin: 24px 0;
    }}
    .stat, .card {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 16px;
    }}
    .panels {{
      display: grid;
      grid-template-columns: 1.2fr .8fr;
      gap: 16px;
      margin-bottom: 24px;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 18px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 16px;
    }}
    img {{
      width: 100%;
      height: 220px;
      object-fit: cover;
      border-radius: 14px;
      display: block;
    }}
    .placeholder {{
      height: 220px;
      border-radius: 14px;
      display: grid;
      place-items: center;
      text-align: center;
      padding: 16px;
      background: linear-gradient(135deg, #ece4d7, #ddd1be);
      color: var(--muted);
      font-weight: 600;
    }}
    h1, h2, h3, p {{
      margin-top: 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.95rem;
    }}
    td, th {{
      padding: 10px 8px;
      border-bottom: 1px solid var(--border);
      text-align: left;
      vertical-align: top;
    }}
    .muted {{
      color: var(--muted);
    }}
    .pill {{
      display: inline-block;
      padding: 6px 10px;
      border-radius: 999px;
      background: #e4f4ef;
      color: #0d7c66;
      font-size: 0.85rem;
      margin-right: 8px;
      margin-bottom: 8px;
    }}
    @media (max-width: 860px) {{
      .panels {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <h1>FaceTrail Report</h1>
      <p>Detected {summary['faces_detected']} faces and grouped them into {summary['people_clustered']} clusters using the <strong>{summary['engine']}</strong> engine. This report is designed for quick review, privacy checks, and local media curation.</p>
    </section>
    <section class="stats">
      <div class="stat"><h3>Images</h3><p>{summary['input_images']}</p></div>
      <div class="stat"><h3>Videos</h3><p>{summary['input_videos']}</p></div>
      <div class="stat"><h3>Faces</h3><p>{summary['faces_detected']}</p></div>
      <div class="stat"><h3>Clusters</h3><p>{summary['people_clustered']}</p></div>
    </section>
    <section class="panels">
      <div class="panel">
        <h2>How to read this</h2>
        <p class="muted">Each cluster groups visually similar face crops. Use the best face card below as a quick starting point, then cross-check the source list before sharing or deleting anything.</p>
        <span class="pill">Automatic crops</span>
        <span class="pill">Blur-ready exports</span>
        <span class="pill">CSV and JSON included</span>
      </div>
      <div class="panel">
        <h2>Source Summary</h2>
        <table>
          <thead>
            <tr><th>Source</th><th>Frames</th><th>Faces</th></tr>
          </thead>
          <tbody>
            {''.join(media_rows)}
          </tbody>
        </table>
      </div>
    </section>
    <section>
      <h2>Best Face Per Cluster</h2>
      <div class="grid">
        {''.join(cards)}
      </div>
    </section>
  </main>
</body>
</html>
"""
