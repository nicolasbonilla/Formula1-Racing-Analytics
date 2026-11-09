"""Data-flow (architecture) diagram of the whole project, drawn from the generated outputs.

Zones follow the usual data-engineering layering: an immutable raw zone, a validated clean zone and
curated / serving products, with cross-cutting controls (schema contract, validation gates, lineage,
orchestration, tests) along the bottom.
"""
from __future__ import annotations

import pandas as pd

from src import config
from src import plot_style as ps

ps.apply()
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

OUT_DIR = config.OUTPUT_DIR / "architecture"
ZONE_COLORS = {"source": ps.NEUTRAL, "raw": ps.CATEGORICAL[3], "quality": ps.CATEGORICAL[1],
               "clean": ps.CATEGORICAL[0], "serve": ps.CATEGORICAL[2]}


def numbers() -> dict:
    issues = pd.read_csv(config.QUALITY_DIR / "quality_issues.csv")
    gates = pd.read_csv(config.CLEANING_DIR / "validation_report.csv")
    passed = pd.read_csv(config.QUALITY_DIR / "passed_checks.csv")
    clean = pd.read_csv(config.CLEAN_RESULTS_CSV)
    manifest = pd.read_csv(config.SOURCE_MANIFEST_CSV)
    edges = pd.read_csv(config.GRAPH_DIR / "property_graph_edge_counts.csv")["count"].sum()
    return {"files": len(manifest), "issues": len(issues), "dims": issues["dimension"].nunique(),
            "passed": len(passed), "gates": len(gates), "rows": len(clean), "cols": clean.shape[1],
            "edges": int(edges)}


def box(ax, x, y, w, h, title, body, zone, emphasis=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.012",
                                facecolor="#ffffff" if not emphasis else "#f1ecff",
                                edgecolor=ZONE_COLORS[zone], linewidth=1.3))
    ax.add_patch(FancyBboxPatch((x, y + h - 0.012), w, 0.012, boxstyle="square,pad=0",
                                facecolor=ZONE_COLORS[zone], edgecolor="none"))
    ax.text(x + 0.012, y + h - 0.03, title, fontsize=8.0, fontweight="bold", va="top", color=ps.INK)
    ax.text(x + 0.012, y + h - 0.07, body, fontsize=7.1, va="top", color=ps.INK_SECONDARY, linespacing=1.25)


def arrow(ax, x1, y1, x2, y2, rad=0.0):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=9, color=ps.INK_MUTED,
                                 linewidth=1.0, connectionstyle=f"arc3,rad={rad}", shrinkA=1, shrinkB=1))


