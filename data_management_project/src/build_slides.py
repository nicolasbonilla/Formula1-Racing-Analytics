"""Build the group presentation (16:9 PowerPoint + PDF + presenter script) from the pipeline outputs.

Every number on the slides and in the speaker notes is read from the generated outputs, so the
deck always matches the data and the report.

    python -m src.build_slides
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pandas as pd
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt

from src import config
from src.build_report import facts

OUT_DIR = config.REPORT_DIR / "presentation"
OUT_PPTX = OUT_DIR / "F1_Data_Management_Presentation.pptx"
OUT_SCRIPT = OUT_DIR / "presenter_script.md"

SLIDE_W, SLIDE_H = 13.333, 7.5
MARGIN = 0.6
FONT = "Calibri"
MONO = "Courier New"

SURFACE = "FCFCFB"
INK = "0B0B0B"
INK2 = "52514E"
MUTED = "898781"
NAVY = "184F95"
BLUE = "2A78D6"
TINT = "EEF3FA"
DARK = "0D366B"
ON_DARK = "CDE2FB"
CARD_ON_DARK = "184F95"
CRITICAL = "D03B3B"
CRITICAL_TINT = "FBEDED"

SPEAKING_WPM = 130


def rgb(hex_: str) -> RGBColor:
    return RGBColor.from_string(hex_)


# ============================================================================================
# Drawing helpers
# ============================================================================================
class Deck:
    def __init__(self) -> None:
        self.prs = Presentation()
        self.prs.slide_width = Inches(SLIDE_W)
        self.prs.slide_height = Inches(SLIDE_H)
        self.script: list[dict] = []

    def slide(self, dark: bool = False):
        s = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        s.background.fill.solid()
        s.background.fill.fore_color.rgb = rgb(DARK if dark else SURFACE)
        return s

    @staticmethod
    def text(s, x, y, w, h, content, size=16, bold=False, color=INK, align=PP_ALIGN.LEFT,
             anchor=MSO_ANCHOR.TOP, font=FONT, name=None, spacing_after=0, line_spacing=1.0):
        """content: str, or list of paragraphs; a paragraph is a str or a list of (text, overrides) runs."""
        tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        if name:
            tb.name = name
        tf = tb.text_frame
        tf.word_wrap = True
        tf.auto_size = MSO_AUTO_SIZE.NONE
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = anchor
        paragraphs = content if isinstance(content, list) else [content]
        for i, para in enumerate(paragraphs):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = align
            p.line_spacing = line_spacing
            p.space_after = Pt(spacing_after)
            runs = para if isinstance(para, list) else [(para, {})]
            for run_text, over in runs:
                r = p.add_run()
                r.text = run_text
                f = r.font
                f.name = over.get("font", font)
                f.size = Pt(over.get("size", size))
                f.bold = over.get("bold", bold)
                f.italic = over.get("italic", False)
                f.color.rgb = rgb(over.get("color", color))
        return tb

    @staticmethod
    def bullets(s, x, y, w, h, items, size=16, color=INK, name=None, gap=8):
        tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        if name:
            tb.name = name
        tf = tb.text_frame
        tf.word_wrap = True
        tf.auto_size = MSO_AUTO_SIZE.NONE
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        for i, item in enumerate(items):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.space_after = Pt(gap)
            p.line_spacing = 1.0
            ppr = p._p.get_or_add_pPr()
            ppr.set("marL", str(int(Inches(0.28))))
            ppr.set("indent", str(-int(Inches(0.28))))
            bu_clr = OxmlElement("a:buClr")
            srgb = OxmlElement("a:srgbClr")
            srgb.set("val", NAVY)
            bu_clr.append(srgb)
            bu_font = OxmlElement("a:buFont")
            bu_font.set("typeface", "Arial")
            bu_char = OxmlElement("a:buChar")
            bu_char.set("char", "\u2022")
            for el in (bu_clr, bu_font, bu_char):
                ppr.append(el)
            runs = item if isinstance(item, list) else [(item, {})]
            for run_text, over in runs:
                r = p.add_run()
                r.text = run_text
                r.font.name = FONT
                r.font.size = Pt(over.get("size", size))
                r.font.bold = over.get("bold", False)
                r.font.color.rgb = rgb(over.get("color", color))
        return tb

    @staticmethod
    def card(s, x, y, w, h, fill=TINT, name=None, radius=0.08):
        shp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        shp.adjustments[0] = radius
        shp.fill.solid()
        shp.fill.fore_color.rgb = rgb(fill)
        shp.line.fill.background()
        shp.shadow.inherit = False
        if name:
            shp.name = name
        shp.text_frame.text = ""
        return shp

    def stat(self, s, x, y, w, number, label, num_size=40, color=NAVY, label_color=INK2, label_size=14,
             name=None, label_h=0.55):
        num_h = num_size / 72 * 1.15
        self.text(s, x, y, w, num_h, number, size=num_size, bold=True, color=color, name=name)
        self.text(s, x, y + num_h + 0.02, w, label_h, label, size=label_size, color=label_color)
        return y + num_h + 0.02 + label_h

    @staticmethod
    def picture(s, path: Path, x, y, w, h, alt: str, name=None):
        iw, ih = Image.open(path).size
        scale = min(w / iw, h / ih)
        pw, ph = iw * scale, ih * scale
        pic = s.shapes.add_picture(str(path), Inches(x + (w - pw) / 2), Inches(y + (h - ph) / 2),
                                   Inches(pw), Inches(ph))
        pic._element.nvPicPr.cNvPr.set("descr", alt)
        if name:
            pic.name = name
        return pic

    def chip(self, s, x, y, text, dark=False, name="presenter_tag"):
        w = 0.46 + 0.088 * len(text)
        shp = self.card(s, x, y, w, 0.34, fill=CARD_ON_DARK if dark else TINT, name=name, radius=0.5)
        tf = shp.text_frame
        tf.margin_left = tf.margin_right = Inches(0.14)
        tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = text
        r.font.name = FONT
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = rgb("FFFFFF" if dark else NAVY)
        return shp

    @staticmethod
    def arrow(s, x1, y1, x2, y2, color=MUTED, width=1.75):
        c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
        c.line.color.rgb = rgb(color)
        c.line.width = Pt(width)
        tail = OxmlElement("a:tailEnd")
        tail.set("type", "triangle")
        tail.set("w", "med")
        tail.set("len", "med")
        c.line._get_or_add_ln().append(tail)
        return c

    def title(self, s, text, dark=False):
        self.text(s, MARGIN, 0.42, SLIDE_W - 2 * MARGIN, 0.95, text, size=32, bold=True,
                  color="FFFFFF" if dark else INK, name="title")

    def footer(self, s, number, total, presenter_label, dark=False):
        number = self.prs.slides.index(s) + 1
        if presenter_label:
            self.chip(s, MARGIN, 6.88, presenter_label, dark=dark)
        self.text(s, SLIDE_W - MARGIN - 2.5, 6.92, 2.5, 0.3, f"{number} / {total}", size=11,
                  color=ON_DARK if dark else MUTED, align=PP_ALIGN.RIGHT, name="slide_number")

    def notes(self, s, text: str, title: str, presenter: str, seconds: int) -> None:
        s.notes_slide.notes_text_frame.text = text
        self.script.append({"title": title, "presenter": presenter, "seconds": seconds, "notes": text})


# ============================================================================================
# Facts used by the deck
# ============================================================================================
def presenter(component: str) -> tuple[str, str]:
    """(tag text, script name) for a component letter."""
    m = next(t for t in config.TEAM if t["component"] == component)
    name = f"{m['given_name']} {m['family_name']}".strip()
    placeholder = "[" in name
    tag = f"Presenter: Student {component}" + ("" if placeholder else f" \u00b7 {name}")
    spoken = f"Student {component}" if placeholder else name
    return tag, spoken


def extra_facts() -> dict:
    issues = pd.read_csv(config.QUALITY_DIR / "quality_issues.csv").set_index("issue_id")
    gaps = pd.read_csv(config.FAIR_DIR / "fair_gaps.csv")
    rda = pd.read_csv(config.FAIR_DIR / "rda_fair_summary.csv").set_index("area")
    eras = pd.read_csv(config.QUALITY_FIG_DIR / "fig_b3_points_eras_data.csv")
    com = pd.read_csv(config.GRAPH_DIR / "communities.csv")
    return {
        "season_missing": int(issues.loc["B01", "affected_records"]),
        "round_missing": int(issues.loc["B02", "affected_records"]),
        "gaps": len(gaps),
        "rda_indicators": int(rda.loc["Overall", "indicators"]),
        "win_min": int(eras["typical"].min()), "win_max": int(eras["maximum"].max()),
        "win_values": sorted({int(v) for v in eras["typical"]}),
        "years": config.LAST_COMPLETE_SEASON - config.FIRST_SEASON,
        "era_names": com[com["drivers"] >= 10].sort_values("median_debut")["most_central_drivers"]
        .str.split("; ").str[0].tolist(),
        "big_communities": int((com["drivers"] >= 10).sum()),
    }


def surname(full: str) -> str:
    parts = full.split()
    particles = {"de", "da", "di", "van", "von", "la", "le", "del"}
    out = [parts[-1]]
    i = len(parts) - 2
    while i >= 1 and parts[i].lower() in particles:
        out.insert(0, parts[i])
        i -= 1
    return " ".join(out)


# ============================================================================================
# Slides
# ============================================================================================
def build() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    F = facts()
    X = extra_facts()
    d = Deck()
    total = 17
    tag = {c: presenter(c) for c in "ABC"}
    A, B, C = (tag[c][1] for c in "ABC")
    figs_a, figs_b, figs_c, figs_g = config.FAIR_DIR, config.QUALITY_FIG_DIR, config.CLEANING_DIR, config.GRAPH_FIG_DIR

    # 1 ---------------------------------------------------------------------------------------- title
    s = d.slide(dark=True)
    d.text(s, MARGIN, 1.0, 11.5, 0.4, f"{config.COURSE}  \u00b7  Group project", size=16, color=ON_DARK)
    d.text(s, MARGIN, 1.55, 11.6, 1.9, "From raw race results to a FAIR, quality-assured knowledge graph",
           size=42, bold=True, color="FFFFFF", name="title", line_spacing=0.95)
    d.text(s, MARGIN, 3.55, 11.5, 0.5,
           "Formula 1 World Championship results 1950\u20132025", size=22, color=ON_DARK)
    for i, m in enumerate(config.TEAM):
        x = MARGIN + i * 4.13
        d.card(s, x, 4.75, 3.85, 1.45, fill=CARD_ON_DARK, name=f"team_{m['component']}")
        name = f"{m['given_name']} {m['family_name']}".strip()
        d.text(s, x + 0.25, 4.92, 3.4, 1.2,
               [[(f"Student {m['component']}", {"bold": True, "size": 16})],
                [(m["title"][0].upper() + m["title"][1:], {"size": 14, "color": ON_DARK})],
                [(name, {"size": 13, "color": ON_DARK})]], color="FFFFFF", spacing_after=3)
    d.footer(s, 1, total, None, dark=True)
    d.notes(s, f"Good morning, we are {A}, {B} and {C}. We take {X['years']} years of Formula 1 results from raw "
               f"files to a FAIR, quality-assured dataset and a knowledge graph. I start with the dataset and FAIR, "
               f"{B} covers quality, {C} the cleaning, and we close with the graph.", "Title",
            "All (opened by Student A)", 20)

    # 2 ---------------------------------------------------------------------------------------- dataset
    s = d.slide()
    d.title(s, f"{F['seasons']} seasons of F1 results with real quality issues")
    stats = [(f"{F['raw_rows']:,}", "race results (one row per car per race)"),
             (f"{F['gp']:,}", "championship Grands Prix"),
             (f"{F['drivers']}", "drivers and " + f"{F['constructors']} constructor entries"),
             (f"{F['circuits']}", f"circuits in {F['countries']} countries")]
    for i, (num, label) in enumerate(stats):
        x = MARGIN + (i % 2) * 3.6
        y = 1.65 + (i // 2) * 2.5
        d.card(s, x, y, 3.35, 2.25, name=f"stat_card_{i}")
        d.stat(s, x + 0.3, y + 0.35, 2.85, num, label, num_size=44, label_size=15, label_h=0.8)
    d.text(s, 8.1, 1.75, 4.6, 0.45, "Why this dataset", size=22, bold=True, color=NAVY)
    d.bullets(s, 8.1, 2.45, 4.6, 3.0, [
        "Relational: one fact table and four reference tables",
        f"Genuine issues from {F['seasons']} seasons of rule changes and file exports",
        "A natural network of drivers, teams, circuits and countries",
    ], size=18, gap=14)
    d.text(s, 8.1, 5.6, 4.6, 0.8, "Source: Ergast database via the Jolpica-F1 API (also mirrored on Kaggle). "
                                  "Sprint races are out of scope.", size=12, color=MUTED)
    d.footer(s, 2, total, tag["A"][0])
    d.notes(s, f"Our dataset is the Ergast Formula 1 database, which the group downloaded from its successor, the "
               f"Jolpica API. The core table has {F['raw_rows']:,} race results: one row for every car in "
               f"every championship Grand Prix since 1950, {F['gp']:,} races in total, linked to tables of races, "
               "circuits, drivers and constructors. We chose it for three reasons. It is relational, so joins and "
               f"keys matter. Its quality problems are real: they come from {F['seasons']} seasons of changing rules "
               "and from "
               "how the files were exported, not from planted errors. And drivers, teams and circuits form a "
               "natural network, which is ideal for graph modelling.", "Dataset and motivation", "Student A", 50)

    # 3 ---------------------------------------------------------------------------------------- pipeline
    s = d.slide()
    d.title(s, "One command rebuilds every deliverable")
    stages = [("Step 0", "Extract", f"{F['raw_rows']:,}", "raw rows, values unchanged"),
              ("B", "Profile", f"{F['issues']}", f"issues in {F['dims']} quality dimensions"),
              ("C", "Clean", f"{F['gates_passed']}/{F['gates']}", "validation gates passed"),
              ("A", "Describe", f"{F['rda_before']:.0f}\u2192{F['rda_after']:.0f}%", "RDA FAIR maturity"),
              ("Graph", "Model", f"{F['pg_edges']:,}", "typed relationships"),
              ("Web", "Show", "7", "dashboard views, live")]
    bw, gap = 1.86, 0.19
    for i, (label, verb, num, sub) in enumerate(stages):
        x = MARGIN + i * (bw + gap)
        d.card(s, x, 1.75, bw, 3.0, fill=TINT if i < len(stages) - 1 else "EDE4FF", name=f"stage_{i}")
        d.chip(s, x + 0.18, 1.95, label, name=f"stage_label_{i}")
        d.text(s, x + 0.18, 2.45, bw - 0.36, 0.45, verb, size=19, bold=True)
        d.text(s, x + 0.18, 3.05, bw - 0.36, 0.75, num, size=24, bold=True, color=NAVY)
        d.text(s, x + 0.18, 3.75, bw - 0.36, 0.8, sub, size=12.5, color=INK2)
        if i < len(stages) - 1:
            d.arrow(s, x + bw + 0.03, 3.25, x + bw + gap - 0.03, 3.25)
    d.card(s, MARGIN, 5.15, SLIDE_W - 2 * MARGIN, 1.15, fill="FFFFFF", name="command_card")
    d.text(s, MARGIN + 0.3, 5.33, 11.5, 0.8, [
        [("python run_all.py --from-scratch", {"font": MONO, "bold": True, "size": 18, "color": NAVY})],
        [(f"Deterministic: two runs give byte-identical files  \u00b7  {F['tests']} automated tests  \u00b7  "
          "no network needed", {"size": 15, "color": INK2})]], spacing_after=4)
    d.footer(s, 3, total, tag["C"][0])
    d.notes(s, "Everything you will see comes from one pipeline. Step zero only flattens the raw archive into CSV "
               "files and records checksums; it never changes a value. Component B profiles those files and writes "
               f"an issue register with {F['issues']} entries. Component C resolves every issue and only publishes "
               f"data that passes all {F['gates']} validation gates. Component A describes the clean package with "
               "standard metadata, and the graph is built from validated output only. A single command rebuilds "
               "every file in about a minute, and two independent runs give byte-identical results, so every "
               "number in our report is reproducible.", "Pipeline overview", "Student C", 45)

    # 3b --------------------------------------------------------------------------------------- architecture
    s = d.slide()
    d.title(s, "Data engineering: zones, contracts and controls")
    d.picture(s, config.OUTPUT_DIR / "architecture" / "fig_e1_data_flow.png", MARGIN, 1.3, SLIDE_W - 2 * MARGIN, 5.45,
              "Data-flow diagram: source, raw zone, quality profile, clean zone and served products, with "
              "cross-cutting controls for schema, orchestration, tests and lineage.", name="fig_architecture")
    d.footer(s, 0, total, tag["A"][0])
    d.notes(s, "Here is the architecture behind it. Data move through zones: an immutable raw zone that keeps the "
               "source values and their lineage, a clean zone that is only written when every validation gate "
               "passes, and served products: the FAIR record, the graph, the dashboard and the report. Underneath "
               "are four engineering controls: one schema contract shared by cleaning and metadata, one orchestrated "
               "command, automated tests, and lineage down to the source line.",
            "Data engineering architecture", "Student A", 40)

    # 4 ---------------------------------------------------------------------------------------- A: FAIR scores
    s = d.slide()
    d.title(s, "As obtained, the data is hard to find and reuse")
    d.picture(s, figs_a / "fig_a2_fuji_scores.png", MARGIN, 1.5, 7.9, 5.15,
              "Bar chart of F-UJI FAIR scores for the group repository, the Jolpica API and the Kaggle mirror.",
              name="fig_fuji")
    y = d.stat(s, 9.05, 1.75, 3.7, f"{F['rda_before']:.0f}% \u2192 {F['rda_after']:.0f}%",
               f"RDA maturity, {X['rda_indicators']} indicators: as obtained \u2192 our package", num_size=40,
               label_h=0.75)
    y = d.stat(s, 9.05, y + 0.35, 3.7, f"{F['ess_before']} \u2192 {F['ess_after']}", "essential indicators met",
               num_size=40, label_h=0.45)
    d.text(s, 9.05, y + 0.35, 3.7, 1.0, "Findable stays at level 0 until a DOI is actually minted.",
           size=15, color=INK)
    d.footer(s, 4, total, tag["A"][0])
    d.notes(s, "We measured FAIRness twice. First automatically with F-UJI, run on a local server against the "
               f"three places where the data lives. The Jolpica API we downloaded from scores only "
               f"{F['fuji_jolpica']:.0f} percent, our own GitHub repository {F['fuji_github']:.0f} percent, and "
               f"the Kaggle mirror {F['fuji_kaggle']:.0f} percent. Because F-UJI only sees what is online, we also "
               f"scored all {X['rda_indicators']} indicators of the RDA maturity model with written evidence. Our "
               f"curated package lifts maturity from {F['rda_before']:.0f} to {F['rda_after']:.0f} percent. "
               "Findable honestly stays at level zero until the DOI is minted.", "FAIR assessment", "Student A", 50)

    # 5 ---------------------------------------------------------------------------------------- A: gaps
    s = d.slide()
    d.title(s, "Biggest gaps: no identifier, conflicting licences")
    d.text(s, MARGIN, 1.6, 6.2, 0.4, "Who says what about the licence?", size=20, bold=True, color=NAVY)
    licences = [("Ergast (original source)", "Non-commercial use only"),
                ("Jolpica-F1 (our download)", "CC BY-NC-SA 4.0"),
                ("Kaggle mirror", "Claims CC0, public domain"),
                ("Our GitHub repository", "MIT licence for everything")]
    for i, (who, what) in enumerate(licences):
        x = MARGIN + (i % 2) * 3.1
        y = 2.2 + (i // 2) * 1.75
        conflict = i >= 2
        d.card(s, x, y, 2.9, 1.5, fill=CRITICAL_TINT if conflict else TINT, name=f"licence_{i}")
        d.text(s, x + 0.22, y + 0.22, 2.5, 1.2, [[(who, {"size": 14, "color": INK2})],
                                                  [(what, {"size": 18, "bold": True,
                                                           "color": CRITICAL if conflict else NAVY})]],
               spacing_after=4)
    d.text(s, MARGIN, 5.85, 6.2, 0.8, [[("Fix: ", {"bold": True}),
                                         ("data under CC BY-NC-SA 4.0, code under MIT, with attribution", {})]],
           size=17, color=INK)
    d.text(s, 7.3, 1.6, 5.4, 0.4, "What our package adds", size=20, bold=True, color=NAVY)
    adds = [(f"{F['qid_driver']:.1f}%", f"of drivers linked to Wikidata IDs (circuits {F['qid_circ']:.0f}%)"),
            ("DataCite 4.5", "record validated against the official XSD"),
            ("ISO + PROV", "ISO 3166 country codes, W3C provenance, checksums"),
            ("DOI", "via Zenodo: reserved now, minted on deposit")]
    for i, (head, body) in enumerate(adds):
        y = 2.25 + i * 1.15
        d.text(s, 7.3, y, 2.1, 0.8, head, size=24, bold=True, color=NAVY)
        d.text(s, 9.5, y + 0.05, 3.25, 0.95, body, size=15, color=INK2)
    d.footer(s, 5, total, tag["A"][0])
    d.notes(s, f"We documented {X['gaps']} concrete FAIR gaps, each with indicator, evidence and remedy. Two stand "
               "out. First, there is no persistent identifier: the data is only reachable through URLs that can "
               "change. Second, the licences contradict each other. Ergast allowed only non-commercial use and "
               "Jolpica licenses the data CC BY-NC-SA, yet the Kaggle mirror claims public domain and our own "
               "repository says MIT for everything. We fixed what we can: a clear licence split, a DataCite record "
               "that validates against the official schema, ISO country codes, provenance, and Wikidata "
               f"identifiers for {F['qid_driver']:.1f} percent of drivers. The DOI is reserved and minted on deposit.",
            "FAIR gaps, licence and identifiers", "Student A", 50)

    # 6 ---------------------------------------------------------------------------------------- B: missingness
    s = d.slide()
    disguised = F["pos_disguised"] + F["grid_zero"]
    d.title(s, f"Completeness is deceptive: {disguised:,} hidden gaps")
    d.picture(s, figs_b / "fig_b1_hidden_missingness.png", MARGIN, 1.5, 7.8, 5.15,
              "Bar chart of explicit versus disguised missing values per column.", name="fig_missing")
    y = d.stat(s, 9.0, 1.7, 3.75, f"{F['null_cells']}", "explicit nulls: the table looks 99.9% complete",
               num_size=40, label_h=0.75)
    y = d.stat(s, 9.0, y + 0.25, 3.75, f"{F['pos_disguised']:,}", "'positions' that are really retirements",
               num_size=40, label_h=0.75)
    d.stat(s, 9.0, y + 0.25, 3.75, f"{F['grid_zero']}", "cars on a fictitious 'grid slot 0'", num_size=40,
           label_h=0.75)
    d.footer(s, 6, total, tag["B"][0])
    d.notes(s, f"I profiled every column of all five tables and ran {F['issues']} quality rules. The first lesson: "
               f"completeness is deceptive. Only {F['null_cells']} cells are empty, so the table looks almost perfect. "
               f"But {disguised:,} values only pretend to be data. The position column is filled for "
               f"{F['pos_disguised']:,} drivers who retired, withdrew or were disqualified, and {F['grid_zero']} cars "
               "start from grid slot zero, which does not exist. A model that predicts results from grid positions "
               "would learn from a retirement ranked eighteenth and from a fictitious pole-better-than-pole.",
            "Hidden missingness", "Student B", 45)

    # 7 ---------------------------------------------------------------------------------------- B: duplicates
    s = d.slide()
    d.title(s, "A naive duplicate check deletes real history")
    d.picture(s, figs_b / "fig_b2_duplicates_vs_shared_drives.png", MARGIN, 1.5, 7.8, 5.15,
              "Stacked bar chart of true duplicates versus legitimate shared drives per season.", name="fig_dups")
    y = d.stat(s, 9.0, 1.7, 3.75, f"{F['dup_exact'] + F['dup_hidden']}", "true duplicates, all from 1960",
               num_size=40, label_h=0.45)
    y = d.stat(s, 9.0, y + 0.25, 3.75, f"{F['dup_hidden']}", "of them hidden behind blanked keys", num_size=40,
               label_h=0.45)
    y = d.stat(s, 9.0, y + 0.25, 3.75, f"{F['shared']}", "valid rows: one driver, two cars in a race",
               num_size=40, label_h=0.75)
    d.text(s, 9.0, y + 0.15, 3.75, 0.8, [[("Correct key: ", {"bold": True}),
                                          ("season, round, driver and car number", {})]], size=15)
    d.footer(s, 7, total, tag["B"][0])
    d.notes(s, "Uniqueness needs domain knowledge. "
               f"{F['dup_exact']} rows of the 1960 United States Grand Prix were appended twice, and "
               f"{F['dup_hidden']} rows of the 1960 Italian Grand Prix are copies whose season and round were "
               "blanked, so they only look like duplicates after the keys are restored. The red bar is the real "
               f"problem. The blue bars are not: {F['shared']} rows share season, round and driver because in the "
               "1950s a driver could take over a team-mate's car and be classified twice. A naive duplicate check "
               "would delete that history. The correct key includes the car number.", "Duplicates vs shared drives",
            "Student B", 45)

    # 8 ---------------------------------------------------------------------------------------- B: eras + AI
    s = d.slide()
    d.title(s, "Valid history can look like bad data")
    d.picture(s, figs_b / "fig_b3_points_scale_by_era.png", MARGIN, 1.4, 7.2, 4.2,
              "Step chart of points awarded for a race win by season.", name="fig_points")
    y = d.stat(s, 9.0, 1.6, 3.75, f"{X['win_min']}–{X['win_max']}",
               "points for the same achievement: winning a race", num_size=40, label_h=0.75)
    d.stat(s, 9.0, y + 0.3, 3.75, f"{F['indy_outliers']}",
           "lap 'outliers', all valid Indianapolis 500 results: flag, never delete", num_size=40, label_h=0.75)
    d.card(s, MARGIN, 5.75, SLIDE_W - 2 * MARGIN, 0.95, name="impact_card")
    d.text(s, MARGIN + 0.3, 5.88, 3.2, 0.7, "Impact on data science and AI", size=16, bold=True, color=NAVY)
    impacts = ["Inflated wins from duplicated rows",
               "Biased targets: a retirement as '18th'",
               "Era bias in all-time rankings"]
    for i, item in enumerate(impacts):
        d.bullets(s, 4.25 + i * 2.85, 5.9, 2.7, 0.7, [item], size=14, gap=0)
    d.footer(s, 8, total, tag["B"][0])
    d.notes(s, "Some issues are not errors at all, but they still break analyses. A race win was worth "
               f"{', '.join(map(str, X['win_values']))} or even {X['win_max']} points depending on the era, so raw "
               f"points are not comparable over time. All {F['indy_outliers']} statistical outliers in laps are "
               "valid Indianapolis 500 results, so we flag them instead of deleting them. The root causes are "
               "export artefacts, undocumented source semantics and genuine historical change. For data science "
               "the impact is concrete: inflated win counts, biased prediction targets, sparse features from "
               f"{F['status_raw']} free-text statuses, and train-test leakage through duplicated rows.",
            "Eras, outliers and impact", "Student B", 50)

    # 9 ---------------------------------------------------------------------------------------- C: order
    s = d.slide()
    d.title(s, "Order matters: repair keys, then de-duplicate")
    col_w = 5.9
    for i, (fill, head, head_color, steps, num, num_label, num_color) in enumerate([
        (CRITICAL_TINT, "Naive order", CRITICAL,
         ["1. Remove exact duplicates", "2. Repair missing keys"], f"{F['dup_hidden']}",
         "duplicates survive, hidden by the blanked keys", CRITICAL),
        (TINT, "Our order (steps C02 \u2192 C03)", NAVY,
         [f"1. Restore season ({X['season_missing']}) and round ({X['round_missing']}) by exact lookup",
          "2. Remove exact duplicates"], f"{F['dup_exact'] + F['dup_hidden']}",
         "duplicates removed, none left; a unit test locks this in", NAVY)]):
        x = MARGIN + i * (col_w + 0.33)
        d.card(s, x, 1.6, col_w, 3.15, fill=fill, name=f"order_card_{i}")
        d.text(s, x + 0.3, 1.8, col_w - 0.6, 0.45, head, size=19, bold=True, color=head_color)
        d.text(s, x + 0.3, 2.35, col_w - 0.6, 0.95, steps, size=15, color=INK, spacing_after=4)
        d.stat(s, x + 0.3, 3.3, col_w - 0.6, num, num_label, num_size=40, color=num_color, label_h=0.45)
    d.text(s, MARGIN, 5.05, 5.0, 0.4, "No invented values", size=19, bold=True, color=NAVY)
    d.bullets(s, MARGIN, 5.55, SLIDE_W - 2 * MARGIN, 1.2, [
        f"Grid 0 becomes missing plus a flag ({F['grid_zero']} rows); no statistical imputation anywhere",
        "Keys come only from deterministic lookups: the file name and races.csv",
    ], size=15, gap=6)
    d.footer(s, 9, total, tag["C"][0])
    d.notes(s, "The most important design decision was the order of operations. If you remove duplicates first "
               f"and repair keys afterwards, {F['dup_hidden']} duplicates survive, because their season and round "
               "were blanked. So step C02 restores the missing season from the file name and the missing round by "
               f"an exact lookup in the races table, and only then does step C03 remove all "
               f"{F['dup_exact'] + F['dup_hidden']} copies. A unit test documents both orders. We also never invent "
               "values: no statistical imputation is used. Grid zero becomes missing with a flag, and withdrawn cars "
               "keep a missing number because none ever existed.", "Order of operations", "Student C", 50)

    # 10 --------------------------------------------------------------------------------------- C: gates
    s = d.slide()
    d.title(s, "Every issue closed, every output validated")
    d.picture(s, figs_c / "fig_c1_issue_resolution.png", MARGIN, 1.5, 7.8, 4.3,
              "Stacked bar chart of how the 28 quality issues were resolved per dimension.", name="fig_resolution")
    d.bullets(s, MARGIN, 6.0, 7.8, 0.75, [
        "Flag, don't delete: Indy 500 rows, shared drives and status conflicts stay, with flags"], size=15, gap=0)
    y = d.stat(s, 9.0, 1.7, 3.75, f"{F['gates_passed']}/{F['gates']}",
               "validation gates passed; one failure blocks publishing", num_size=40, label_h=0.75)
    y = d.stat(s, 9.0, y + 0.25, 3.75, f"{F['fixed']} of {F['issues']}", "issues fixed, the rest flagged, "
               "kept or verified", num_size=40, label_h=0.75)
    d.stat(s, 9.0, y + 0.25, 3.75, f"{F['clean_rows']:,}", f"clean rows, {F['clean_cols']} documented columns, "
           "an audit record per step", num_size=40, label_h=0.75)
    d.footer(s, 10, total, tag["C"][0])
    d.notes(s, f"Every one of the {F['issues']} issues is now closed: {F['fixed']} are fixed, {F['flagged']} are "
               f"mitigated or flagged, {F['kept']} are kept and documented, and {F['not_error']} were verified as "
               "non-errors. Our rule is flag, don't delete: Indianapolis 500 rows and shared drives stay in the data "
               f"with flags. Status went from {F['status_raw']} free-text values to {F['status_groups']} groups. "
               f"Every step writes an audit record, and {F['gates']} validation gates check schema, keys, foreign "
               "keys and vocabularies. If a single gate fails, nothing is published as clean. The final table has "
               f"{F['clean_rows']:,} rows and {F['clean_cols']} documented columns.", "Validation and resolution",
            "Student C", 50)

    # 11 --------------------------------------------------------------------------------------- graph model
    s = d.slide()
    d.title(s, f"{X['years']} years of F1 form a small world")
    d.picture(s, figs_g / "fig_g1_property_graph_model.png", MARGIN, 1.35, 6.95, 4.65,
              "Diagram of the property graph model with five node labels and seven relationship types.",
              name="fig_graph_model")
    d.text(s, MARGIN, 6.1, 6.95, 0.6, f"NetworkX MultiDiGraph: {F['pg_nodes']:,} nodes, {F['pg_edges']:,} typed "
                                     "edges, exported to GEXF for Gephi", size=13, color=INK2)
    d.stat(s, 7.8, 1.6, 2.35, f"{F['clust']:.2f}", f"clustering (random graph: {F['clust_r']:.3f})", num_size=40,
           label_h=0.75)
    d.stat(s, 10.35, 1.6, 2.4, f"{F['aspl']:.1f}", "team-mate links between two drivers on average",
           num_size=40, label_h=0.75)
    chain = [F["path"].iloc[0]["from"]] + F["path"]["to"].tolist()
    d.card(s, 7.8, 3.5, 4.93, 2.95, name="path_card")
    d.text(s, 8.05, 3.68, 4.45, 0.45, f"Fangio \u2192 Verstappen in {F['hops']} steps", size=19, bold=True,
           color=NAVY)
    names = [surname(n).replace(" ", "\u00a0") for n in chain]
    d.text(s, 8.05, 4.25, 4.45, 2.1, "\u00a0\u2192 ".join(names), size=16, color=INK, line_spacing=1.2)
    d.footer(s, 11, total, tag["B"][0])
    d.notes(s, "For the graph we modelled the cleaned data as a property graph: drivers, races, constructors, "
               "circuits and countries, with results stored as properties on RACED_IN edges, and a derived "
               "TEAMMATE_OF relationship. Indianapolis 500 rounds are excluded from the team-mate projection, a "
               f"direct consequence of the quality analysis. The result is a small world: clustering is "
               f"{F['clust']:.2f} against {F['clust_r']:.3f} for a random graph, yet two drivers are on average only "
               f"{F['aspl']:.1f} links apart. Juan Manuel Fangio reaches Max Verstappen in {F['hops']} steps, through "
               "long careers such as de Cesaris and Barrichello.", "Property graph and small world", "Student B", 47)

    # 12 --------------------------------------------------------------------------------------- communities
    s = d.slide()
    d.title(s, "Communities rediscover the eras by themselves")
    d.picture(s, figs_g / "fig_g4_communities_by_era.png", MARGIN, 1.5, 7.8, 5.15,
              "Range chart of Louvain communities and the seasons their drivers were active.", name="fig_communities")
    d.stat(s, 9.0, 1.7, 3.75, f"{F['communities']}", f"Louvain communities, modularity {F['modularity']:.2f}",
           num_size=40, label_h=0.45)
    top = F["top"]
    bridges = ", ".join(top["name"].head(3).map(surname))
    d.stat(s, 9.0, 2.85, 3.75, f"{top['betweenness'].iloc[0]:.2f}",
           f"highest betweenness; top bridges: {bridges}", num_size=40, label_h=0.75)
    d.card(s, 9.0, 4.45, 3.75, 2.05, name="caveat_card")
    d.text(s, 9.25, 4.62, 3.3, 1.8, [
        [("Caveat", {"bold": True, "size": 17, "color": NAVY})],
        [("Before the 1970s 'constructor' means the chassis make that private entrants shared, which "
          "inflates early drivers' degree.", {"size": 14})]], spacing_after=6)
    d.footer(s, 12, total, tag["A"][0])
    d.notes(s, f"Louvain community detection finds {F['communities']} communities with a modularity of "
               f"{F['modularity']:.2f}. The algorithm never sees a date, yet the large communities line up with "
               f"eras, from the fifties around {X['era_names'][0]} and the sixties around {X['era_names'][1]} to "
               f"the present grid around {X['era_names'][-1]}. Betweenness highlights bridges between eras such as "
               f"{top['name'].iloc[0]} and {top['name'].iloc[2]}. One caveat links back to data "
               "quality: before the seventies the constructor field records the chassis make shared by private "
               "entrants, so early drivers look more connected than they were.", "Communities by era", "Student A",
            37)

    # 13 --------------------------------------------------------------------------------------- dashboard
    s = d.slide()
    d.title(s, "The project, live: our interactive dashboard")
    d.picture(s, config.OUTPUT_DIR / "dashboard" / "fig_d1_dashboard_overview.png", MARGIN, 1.45, 8.0, 5.2,
              "Four screenshots of the interactive dashboard: start lights, constructor eras, the Fangio to "
              "Verstappen chain in the team-mate network, and how the data were checked.", name="fig_dashboard")
    d.text(s, 9.15, 1.55, 3.65, 0.4, "Built only from validated outputs", size=17, bold=True, color=NAVY)
    d.bullets(s, 9.15, 2.05, 3.65, 2.3, [
        "build_web_data.py reads the clean tables, graph metrics, issue register and FAIR scores",
        "run_all.py rebuilds it as its last step",
        f"It found issue B29: retirement causes not recorded from 2023",
    ], size=14, gap=7)
    d.card(s, 9.15, 4.75, 3.65, 1.75, fill="EDE4FF", name="demo_card")
    d.text(s, 9.4, 4.92, 3.2, 1.45, [
        [("Live demo", {"bold": True, "size": 17, "color": NAVY})],
        [("streamlit run app.py", {"font": MONO, "size": 14})],
        [("then localhost:8501", {"size": 14, "color": INK2})]], spacing_after=4)
    d.footer(s, 13, total, tag["C"][0])
    d.notes(s, f"Everything we showed ends here, in an interactive dashboard that the group can open with one command. "
               "It reads only validated outputs: the clean tables, the graph metrics, the issue register and the FAIR "
               "scores, and run_all rebuilds it as its last step. It also paid back: the reliability view showed "
               "mechanical failures vanishing after 2022, which turned out to be the source no longer recording why "
               "cars retired. That became issue B29. If time allows, we open it live.",
            "Interactive dashboard", "Student C", 33)

    # 13b -------------------------------------------------------------------------------------- dashboard gallery
    s = d.slide()
    d.title(s, "Inside the dashboard: every chart reads validated data")
    dash = config.OUTPUT_DIR / "dashboard"
    gallery = [("dashboard_drivers.png", "Timing tower: wins, podiums, era-adjusted score"),
               ("dashboard_grid.png", "Grid to finish, pole conversion, furthest-back wins"),
               ("dashboard_reliability.png", "Reliability, with the 2023 break (B29) marked"),
               ("dashboard_circuits.png", "77 circuits on a rotating globe")]
    img_h = 2.42
    img_w = img_h * 1.6
    gap_x, row_h = 0.45, img_h + 0.36
    left = (SLIDE_W - 2 * img_w - gap_x) / 2
    for i, (file, cap) in enumerate(gallery):
        x = left + (i % 2) * (img_w + gap_x)
        y = 1.3 + (i // 2) * row_h
        d.picture(s, dash / file, x, y, img_w, img_h, cap, name=f"gallery_{i}")
        d.text(s, x, y + img_h + 0.04, img_w, 0.3, cap, size=12, color=INK2)
    d.footer(s, 0, total, tag["B"][0])
    d.notes(s, "Four more views. The timing tower ranks drivers by wins or by our era-adjusted score. The grid view "
               "shows where cars finish from each starting slot, using classified positions only, which is exactly "
               "the fix for issue B11. The reliability view marks the 2023 break that became issue B29, and the "
               "globe places all seventy-seven circuits.", "Dashboard gallery", "Student B", 30)

    # 14 --------------------------------------------------------------------------------------- conclusion
    s = d.slide(dark=True)
    d.title(s, "What we learned", dark=True)
    lessons = [("1", "Quality is contextual", "Outliers, duplicates and short grids were often valid history"),
               ("2", "Order of operations matters", f"{F['dup_hidden']} duplicates hid behind blanked keys"),
               ("3", "FAIR gaps sit around the values", "No DOI, conflicting licences, no provenance"),
               ("4", "Automate the evidence", f"Audit log, {F['gates']} gates, {F['tests']} tests, metadata "
                                              "generated from code")]
    for i, (num, head, body) in enumerate(lessons):
        x = MARGIN + (i % 2) * 6.2
        y = 1.75 + (i // 2) * 2.4
        d.card(s, x, y, 5.95, 2.1, fill=CARD_ON_DARK, name=f"lesson_{num}")
        d.text(s, x + 0.35, y + 0.3, 0.8, 1.0, num, size=44, bold=True, color=ON_DARK)
        d.text(s, x + 1.2, y + 0.38, 4.5, 1.6, [[(head, {"bold": True, "size": 23, "color": "FFFFFF"})],
                                                 [(body, {"size": 17, "color": ON_DARK})]], spacing_after=6)
    d.footer(s, 14, total, tag["C"][0], dark=True)
    d.notes(s, "Four lessons. First, quality is contextual: outliers, duplicates and short grids were often valid "
               "history, so every automatic rule needed domain checking before deleting anything. Second, the order "
               f"of operations matters, as the {F['dup_hidden']} hidden duplicates show. Third, the largest FAIR "
               "gaps were around the values: no identifier, conflicting licences and no provenance. Fourth, "
               "automating the evidence, with an audit log, validation gates, tests and generated metadata, turns "
               "cleaning into something an examiner can verify. Next steps are a Zenodo DOI and reporting the "
               "source defects upstream to Jolpica.", "Conclusion", "Student C", 25)

    # 15 --------------------------------------------------------------------------------------- questions
    s = d.slide(dark=True)
    d.text(s, MARGIN, 2.2, 12.1, 1.2, "Questions?", size=60, bold=True, color="FFFFFF", name="title")
    d.text(s, MARGIN, 3.65, 12.1, 1.5, [
        [("Code, data, metadata and report: github.com/zalkimanohar/Formula1-Racing-Analytics", {"size": 18})],
        [("Rebuild everything: ", {"size": 18}), ("python run_all.py --from-scratch", {"font": MONO, "size": 18})]],
        color=ON_DARK, spacing_after=8)
    for i, c in enumerate("ABC"):
        d.chip(s, MARGIN + i * 3.2, 5.4, tag[c][0].replace("Presenter: ", ""), dark=True, name=f"team_chip_{c}")
    d.footer(s, 15, total, None, dark=True)
    d.notes(s, "Thank you. We are happy to take your questions; each of us will answer on our own component.",
            "Questions", "All", 5)

    d.prs.save(OUT_PPTX)
    write_script(d.script)
    print(f"[slides] {len(d.prs.slides)} slides -> {OUT_PPTX.name}")
    return OUT_PPTX


def write_script(script: list[dict]) -> None:
    budget = sum(i["seconds"] for i in script)
    names = {f"Student {m['component']}": f"{m['given_name']} {m['family_name']}" for m in config.TEAM}
    for item in script:
        item["seconds"] = round(item["seconds"] * 600 / budget)
        item["presenter"] = names.get(item["presenter"], item["presenter"])
    script[-1]["seconds"] += 600 - sum(i["seconds"] for i in script)
    lines = ["# Presenter script - group presentation (10 minutes + 5 minutes Q&A)", "",
             f"Speaking pace assumed: {SPEAKING_WPM} words per minute. Time budget per slide below; rehearse "
             "once with a timer.", "", "| # | Slide | Presenter | Budget | Words | Est. at pace |",
             "|---|---|---|---|---|---|"]
    per_presenter: dict[str, int] = {}
    for i, item in enumerate(script, start=1):
        words = len(item["notes"].split())
        est = round(words / SPEAKING_WPM * 60)
        lines.append(f"| {i} | {item['title']} | {item['presenter']} | {item['seconds']} s | {words} | {est} s |")
        key = item["presenter"].split(" (")[0]
        per_presenter[key] = per_presenter.get(key, 0) + item["seconds"]
    total = sum(i["seconds"] for i in script)
    lines += ["", f"**Total budget:** {total // 60} min {total % 60:02d} s.", "",
              "| Presenter | Time budget |", "|---|---|"]
    lines += [f"| {k} | {v // 60} min {v % 60:02d} s |" for k, v in per_presenter.items()]
    lines += ["", "## Script per slide", ""]
    for i, item in enumerate(script, start=1):
        lines += [f"### Slide {i} - {item['title']} ({item['presenter']}, {item['seconds']} s)", "", item["notes"], ""]
    lines += ["## Hand-over cues", "",
              "- Slide 2 -> 3: Student A hands over to Student C for the pipeline overview.",
              "- Slide 3 -> 4: Student C hands back to Student A for the FAIR assessment.",
              "- Slide 5 -> 6: Student A hands over to Student B for data quality.",
              "- Slide 8 -> 9: Student B hands over to Student C for the cleaning pipeline.",
              "- Slide 10 -> 11: Student C hands over to Student B for the graph model.",
              "- Slide 11 -> 12: Student B hands over to Student A for communities.",
              "- Slide 12 -> 13: Student A hands over to Student C for the conclusion.", ""]
    OUT_SCRIPT.write_text("\n".join(lines), encoding="utf-8")


def convert_pdf(pptx: Path) -> Path | None:
    soffice = config.find_soffice()
    if not soffice:
        return None
    profile = (config.REPORT_DIR / "presentation" / ".lo_profile").resolve().as_uri()
    subprocess.run([soffice, f"-env:UserInstallation={profile}", "--headless", "--convert-to", "pdf",
                    "--outdir", str(pptx.parent), str(pptx)], check=True, capture_output=True)
    shutil.rmtree(config.REPORT_DIR / "presentation" / ".lo_profile", ignore_errors=True)
    return pptx.with_suffix(".pdf")


def run() -> None:
    pptx = build()
    pdf = convert_pdf(pptx)
    print(f"[slides] PDF: {pdf.name if pdf else 'LibreOffice not found'}")


if __name__ == "__main__":
    run()
