from __future__ import annotations

import argparse
import webbrowser
from pathlib import Path

from facetrail import __version__
from facetrail.core import FaceTrailAnalyzer
from facetrail.gui import launch_gui


def parse_cluster_threshold(value: str) -> float | None:
    if value.lower() == "auto":
        return None
    return float(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="facetrail",
        description="Scan image/video libraries, extract faces, cluster similar appearances, and create privacy-safe copies.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Analyze a file or folder and export a report.")
    scan_parser.add_argument("input", help="Image, video, or folder to process.")
    scan_parser.add_argument(
        "-o",
        "--output",
        default="output",
        help="Folder where crops, reports, and redacted media will be written.",
    )
    scan_parser.add_argument(
        "--sample-every",
        type=int,
        default=5,
        help="Process every Nth frame in videos.",
    )
    scan_parser.add_argument(
        "--min-face-size",
        type=int,
        default=64,
        help="Ignore detections smaller than this size in pixels.",
    )
    scan_parser.add_argument(
        "--cluster-threshold",
        type=parse_cluster_threshold,
        default=None,
        help="Similarity threshold. Use 'auto' to apply the engine default.",
    )
    scan_parser.add_argument(
        "--engine",
        choices=("auto", "pro", "classic"),
        default="auto",
        help="Detection and recognition engine. 'auto' tries the pro engine first and falls back if needed.",
    )
    scan_parser.add_argument(
        "--save-redacted",
        action="store_true",
        help="Write privacy-safe copies with all detected faces blurred.",
    )
    scan_parser.add_argument(
        "--open-report",
        action="store_true",
        help="Open the generated HTML report in your default browser when done.",
    )

    gui_parser = subparsers.add_parser("gui", help="Launch the local desktop interface.")
    gui_parser.add_argument(
        "--start-input",
        default="",
        help="Optional file or folder to prefill in the interface.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        analyzer = FaceTrailAnalyzer(
            Path(args.output),
            sample_every=args.sample_every,
            min_face_size=args.min_face_size,
            cluster_threshold=args.cluster_threshold,
            save_redacted=args.save_redacted,
            engine=args.engine,
        )
        summary = analyzer.analyze(Path(args.input))
        print(
            "FaceTrail finished. "
            f"Faces: {summary['faces_detected']} | Tracks: {summary.get('tracks_detected', 0)} | "
            f"Clusters: {summary['people_clustered']}"
        )
        print(f"Engine: {summary['engine']}")
        report_path = Path(args.output) / "report" / "gallery.html"
        print(f"Report: {report_path}")
        if args.open_report:
            webbrowser.open(report_path.resolve().as_uri())
        return 0

    if args.command == "gui":
        launch_gui(args.start_input)
        return 0

    parser.error("Unknown command")
    return 2
