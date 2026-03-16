from __future__ import annotations

import os
import queue
import shutil
import subprocess
import sys
import threading
import webbrowser
from datetime import datetime
from pathlib import Path
from tkinter import BooleanVar, IntVar, StringVar, Tk, filedialog, messagebox, ttk

import cv2
from PIL import Image, ImageTk

from facetrail.core import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, FaceTrailAnalyzer


def launch_gui(start_input: str = "") -> None:
    app = FaceTrailApp(start_input=start_input)
    app.run()


def main() -> int:
    launch_gui()
    return 0


class FaceTrailApp:
    def __init__(self, start_input: str = "") -> None:
        self.root = Tk()
        self.root.title("FaceTrail")
        self.root.geometry("980x760")
        self.root.minsize(860, 660)

        self.input_path = StringVar(value=start_input)
        self.output_path = StringVar(value="output")
        self.sample_every = IntVar(value=5)
        self.min_face_size = IntVar(value=64)
        self.cluster_threshold = StringVar(value="auto")
        self.mode = StringVar(value="full_workspace")
        self.engine = StringVar(value="auto")
        self.auto_open = BooleanVar(value=True)
        self.create_zip = BooleanVar(value=True)
        self.status_text = StringVar(value="Choose an image, video, or folder and press Start Scan.")
        self.summary_text = StringVar(value="No scan yet.")
        self.preview_caption = StringVar(value="No media selected.")
        self.run_button: ttk.Button | None = None
        self.last_report_path: Path | None = None
        self.last_output_path: Path | None = None
        self.last_zip_path: Path | None = None
        self.preview_photo: ImageTk.PhotoImage | None = None
        self.preview_label: ttk.Label | None = None
        self.worker_queue: queue.Queue[tuple[str, dict | str]] = queue.Queue()

        self._build_layout()
        self._refresh_preview()
        self.root.after(150, self._poll_worker_queue)

    def run(self) -> None:
        self.root.mainloop()

    def _build_layout(self) -> None:
        self.root.configure(background="#f4ecde")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("FaceTrail.TFrame", background="#f4ecde")
        style.configure("Hero.TFrame", background="#132930")
        style.configure("Card.TLabelframe", background="#fff8ef")
        style.configure("Card.TLabelframe.Label", background="#fff8ef", foreground="#132930", font=("Segoe UI", 11, "bold"))
        style.configure("Primary.TButton", font=("Segoe UI", 11, "bold"))
        style.configure("Status.TLabel", background="#132930", foreground="#fff8ef", font=("Segoe UI", 10))
        style.configure("Preview.TLabel", background="#f0e7d8", foreground="#52616c", anchor="center", justify="center")

        outer = ttk.Frame(self.root, style="FaceTrail.TFrame", padding=18)
        outer.pack(fill="both", expand=True)

        hero = ttk.Frame(outer, style="Hero.TFrame", padding=22)
        hero.pack(fill="x")
        ttk.Label(hero, text="FaceTrail", foreground="#fff8ef", background="#132930", font=("Segoe UI", 28, "bold")).pack(anchor="w")
        ttk.Label(
            hero,
            text="Pick media, choose what you want, preview it, scan it, and export a ready-to-share result package.",
            foreground="#d8d2c9",
            background="#132930",
            font=("Segoe UI", 11),
            wraplength=860,
        ).pack(anchor="w", pady=(8, 0))

        body = ttk.Frame(outer, style="FaceTrail.TFrame")
        body.pack(fill="both", expand=False, pady=(16, 0))
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)

        source_card = ttk.LabelFrame(body, text="Media Source", style="Card.TLabelframe", padding=16)
        source_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        source_card.columnconfigure(0, weight=1)
        ttk.Label(source_card, text="Input file or folder", background="#fff8ef").grid(row=0, column=0, sticky="w")
        ttk.Entry(source_card, textvariable=self.input_path).grid(row=1, column=0, sticky="ew", pady=(6, 10))
        source_buttons = ttk.Frame(source_card, style="FaceTrail.TFrame")
        source_buttons.grid(row=2, column=0, sticky="w")
        ttk.Button(source_buttons, text="Choose Folder", command=self._pick_folder).pack(side="left")
        ttk.Button(source_buttons, text="Choose File", command=self._pick_file).pack(side="left", padx=(8, 0))
        ttk.Button(source_buttons, text="Refresh Preview", command=self._refresh_preview).pack(side="left", padx=(8, 0))

        preview_card = ttk.LabelFrame(body, text="Preview", style="Card.TLabelframe", padding=16)
        preview_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.preview_label = ttk.Label(preview_card, textvariable=self.preview_caption, style="Preview.TLabel", width=40)
        self.preview_label.pack(fill="both", expand=True, ipady=70)

        output_card = ttk.LabelFrame(outer, text="Results", style="Card.TLabelframe", padding=16)
        output_card.pack(fill="x", pady=(16, 0))
        output_card.columnconfigure(0, weight=1)
        ttk.Label(output_card, text="Output folder", background="#fff8ef").grid(row=0, column=0, sticky="w")
        ttk.Entry(output_card, textvariable=self.output_path).grid(row=1, column=0, sticky="ew", pady=(6, 10))
        output_buttons = ttk.Frame(output_card, style="FaceTrail.TFrame")
        output_buttons.grid(row=2, column=0, sticky="w")
        ttk.Button(output_buttons, text="Choose Output", command=self._pick_output).pack(side="left")
        ttk.Button(output_buttons, text="Open Output Folder", command=self._open_output_folder).pack(side="left", padx=(8, 0))
        ttk.Button(output_buttons, text="Open ZIP", command=self._open_last_zip).pack(side="left", padx=(8, 0))
        ttk.Button(output_buttons, text="Save ZIP As...", command=self._save_last_zip_as).pack(side="left", padx=(8, 0))

        mode_card = ttk.LabelFrame(outer, text="Choose What You Want", style="Card.TLabelframe", padding=16)
        mode_card.pack(fill="x", pady=(16, 0))
        ttk.Radiobutton(mode_card, text="Extract faces + report", value="extract_faces", variable=self.mode).pack(anchor="w")
        ttk.Radiobutton(mode_card, text="Blur faces in the original media", value="privacy_blur", variable=self.mode).pack(anchor="w", pady=(6, 0))
        ttk.Radiobutton(
            mode_card,
            text="Full workspace: crops + report + blurred exports",
            value="full_workspace",
            variable=self.mode,
        ).pack(anchor="w", pady=(6, 0))

        engine_card = ttk.LabelFrame(outer, text="Detection Engine", style="Card.TLabelframe", padding=16)
        engine_card.pack(fill="x", pady=(16, 0))
        ttk.Radiobutton(
            engine_card,
            text="Auto (recommended): try YuNet + SFace, then fallback if needed",
            value="auto",
            variable=self.engine,
        ).pack(anchor="w")
        ttk.Radiobutton(
            engine_card,
            text="Pro: YuNet detection + SFace identity features",
            value="pro",
            variable=self.engine,
        ).pack(anchor="w", pady=(6, 0))
        ttk.Radiobutton(
            engine_card,
            text="Classic: Haar cascades only",
            value="classic",
            variable=self.engine,
        ).pack(anchor="w", pady=(6, 0))

        settings_card = ttk.LabelFrame(outer, text="Automation Settings", style="Card.TLabelframe", padding=16)
        settings_card.pack(fill="x", pady=(16, 0))
        for index in range(4):
            settings_card.columnconfigure(index, weight=1)

        ttk.Label(settings_card, text="Sample every N frames", background="#fff8ef").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(settings_card, from_=1, to=120, textvariable=self.sample_every, width=8).grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Label(settings_card, text="Minimum face size", background="#fff8ef").grid(row=0, column=1, sticky="w")
        ttk.Spinbox(settings_card, from_=24, to=512, textvariable=self.min_face_size, width=8).grid(row=1, column=1, sticky="w", pady=(6, 0))
        ttk.Label(settings_card, text="Cluster threshold", background="#fff8ef").grid(row=0, column=2, sticky="w")
        ttk.Entry(settings_card, textvariable=self.cluster_threshold, width=10).grid(row=1, column=2, sticky="w", pady=(6, 0))
        options = ttk.Frame(settings_card, style="FaceTrail.TFrame")
        options.grid(row=0, column=3, rowspan=2, sticky="e")
        ttk.Checkbutton(options, text="Open report when finished", variable=self.auto_open).pack(anchor="w")
        ttk.Checkbutton(options, text="Create ZIP package", variable=self.create_zip).pack(anchor="w")

        actions = ttk.Frame(outer, style="FaceTrail.TFrame")
        actions.pack(fill="x", pady=(16, 0))
        self.run_button = ttk.Button(actions, text="Start Scan", style="Primary.TButton", command=self._start_scan)
        self.run_button.pack(side="left")
        ttk.Button(actions, text="Open Last Report", command=self._open_last_report).pack(side="left", padx=(10, 0))

        status = ttk.Label(outer, textvariable=self.status_text, style="Status.TLabel", anchor="w", padding=12)
        status.pack(fill="x", pady=(16, 0))

        summary_card = ttk.LabelFrame(outer, text="Summary", style="Card.TLabelframe", padding=16)
        summary_card.pack(fill="both", expand=True, pady=(16, 0))
        ttk.Label(
            summary_card,
            textvariable=self.summary_text,
            background="#fff8ef",
            justify="left",
            anchor="nw",
            font=("Consolas", 10),
        ).pack(fill="both", expand=True)

    def _pick_folder(self) -> None:
        selected = filedialog.askdirectory(title="Choose a media folder")
        if selected:
            self.input_path.set(selected)
            self._refresh_preview()

    def _pick_file(self) -> None:
        selected = filedialog.askopenfilename(title="Choose an image or video")
        if selected:
            self.input_path.set(selected)
            self._refresh_preview()

    def _pick_output(self) -> None:
        selected = filedialog.askdirectory(title="Choose an output folder")
        if selected:
            self.output_path.set(selected)

    def _start_scan(self) -> None:
        input_value = self.input_path.get().strip()
        if not input_value:
            messagebox.showerror("FaceTrail", "Pick a file, video, or folder first.")
            return
        cluster_raw = self.cluster_threshold.get().strip().lower()
        cluster_threshold = None
        if cluster_raw and cluster_raw != "auto":
            try:
                cluster_threshold = float(cluster_raw)
            except ValueError:
                messagebox.showerror("FaceTrail", "Cluster threshold must be a number like 0.36, 0.92, or 'auto'.")
                return

        if self.run_button is not None:
            self.run_button.configure(state="disabled")
        self.status_text.set("Scanning media, tracking faces, and preparing outputs...")
        self.summary_text.set("Working...")

        worker = threading.Thread(
            target=self._run_scan,
            args=(
                input_value,
                self.output_path.get().strip() or "output",
                cluster_threshold,
                self.mode.get(),
                self.engine.get(),
                self.create_zip.get(),
            ),
            daemon=True,
        )
        worker.start()

    def _run_scan(
        self,
        input_value: str,
        output_value: str,
        cluster_threshold: float | None,
        mode: str,
        engine: str,
        create_zip: bool,
    ) -> None:
        try:
            target_output = self._build_mode_output(Path(output_value), mode)
            options = self._mode_options(mode)
            analyzer = FaceTrailAnalyzer(
                target_output,
                sample_every=self.sample_every.get(),
                min_face_size=self.min_face_size.get(),
                cluster_threshold=cluster_threshold,
                save_redacted=options["save_redacted"],
                save_crops=options["save_crops"],
                save_report=options["save_report"],
                engine=engine,
            )
            summary = analyzer.analyze(Path(input_value))
            zip_path = self._create_zip_package(target_output) if create_zip else None
            self.worker_queue.put(
                (
                    "success",
                    {
                        "summary": summary,
                        "output": str(target_output),
                        "mode": mode,
                        "zip_path": str(zip_path) if zip_path else "",
                    },
                )
            )
        except Exception as exc:
            self.worker_queue.put(("error", str(exc)))

    def _poll_worker_queue(self) -> None:
        try:
            kind, payload = self.worker_queue.get_nowait()
        except queue.Empty:
            self.root.after(150, self._poll_worker_queue)
            return

        if self.run_button is not None:
            self.run_button.configure(state="normal")

        if kind == "success":
            data = payload if isinstance(payload, dict) else {}
            summary = data.get("summary", {})
            mode = str(data.get("mode", "full_workspace"))
            output_path = Path(data.get("output", "output"))
            zip_path = Path(data["zip_path"]) if data.get("zip_path") else None
            report_path = output_path / "report" / "gallery.html"
            self.last_output_path = output_path
            self.last_zip_path = zip_path if zip_path and zip_path.exists() else None
            self.last_report_path = report_path if report_path.exists() else None
            self.status_text.set("Finished. Your files and export package are ready.")
            self.summary_text.set(self._format_summary(summary, output_path, mode, self.last_zip_path))
            if self.auto_open.get() and self.last_report_path is not None:
                webbrowser.open(self.last_report_path.resolve().as_uri())
        else:
            error_message = str(payload)
            self.status_text.set("Scan failed.")
            self.summary_text.set(error_message)
            messagebox.showerror("FaceTrail", error_message)

        self.root.after(150, self._poll_worker_queue)

    def _refresh_preview(self) -> None:
        if self.preview_label is None:
            return
        raw_path = self.input_path.get().strip()
        if not raw_path:
            self._set_preview_state("No media selected.", None)
            return

        path = Path(raw_path)
        if not path.exists():
            self._set_preview_state("Path does not exist yet.", None)
            return
        if path.is_dir():
            self._set_preview_state("Folder selected.\nFaceTrail will scan supported images and videos inside it.", None)
            return

        frame = self._load_preview_frame(path)
        if frame is None:
            self._set_preview_state("Preview unavailable for this file.", None)
            return

        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        image.thumbnail((360, 220))
        preview = ImageTk.PhotoImage(image=image)
        self.preview_photo = preview
        caption = f"{path.name}\nPreview loaded"
        self._set_preview_state(caption, preview)

    def _load_preview_frame(self, path: Path) -> np.ndarray | None:
        suffix = path.suffix.lower()
        if suffix in IMAGE_EXTENSIONS:
            return cv2.imread(str(path))
        if suffix in VIDEO_EXTENSIONS:
            cap = cv2.VideoCapture(str(path))
            ok, frame = cap.read()
            cap.release()
            return frame if ok else None
        return None

    def _set_preview_state(self, caption: str, preview: ImageTk.PhotoImage | None) -> None:
        self.preview_caption.set(caption)
        self.preview_photo = preview
        if self.preview_label is not None:
            self.preview_label.configure(image=preview)

    def _open_last_report(self) -> None:
        if self.last_report_path is None or not self.last_report_path.exists():
            messagebox.showinfo("FaceTrail", "No report is ready yet.")
            return
        webbrowser.open(self.last_report_path.resolve().as_uri())

    def _open_output_folder(self) -> None:
        if self.last_output_path is None or not self.last_output_path.exists():
            messagebox.showinfo("FaceTrail", "No output folder is ready yet.")
            return
        self._open_path(self.last_output_path)

    def _open_last_zip(self) -> None:
        if self.last_zip_path is None or not self.last_zip_path.exists():
            messagebox.showinfo("FaceTrail", "No ZIP package is ready yet.")
            return
        self._open_path(self.last_zip_path)

    def _open_path(self, path: Path) -> None:
        if sys.platform.startswith("win"):
            os.startfile(str(path))
            return
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.Popen([opener, str(path)])

    def _create_zip_package(self, output_path: Path) -> Path:
        archive_base = output_path.parent / output_path.name
        archive_path = Path(shutil.make_archive(str(archive_base), "zip", root_dir=output_path.parent, base_dir=output_path.name))
        return archive_path

    def _format_summary(self, summary: dict, output_path: Path, mode: str, zip_path: Path | None) -> str:
        mode_labels = {
            "extract_faces": "Extract faces + report",
            "privacy_blur": "Blur faces in media",
            "full_workspace": "Full workspace",
        }
        lines = [
            f"Mode: {mode_labels.get(mode, mode)}",
            f"Output folder: {output_path}",
            f"ZIP package: {zip_path if zip_path else 'disabled'}",
            f"Engine: {summary.get('engine', 'unknown')}",
            f"Faces detected: {summary.get('faces_detected', 0)}",
            f"Tracks detected: {summary.get('tracks_detected', 0)}",
            f"Clusters: {summary.get('people_clustered', 0)}",
            f"Images: {summary.get('input_images', 0)}",
            f"Videos: {summary.get('input_videos', 0)}",
            "",
            "Expected folders:",
        ]
        if mode == "extract_faces":
            lines.extend(["- faces", "- report"])
        elif mode == "privacy_blur":
            lines.extend(["- redacted"])
        else:
            lines.extend(["- faces", "- redacted", "- report"])

        lines.extend(
            [
                "",
                "Top clusters:",
            ]
        )
        for person in summary.get("people", [])[:5]:
            lines.append(
                f"- Cluster {person['cluster_id']}: {person['detections']} detections | avg sharpness {person['avg_sharpness']}"
            )
        if not summary.get("people"):
            lines.append("- No clusters detected.")
        return "\n".join(lines)

    def _mode_options(self, mode: str) -> dict[str, bool]:
        if mode == "extract_faces":
            return {"save_crops": True, "save_redacted": False, "save_report": True}
        if mode == "privacy_blur":
            return {"save_crops": False, "save_redacted": True, "save_report": False}
        return {"save_crops": True, "save_redacted": True, "save_report": True}

    def _build_mode_output(self, base_output: Path, mode: str) -> Path:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        suffix = {
            "extract_faces": "extract_faces",
            "privacy_blur": "privacy_blur",
            "full_workspace": "full_workspace",
        }.get(mode, "run")
        return base_output / suffix / stamp

    def _save_last_zip_as(self) -> None:
        if self.last_zip_path is None or not self.last_zip_path.exists():
            messagebox.showinfo("FaceTrail", "No ZIP package is ready yet.")
            return
        destination = filedialog.asksaveasfilename(
            title="Save result ZIP as",
            defaultextension=".zip",
            initialfile=self.last_zip_path.name,
            filetypes=[("ZIP archive", "*.zip")],
        )
        if not destination:
            return
        shutil.copy2(self.last_zip_path, destination)
        messagebox.showinfo("FaceTrail", f"ZIP saved to:\n{destination}")
