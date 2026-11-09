"""Package the group submission ZIP (deliverables 1-8 of the assignment).

Reflection logs (deliverable 9) are submitted individually and are therefore NOT included.

    python build_submission.py
"""
from __future__ import annotations

import hashlib
import re
import zipfile
from pathlib import Path

from docx import Document
from docx.shared import Pt

from src import config

ROOT = config.PROJECT_ROOT
DIST = ROOT / "dist"
ZIP_PATH = DIST / "F1_DataManagement_Group_Submission.zip"

INCLUDE = [
    "README.md", "requirements.txt", "run_all.py", "build_submission.py",
    "src/*.py", "tests/*.py",
    "data/source/*", "data/raw/*", "data/cleaned/*", "data/reference/**/*",
    "outputs/**/*",
    "report/*.docx", "report/*.pdf", "report/presentation/*",
]
EXCLUDE = re.compile(r"(__pycache__|\.pytest_cache|\.pyc$|~\$)")
DASHBOARD_INCLUDE = ["app.py", "build_web_data.py", "static/*", "static/vendor/*"]


def reflection_docx() -> None:
    """Word versions of the reflection drafts for each student to personalise (not part of the ZIP)."""
    for md in sorted((config.REPORT_DIR / "reflection_drafts").glob("*.md")):
        doc = Document()
        doc.styles["Normal"].font.name = "Calibri"
        doc.styles["Normal"].font.size = Pt(11)
        for block in md.read_text(encoding="utf-8").split("\n\n"):
            block = block.strip()
            if not block:
                continue
            if block.startswith("# "):
                doc.add_heading(block[2:], level=1)
                continue
            para = doc.add_paragraph()
            text = " ".join(line.lstrip("> ").strip() for line in block.splitlines())
            for part in re.split(r"(\*\*[^*]+\*\*)", text):
                run = para.add_run(part.strip("*") if part.startswith("**") else part)
                run.bold = part.startswith("**")
                run.italic = block.startswith(">")
        doc.save(md.with_suffix(".docx"))


def main() -> None:
    reflection_docx()
    DIST.mkdir(exist_ok=True)
    files = sorted({p for pattern in INCLUDE for p in ROOT.glob(pattern)
                    if p.is_file() and not EXCLUDE.search(p.as_posix())})
    dash_files = sorted({p for pattern in DASHBOARD_INCLUDE for p in config.DASHBOARD_DIR.glob(pattern)
                         if p.is_file() and not EXCLUDE.search(p.as_posix())})
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            zf.write(path, Path("F1_DataManagement_Group") / path.relative_to(ROOT))
        for path in dash_files:
            zf.write(path, Path("F1_DataManagement_Group") / "dashboard" / path.relative_to(config.DASHBOARD_DIR))
    files += dash_files
    digest = hashlib.sha256(ZIP_PATH.read_bytes()).hexdigest()
    print(f"[submission] {len(files)} files -> {ZIP_PATH.relative_to(ROOT)} "
          f"({ZIP_PATH.stat().st_size / 1e6:.1f} MB, sha256 {digest[:16]}...)")


if __name__ == "__main__":
    main()