def draw(path) -> None:
    n = numbers()
    fig, ax = plt.subplots(figsize=(7.6, 4.7))
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.86)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    cols = [0.0, 0.197, 0.394, 0.591, 0.826]
    w = 0.178
    heads = [("Source", "source"), ("Raw zone (bronze)", "raw"), ("Quality (B)", "quality"),
             ("Clean zone (silver)", "clean"), ("Served (gold)", "serve")]
    for x, (label, zone) in zip(cols, heads):
        ax.text(x, 0.985, label, fontsize=8.6, fontweight="bold", va="top",
                color=ZONE_COLORS[zone] if zone != "source" else ps.INK_SECONDARY)

    top, mid, low = (0.75, 0.16), (0.53, 0.16), (0.31, 0.16)
    box(ax, cols[0], *top[:1], w, top[1], "Ergast / Jolpica", "public F1 API\nCC BY-NC-SA 4.0", "source")
    box(ax, cols[0], *mid[:1], w, mid[1], "racing_f1_data.zip", f"{n['files']} files, JSON + CSV\nSHA-256 pinned",
        "source")
    box(ax, cols[1], *top[:1], w, top[1], "Step 0: extract", "format detection\nlineage: file + line", "raw")
    box(ax, cols[1], *mid[:1], w, mid[1], "data/raw", "5 CSV tables\nvalues unchanged", "raw")
    box(ax, cols[2], *top[:1], w, top[1], "Profiling", f"{n['issues']} issues\n{n['dims']} dimensions",
        "quality")
    box(ax, cols[2], *mid[:1], w, mid[1], "Issue register", "contract B to C\nevidence + fix step", "quality")
    box(ax, cols[3], *top[:1], w, top[1], "Cleaning", "12 audited steps\nraw + register in", "clean")
    box(ax, cols[3], *mid[:1], w, mid[1], "Validation gates", f"{n['gates']} checks\nfail-fast", "clean")
    box(ax, cols[3], *low[:1], w, low[1], "data/cleaned", f"{n['rows']:,} x {n['cols']}\n+ 4 reference tables",
        "clean")
    serve = [("FAIR record (A)", "DataCite, PROV-O\nschema.org", False),
             ("Property graph", f"NetworkX\n{n['edges']:,} edges", False),
             ("Dashboard", "7 interactive\nviews", True),
             ("Report, slides", "generated\nfrom outputs", False)]
    sy = [0.79, 0.615, 0.44, 0.265]
    for y, (t, b, emph) in zip(sy, serve):
        box(ax, cols[4], y, 0.17, 0.135, t, b, "serve", emphasis=emph)

    arrow(ax, cols[0] + w / 2, top[0], cols[0] + w / 2, mid[0] + mid[1])
    arrow(ax, cols[0] + w, mid[0] + 0.08, cols[1], top[0] + 0.08)
    arrow(ax, cols[1] + w / 2, top[0], cols[1] + w / 2, mid[0] + mid[1])
    arrow(ax, cols[1] + w, mid[0] + 0.08, cols[2], top[0] + 0.08)
    arrow(ax, cols[2] + w / 2, top[0], cols[2] + w / 2, mid[0] + mid[1])
    arrow(ax, cols[2] + w, mid[0] + 0.08, cols[3], top[0] + 0.08)
    arrow(ax, cols[3] + w / 2, top[0], cols[3] + w / 2, mid[0] + mid[1])
    arrow(ax, cols[3] + w / 2, mid[0], cols[3] + w / 2, low[0] + low[1])
    for i, y in enumerate(sy):
        arrow(ax, cols[3] + w, low[0] + 0.125 - i * 0.03, cols[4], y + 0.0675)
    ax.text(cols[2], 0.47, "Feedback loop:\nissue B29 came from\nthe dashboard",
            fontsize=7.0, color=ps.CATEGORICAL[6], va="top", linespacing=1.25)

    ax.add_patch(FancyBboxPatch((0.0, 0.02), 0.996, 0.185, boxstyle="round,pad=0,rounding_size=0.012",
                                facecolor="#f4f3ef", edgecolor="none"))
    ax.text(0.015, 0.19, "Cross-cutting engineering controls", fontsize=8.2, fontweight="bold", va="top",
            color=ps.INK)
    controls = [("Schema as code", "schema.py, vocabularies.py:\none contract for C and A"),
                ("Orchestration", "run_all.py: one command,\nbyte-identical reruns"),
                ("Automated tests", "pytest on key decisions\n(order, keys, sentinels)"),
                ("Lineage", "file + line per row,\nchecksums, PROV-O")]
    for i, (t, b) in enumerate(controls):
        x = 0.015 + i * 0.248
        ax.text(x, 0.135, t, fontsize=7.6, fontweight="bold", va="top", color=ps.INK)
        ax.text(x, 0.098, b, fontsize=7.0, va="top", color=ps.INK_SECONDARY, linespacing=1.25)

    ps.titles(ax, "End-to-end data flow: from the raw archive to the dashboard",
              "Every arrow is code in run_all.py; each zone reads only the zone before it.")
    ps.source_note(fig, "Numbers read from the generated outputs; group project, Data Management 2026/27.")
    ps.save(fig, path)


def run() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    draw(OUT_DIR / "fig_e1_data_flow.png")
    print("[architecture] data-flow diagram written")


if __name__ == "__main__":
    run()
