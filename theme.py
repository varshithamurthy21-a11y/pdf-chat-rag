"""
theme.py - colourful themes for the whole app.

How it works:
  * .streamlit/config.toml sets the base look (light main area, dark sidebar,
    rounded corners). Streamlit handles text colours from there.
  * This file adds a theme picker in the sidebar and injects CSS for the
    chosen theme: gradient sidebar, soft gradient background, gradient
    buttons, chat bubbles, upload box and a "hero" banner at the top.

Every theme follows the same rule: deep, rich colours in the sidebar (white
text) and a light pastel main area (dark text), so text is always readable.

To add your own theme, copy one entry in THEMES and change the colours.
"""

import html

import streamlit as st

THEMES = {
    "🌌 Aurora": {
        "accent": "#7c3aed", "accent2": "#db2777",
        "side1": "#2e1065", "side2": "#701a75",
        "bg1": "#f7f3ff", "bg2": "#fdf2f8", "tint": "#ede9fe",
    },
    "🌊 Ocean": {
        "accent": "#0369a1", "accent2": "#0d9488",
        "side1": "#0c1e3e", "side2": "#134e4a",
        "bg1": "#eff8ff", "bg2": "#ecfdf5", "tint": "#e0f2fe",
    },
    "🌅 Sunset": {
        "accent": "#ea580c", "accent2": "#db2777",
        "side1": "#7c2d12", "side2": "#831843",
        "bg1": "#fff7ed", "bg2": "#fdf2f8", "tint": "#ffedd5",
    },
    "🌿 Forest": {
        "accent": "#047857", "accent2": "#65a30d",
        "side1": "#052e16", "side2": "#14532d",
        "bg1": "#f0fdf4", "bg2": "#f7fee7", "tint": "#dcfce7",
    },
    "🍬 Candy": {
        "accent": "#c026d3", "accent2": "#2563eb",
        "side1": "#4a044e", "side2": "#1e3a8a",
        "bg1": "#fdf4ff", "bg2": "#eff6ff", "tint": "#fae8ff",
    },
    "🌙 Midnight Gold": {
        "accent": "#b45309", "accent2": "#d97706",
        "side1": "#0f172a", "side2": "#1e293b",
        "bg1": "#f8fafc", "bg2": "#fefce8", "tint": "#fef3c7",
    },
}
DEFAULT_THEME = "🌌 Aurora"

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
  --accent: %(accent)s; --accent2: %(accent2)s;
  --side1: %(side1)s; --side2: %(side2)s;
  --bg1: %(bg1)s; --bg2: %(bg2)s; --tint: %(tint)s;
  --grad: linear-gradient(135deg, %(accent)s 0%%, %(accent2)s 100%%);
}

/* ---------- font ---------- */
html, body, .stApp, .stApp p, .stApp label, .stApp li, .stApp input,
.stApp textarea, .stApp button, .stApp h1, .stApp h2, .stApp h3 {
  font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
}
.stApp h1, .stApp h2, .stApp h3 { letter-spacing: -0.02em; }

/* ---------- main background ---------- */
.stApp {
  background:
    radial-gradient(circle at 0%% 0%%, var(--bg1) 0%%, transparent 55%%),
    radial-gradient(circle at 100%% 100%%, var(--bg2) 0%%, transparent 55%%),
    #ffffff;
  background-attachment: fixed;
}
[data-testid="stHeader"], [data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] > div { background: transparent !important; }
.block-container { padding-top: 2.2rem; }

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] {
  background: linear-gradient(170deg, var(--side1) 0%%, var(--side2) 100%%);
  border-right: none;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"],
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="input"],
[data-testid="stSidebar"] [data-baseweb="base-input"],
[data-testid="stSidebar"] [data-testid="stExpander"] details {
  background: rgba(255,255,255,0.10) !important;
  border-color: rgba(255,255,255,0.25) !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
  border: 1.5px dashed rgba(255,255,255,0.45) !important;
}
[data-testid="stSidebar"] [data-testid="stAlert"] {
  background: rgba(255,255,255,0.12) !important;
  border: 1px solid rgba(255,255,255,0.18);
}
[data-testid="stSidebar"] [data-testid="stAlert"] * { color: #ffffff !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.18); }

/* page links in the sidebar */
[data-testid="stSidebarNavLink"] { border-radius: 12px; margin: 2px 0; }
[data-testid="stSidebarNavLink"]:hover { background: rgba(255,255,255,0.10); }
[data-testid="stSidebarNavLink"][aria-current="page"] {
  background: rgba(255,255,255,0.18);
  box-shadow: inset 3px 0 0 var(--accent2);
}

/* ---------- buttons ---------- */
.stButton > button, .stDownloadButton > button,
[data-testid="stFormSubmitButton"] > button {
  border-radius: 12px; font-weight: 600;
  transition: transform .15s ease, box-shadow .15s ease, filter .15s ease;
}
.stButton > button[kind="primary"], .stDownloadButton > button,
[data-testid="stFormSubmitButton"] > button,
[data-testid="stBaseButton-primary"] {
  background: var(--grad) !important; color: #ffffff !important;
  border: none !important;
  box-shadow: 0 6px 18px -6px var(--accent);
}
.stButton > button:hover, .stDownloadButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
  transform: translateY(-1px); filter: brightness(1.05);
}
.stButton > button[kind="secondary"] {
  border: 1.5px solid var(--accent); color: var(--accent); background: #ffffffcc;
}
[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
  background: rgba(255,255,255,0.12); color: #ffffff;
  border: 1px solid rgba(255,255,255,0.35);
}

