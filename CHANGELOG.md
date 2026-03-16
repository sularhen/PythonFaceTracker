# Changelog

## 1.3.0 - 2026-03-15

- Made `facetrail` open the desktop GUI by default.
- Added root launchers for cloned repos and release packages on Windows and Linux.
- Added GUI ZIP export copy via "Save ZIP As...".
- Organized output history inside per-mode folders.

## 1.2.0 - 2026-03-15

- Added temporal face tracking across video frames.
- Added GUI media preview for images and video first frames.
- Added automatic ZIP export packages from the GUI output.
- Added quick-open actions for output folders and ZIP files.
- Added terminal walkthrough support in the documentation.

## 1.1.0 - 2026-03-15

- Added a pro engine based on OpenCV YuNet face detection and SFace recognition.
- Added automatic download and caching of official OpenCV Zoo face models.
- Added engine selection and automatic fallback to legacy Haar mode.
- Improved clustering quality with engine-specific defaults.
- Kept only the best crop per detected face cluster.

## 1.0.0 - 2026-03-15

- Rebuilt the repository as the `facetrail` Python package.
- Added a proper CLI for image and video analysis.
- Added face crop extraction, clustering, sharpness ranking, and reporting.
- Added privacy-safe redacted exports for images and videos.
- Replaced the old README with bilingual documentation and a project banner.
- Added release packaging for Windows `.zip` and Linux `.tar.gz`.
