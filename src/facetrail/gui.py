from __future__ import annotations

import queue
import threading
import webbrowser
from datetime import datetime
from pathlib import Path
from tkinter import BooleanVar, IntVar, StringVar, Tk, filedialog, messagebox, ttk

from facetrail.core import FaceTrailAnalyzer


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
        self.root.geometry("860x640")
        self.root.minsize(760, 580)

        self.input_path = StringVar(value=start_input)
        self.output_path = StringVar(value="output")
        self.sample_every = IntVar(value=5)
        self.min_face_size = IntVar(value=64)
        self.cluster_threshold = StringVar(value="0.92")
        self.mode = StringVar(value="full_workspace")
        self.auto_open = BooleanVar(value=True)
        self.status_text = StringVar(value="Choose a file or folder and press Start Scan.")
        self.summary_text = StringVar(value="No scan yet.")
        self.run_button: ttk.Button | None = None
        self.last_report_path: Path | None = None
        self.worker_queue: queue.Queue[tuple[str, str | dict]] = queue.Queue()

        self._build_layout()
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

        outer = ttk.Frame(self.root, style="FaceTrail.TFrame", padding=18)
        outer.pack(fill="both", expand=True)

        hero = ttk.Frame(outer, style="Hero.TFrame", padding=22)
        hero.pack(fill="x")
        ttk.Label(hero, text="FaceTrail", foreground="#fff8ef", background="#132930", font=("Segoe UI", 28, "bold")).pack(anchor="w")
        ttk.Label(
            hero,
            text="Desktop face review for people who just want to pick media, click start, and get a usable report.",
            foreground="#d8d2c9",
            background="#132930",
            font=("Segoe UI", 11),
            wraplength=760,
        ).pack(anchor="w", pady=(8, 0))

        body = ttk.Frame(outer, style="FaceTrail.TFrame")
        body.pack(fill="both", expand=True, pady=(16, 0))
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

        output_card = ttk.LabelFrame(body, text="Results", style="Card.TLabelframe", padding=16)
        output_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        output_card.columnconfigure(0, weight=1)
        ttk.Label(output_card, text="Output folder", background="#fff8ef").grid(row=0, column=0, sticky="w")
        ttk.Entry(output_card, textvariable=self.output_path).grid(row=1, column=0, sticky="ew", pady=(6, 10))
        ttk.Button(output_card, text="Choose Output", command=self._pick_output).grid(row=2, column=0, sticky="w")

        mode_card = ttk.LabelFrame(outer, text="Choose What You Want", style="Card.TLabelframe", padding=16)
        mode_card.pack(fill="x", pady=(16, 0))
        ttk.Radiobutton(
            mode_card,
            text="Extract faces + report",
            value="extract_faces",
            variable=self.mode,
        ).pack(anchor="w")
        ttk.Radiobutton(
            mode_card,
            text="Blur faces in the original media",
            value="privacy_blur",
            variable=self.mode,
        ).pack(anchor="w", pady=(6, 0))
        ttk.Radiobutton(
            mode_card,
            text="Full workspace: crops + report + blurred exports",
            value="full_workspace",
            variable=self.mode,
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
        ttk.Entry(settings_card, textvariable=self.cluster_threshold, width=8).grid(row=1, column=2, sticky="w", pady=(6, 0))
        options = ttk.Frame(settings_card, style="FaceTrail.TFrame")
        options.grid(row=0, column=3, rowspan=2, sticky="e")
        ttk.Checkbutton(options, text="Open report when finished", variable=self.auto_open).pack(anchor="w")

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

    def _pick_file(self) -> None:
        selected = filedialog.askopenfilename(title="Choose an image or video")
        if selected:
            self.input_path.set(selected)

    def _pick_output(self) -> None:
        selected = filedialog.askdirectory(title="Choose an output folder")
        if selected:
            self.output_path.set(selected)

    def _start_scan(self) -> None:
        input_value = self.input_path.get().strip()
        if not input_value:
            messagebox.showerror("FaceTrail", "Pick a file or folder first.")
            return
        try:
            cluster_threshold = float(self.cluster_threshold.get())
        except ValueError:
            messagebox.showerror("FaceTrail", "Cluster threshold must be a number like 0.92.")
            return

        if self.run_button is not None:
            self.run_button.configure(state="disabled")
        self.status_text.set("Scanning media and building the report...")
        self.summary_text.set("Working...")

        worker = threading.Thread(
            target=self._run_scan,
            args=(input_value, self.output_path.get().strip() or "output", cluster_threshold, self.mode.get()),
            daemon=True,
        )
        worker.start()

    def _run_scan(self, input_value: str, output_value: str, cluster_threshold: float, mode: str) -> None:
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
            )
            summary = analyzer.analyze(Path(input_value))
            self.worker_queue.put(("success", {"summary": summary, "output": str(target_output), "mode": mode}))
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
            report_path = Path(data.get("output", "output")) / "report" / "gallery.html"
            self.last_report_path = report_path if report_path.exists() else None
            self.status_text.set("Finished. Your files are ready.")
            self.summary_text.set(self._format_summary(summary, Path(data.get("output", "output")), mode))
            if self.auto_open.get() and self.last_report_path is not None:
                webbrowser.open(report_path.resolve().as_uri())
        else:
            error_message = str(payload)
            self.status_text.set("Scan failed.")
            self.summary_text.set(error_message)
            messagebox.showerror("FaceTrail", error_message)

        self.root.after(150, self._poll_worker_queue)

    def _open_last_report(self) -> None:
        if self.last_report_path is None or not self.last_report_path.exists():
            messagebox.showinfo("FaceTrail", "No report is ready yet.")
            return
        webbrowser.open(self.last_report_path.resolve().as_uri())

    def _format_summary(self, summary: dict, output_path: Path, mode: str) -> str:
        mode_labels = {
            "extract_faces": "Extract faces + report",
            "privacy_blur": "Blur faces in media",
            "full_workspace": "Full workspace",
        }
        lines = [
            f"Mode: {mode_labels.get(mode, mode)}",
            f"Output folder: {output_path}",
            f"Faces detected: {summary.get('faces_detected', 0)}",
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
        return base_output / f"{suffix}_{stamp}"