/* ---------- chat ---------- */
[data-testid="stChatMessage"] {
  background: #ffffffd9; border: 1px solid rgba(0,0,0,0.05);
  border-radius: 18px; padding: 14px 18px;
  box-shadow: 0 8px 24px -16px rgba(30, 20, 60, 0.35);
  backdrop-filter: blur(6px);
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  background: var(--tint);
}
[data-testid="stChatMessageAvatarAssistant"] { background: var(--grad); }
[data-testid="stChatInput"] {
  border-radius: 16px; background: #ffffff;
  border: 1.5px solid var(--accent) !important;
  box-shadow: 0 10px 30px -18px var(--accent);
}
[data-testid="stChatInput"] button { background: var(--grad) !important; color: #fff !important; }

/* ---------- main-area widgets ---------- */
.main [data-testid="stFileUploaderDropzone"], section.main [data-testid="stFileUploaderDropzone"],
[data-testid="stMain"] [data-testid="stFileUploaderDropzone"] {
  background: #ffffffcc; border: 2px dashed var(--accent); border-radius: 16px;
}
[data-testid="stMain"] [data-testid="stExpander"] details {
  background: #ffffffcc; border-radius: 14px;
}
[data-testid="stMain"] [data-testid="stImage"] img {
  border-radius: 12px; box-shadow: 0 8px 20px -12px rgba(0,0,0,.35);
}
[data-baseweb="slider"] [role="slider"] { background: var(--accent) !important; }
[data-testid="stProgress"] > div > div > div > div { background: var(--grad) !important; }
[data-testid="stMain"] [data-testid="stAlert"] { border-radius: 14px; }

/* ---------- custom blocks (hero, cards, badges) ---------- */
.ui-hero {
  background: var(--grad); color: #fff; border-radius: 24px;
  padding: 26px 30px; margin-bottom: 18px; position: relative; overflow: hidden;
  box-shadow: 0 18px 40px -22px var(--accent);
}
.ui-hero::after {
  content: ""; position: absolute; right: -60px; top: -60px; width: 220px; height: 220px;
  border-radius: 50%%; background: rgba(255,255,255,0.14);
}
.ui-hero h1 { color: #fff !important; font-size: 2rem; font-weight: 800; margin: 0; padding: 0; }
.ui-hero p { color: rgba(255,255,255,0.92) !important; margin: 6px 0 0; font-size: 1.02rem; }
.ui-hero .ui-icon { font-size: 2.2rem; margin-right: 10px; vertical-align: -4px; }

.ui-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 14px; margin: 8px 0 18px; }
.ui-card {
  background: #ffffffd9; border-radius: 18px; padding: 18px;
  border: 1px solid rgba(0,0,0,0.05); box-shadow: 0 10px 26px -18px rgba(30,20,60,.4);
}
.ui-card .ui-card-icon {
  width: 42px; height: 42px; border-radius: 12px; background: var(--grad);
  display: flex; align-items: center; justify-content: center; font-size: 1.3rem; margin-bottom: 10px;
}
.ui-card b { display: block; font-size: 1rem; margin-bottom: 4px; color: #1f1d2e; }
.ui-card span { color: #555366; font-size: .9rem; }

.ui-badge {
  display: inline-block; padding: 3px 12px; border-radius: 999px; font-size: .78rem;
  font-weight: 700; background: var(--tint); color: var(--accent); margin-bottom: 6px;
}
</style>
"""


def _remember_theme():
    st.session_state.ui_theme_choice = st.session_state._ui_theme_widget


def apply_theme(show_picker: bool = True) -> dict:
    """Inject the chosen theme's CSS. Call once near the top of every page."""
    if "ui_theme_choice" not in st.session_state:
        st.session_state.ui_theme_choice = DEFAULT_THEME
    names = list(THEMES)

    if show_picker:
        st.sidebar.selectbox(
            "🎨 Theme", names,
            index=names.index(st.session_state.ui_theme_choice),
            key="_ui_theme_widget", on_change=_remember_theme,
        )

    colors = THEMES[st.session_state.ui_theme_choice]
    st.markdown(_CSS % colors, unsafe_allow_html=True)
    return colors


def hero(title: str, subtitle: str = "", icon: str = ""):
    """Big gradient banner at the top of a page."""
    icon_html = f'<span class="ui-icon">{icon}</span>' if icon else ""
    st.markdown(
        f'<div class="ui-hero"><h1>{icon_html}{html.escape(title)}</h1>'
        f'<p>{html.escape(subtitle)}</p></div>',
        unsafe_allow_html=True,
    )


def feature_cards(cards: list[tuple[str, str, str]]):
    """Row of small cards: [(icon, title, text), ...]"""
    items = "".join(
        f'<div class="ui-card"><div class="ui-card-icon">{icon}</div>'
        f"<b>{html.escape(title)}</b><span>{html.escape(text)}</span></div>"
        for icon, title, text in cards
    )
    st.markdown(f'<div class="ui-cards">{items}</div>', unsafe_allow_html=True)


def badge(text: str):
    st.markdown(f'<span class="ui-badge">{html.escape(text)}</span>', unsafe_allow_html=True)
