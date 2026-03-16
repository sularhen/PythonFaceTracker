from __future__ import annotations

import shutil
import tarfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
STAGING = DIST / "staging"
PROJECT_NAME = "facetrail"
VERSION = "1.3.0"

INCLUDE_PATHS = [
    "README.md",
    "README.es.md",
    "LICENSE",
    "CHANGELOG.md",
    "pyproject.toml",
    "facetrail.bat",
    "facetrail.ps1",
    "facetrail.sh",
    "python_code_for_images",
    "python_code_for_videos",
    "assets",
    "scripts",
    "src",
]


def main() -> int:
    DIST.mkdir(exist_ok=True)
    if STAGING.exists():
        shutil.rmtree(STAGING)
    package_root = STAGING / f"{PROJECT_NAME}-v{VERSION}"
    package_root.mkdir(parents=True, exist_ok=True)

    for relative_path in INCLUDE_PATHS:
        source = ROOT / relative_path
        destination = package_root / relative_path
        if source.is_dir():
            shutil.copytree(source, destination, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", "*.egg-info"))
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    windows_archive = DIST / f"{PROJECT_NAME}-windows-v{VERSION}.zip"
    linux_archive = DIST / f"{PROJECT_NAME}-linux-v{VERSION}.tar.gz"

    if windows_archive.exists():
        windows_archive.unlink()
    if linux_archive.exists():
        linux_archive.unlink()

    with zipfile.ZipFile(windows_archive, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in package_root.rglob("*"):
            if file_path.is_file():
                archive.write(file_path, file_path.relative_to(STAGING))

    with tarfile.open(linux_archive, "w:gz") as archive:
        archive.add(package_root, arcname=package_root.name)

    print(f"Created {windows_archive}")
    print(f"Created {linux_archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
