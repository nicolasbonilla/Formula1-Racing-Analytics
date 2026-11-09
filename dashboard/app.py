"""Formula 1 in numbers - Streamlit entry point (`streamlit run app.py`).

The page itself is a self-contained web app in static/ (index.html, styles.css, app.js, data.js),
built from the cleaned dataset by build_web_data.py. Streamlit only serves it full screen; the
same index.html also opens directly in a browser.
"""
import re
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

STATIC = Path(__file__).resolve().parent / "static"

FULL_SCREEN = """
<style>
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"], [data-testid="stStatusWidget"], #MainMenu, footer { display: none !important; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background: #16181c !important; }
[data-testid="stMainBlockContainer"], .block-container { padding: 0 !important; max-width: 100% !important; }
iframe { position: fixed !important; inset: 0 !important; width: 100vw !important; height: 100vh !important;
         border: 0 !important; z-index: 999; }
</style>
"""


@st.cache_resource(show_spinner=False)
def bundled_page(version: float) -> str:
    """index.html with its stylesheet and scripts inlined, so it can run inside one frame."""
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    css = (STATIC / "styles.css").read_text(encoding="utf-8")
    html = html.replace('<link rel="stylesheet" href="styles.css">', f"<style>{css}</style>")
    return re.sub(r'<script src="([^"]+)"></script>',
                  lambda m: f"<script>{(STATIC / m.group(1)).read_text(encoding='utf-8')}</script>", html)


st.set_page_config(page_title="Formula 1 in Numbers, 1950-2025", page_icon=":material/sports_motorsports:",
                   layout="wide", initial_sidebar_state="collapsed")
st.markdown(FULL_SCREEN, unsafe_allow_html=True)
latest_change = max(p.stat().st_mtime for p in STATIC.rglob("*") if p.is_file())
components.html(bundled_page(latest_change), height=900, scrolling=True)
