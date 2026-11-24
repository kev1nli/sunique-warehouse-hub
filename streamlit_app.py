import base64
import html
from pathlib import Path

import streamlit as st

from apps import APPS
from sops import SOPS

st.set_page_config(page_title="Sunique Warehouse Hub", page_icon="favicon.png", layout="wide")

BRAND = "#4E5B30"  # Sunique brand green
SOP_DIR = Path(__file__).parent / "sops"
LOGO_B64 = base64.b64encode((Path(__file__).parent / "logo.png").read_bytes()).decode()

GROUPS = [
    ("live", "Available now"),
    ("build", "In development"),
    ("plan", "Planned"),
]
LABEL = {"live": "Live", "build": "Building", "plan": "Planned"}

st.markdown(
    f"""
<style>
.stApp {{background: {BRAND};}}
header[data-testid="stHeader"] {{background: transparent;}}
.block-container {{max-width: 1100px; padding-top: 2.5rem;}}
.stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label, .stApp [data-testid="stCaptionContainer"] {{color: #ffffff;}}
.brand {{display: flex; flex-direction: column; align-items: center; gap: 14px; margin-bottom: 28px; text-align: center;}}
.brand img {{width: 260px; max-width: 70vw;}}
.brand .rule {{width: 56px; height: 1px; background: rgba(255,255,255,.55);}}
.brand .title {{color: #fff; font-size: 1.05rem; letter-spacing: .32em; text-transform: uppercase; font-weight: 500;}}
.brand .sub {{color: rgba(255,255,255,.75); font-size: .9rem;}}
.stTextInput input {{background: #ffffff; color: #1d2226; border: none;}}
.section {{color: #fff; font-size: .95rem; letter-spacing: .2em; text-transform: uppercase; font-weight: 600;
  border-bottom: 1px solid rgba(255,255,255,.3); padding-bottom: 6px; margin: 28px 0 14px;}}
.hub-card {{
  background: #ffffff; color: #1d2226; border-radius: 10px; padding: 18px 20px; height: 100%;
  border-top: 4px solid var(--stripe); display: flex; flex-direction: column; gap: 6px;
  box-shadow: 0 4px 14px rgba(0,0,0,.15);
}}
.hub-card.live {{--stripe: {BRAND};}} .hub-card.build {{--stripe: #c9a227;}} .hub-card.plan {{--stripe: #b5b9ad;}}
.hub-card.plan, .hub-card.build {{background: #f4f5f0;}}
.hub-head {{display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;}}
.hub-name {{font-size: 1.1rem; font-weight: 700; line-height: 1.3; color: #1d2226;}}
.hub-zh {{font-size: .85rem; color: #6b7064;}}
.hub-icon {{font-size: 1.6rem;}}
.hub-desc {{font-size: .92rem; color: #4a4f45; margin: 4px 0;}}
.hub-tags span {{font-size: .75rem; padding: 2px 8px; margin-right: 4px; border-radius: 4px;
  background: #eef0e8; color: {BRAND};}}
.hub-foot {{margin-top: auto; padding-top: 10px; display: flex; justify-content: space-between; align-items: center; font-size: .9rem;}}
.hub-foot a {{font-weight: 700; text-decoration: none; color: #fff !important; background: {BRAND};
  padding: 5px 14px; border-radius: 6px;}}
.hub-foot a:hover {{background: #3d4826;}}
.pill {{font-size: .75rem; font-weight: 600; padding: 2px 10px; border-radius: 999px;}}
.pill.live {{background: #e6ebd9; color: {BRAND};}} .pill.build {{background: #f6edcc; color: #8a6d0b;}} .pill.plan {{background: #e7e8e3; color: #6b7064;}}
.muted {{color: #8a8f82;}}
.foot-note {{color: rgba(255,255,255,.7); font-size: .85rem; text-align: center; margin-top: 40px;
  border-top: 1px solid rgba(255,255,255,.25); padding-top: 14px;}}
[data-testid="stTab"] {{color: rgba(255,255,255,.7); padding: 6px 4px;}}
[data-testid="stTab"] p {{color: inherit !important; font-size: 1.1rem; font-weight: 700; letter-spacing: .04em;}}
[data-testid="stTab"][aria-selected="true"] {{color: #ffffff;}}
[role="tablist"] {{gap: 18px; border-bottom: 1px solid rgba(255,255,255,.3);}}
.react-aria-SelectionIndicator {{background-color: #ffffff !important; height: 3px !important;}}
.sop-card {{background: #ffffff; border-radius: 10px; padding: 16px 20px; box-shadow: 0 4px 14px rgba(0,0,0,.15);
  display: flex; flex-direction: column; gap: 4px; color: #1d2226;}}
.sop-title {{font-weight: 700; font-size: 1.05rem;}}
.sop-meta {{font-size: .8rem; color: #6b7064;}}
.sop-desc {{font-size: .92rem; color: #4a4f45;}}
.empty-box {{background: rgba(255,255,255,.08); border: 1px dashed rgba(255,255,255,.45); border-radius: 10px;
  padding: 36px 20px; text-align: center; color: #fff;}}
.empty-box b {{display: block; font-size: 1.1rem; margin-bottom: 6px;}}
.empty-box span {{color: rgba(255,255,255,.75); font-size: .92rem;}}
.stDownloadButton button {{background: {BRAND}; color: #fff; border: none; font-weight: 600;}}
.stDownloadButton button:hover {{background: #3d4826; color: #fff;}}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="brand">
  <img src="data:image/png;base64,{LOGO_B64}" alt="Sunique International">
  <div class="rule"></div>
  <div class="title">Warehouse Hub</div>
  <div class="sub">Sunique warehouse tools and SOPs in one place</div>
</div>""",
    unsafe_allow_html=True,
)

q = st.text_input("Search", placeholder="Search apps and SOPs, e.g. freight, orders, pickup", label_visibility="collapsed").strip().lower()


def matches(a):
    if not q:
        return True
    text = " ".join([a["name"], a["desc"], *a["tags"]]).lower()
    return q in text


def card(a):
    e = html.escape
    if a["url"]:
        foot = f'<a href="{e(a["url"])}" target="_blank">Open ↗</a>'
    elif a["status"] == "live":
        foot = '<span class="muted">Link coming soon</span>'
    elif a["status"] == "build":
        foot = '<span class="muted">Coming soon</span>'
    else:
        foot = '<span class="muted">Next up</span>'
    tags = "".join(f"<span>{e(t)}</span>" for t in a["tags"])
    return f"""
<div class="hub-card {a['status']}">
  <div class="hub-head">
    <div class="hub-name">{e(a['name'])}</div>
    <div class="hub-icon">{a['icon']}</div>
  </div>
  <div class="hub-desc">{e(a['desc'])}</div>
  <div class="hub-tags">{tags}</div>
  <div class="hub-foot">{foot}<span class="pill {a['status']}">{LABEL[a['status']]}</span></div>
</div>"""


tab_apps, tab_sops = st.tabs(["Apps", "SOPs"])

with tab_apps:
    shown = 0
    for key, title in GROUPS:
        items = [a for a in APPS if a["status"] == key and matches(a)]
        if not items:
            continue
        st.markdown(f'<div class="section">{title}</div>', unsafe_allow_html=True)
        for i in range(0, len(items), 3):
            cols = st.columns(3)
            for col, a in zip(cols, items[i : i + 3]):
                col.markdown(card(a), unsafe_allow_html=True)
        shown += len(items)
    if shown == 0:
        st.markdown('<div class="empty-box"><b>No apps match your search</b><span>Try a different word.</span></div>', unsafe_allow_html=True)


def sop_matches(s):
    if not q:
        return True
    return q in " ".join([s.get("title", ""), s.get("desc", ""), s.get("category", "")]).lower()


with tab_sops:
    st.markdown('<div class="section">Standard operating procedures</div>', unsafe_allow_html=True)
    if not SOPS:
        st.markdown(
            '<div class="empty-box"><b>SOPs coming soon</b>'
            "<span>Warehouse and sales procedures will be posted here as PDFs.</span></div>",
            unsafe_allow_html=True,
        )
    else:
        items = [s for s in SOPS if sop_matches(s)]
        if not items:
            st.markdown('<div class="empty-box"><b>No SOPs match your search</b><span>Try a different word.</span></div>', unsafe_allow_html=True)
        for i in range(0, len(items), 2):
            cols = st.columns(2)
            for col, s in zip(cols, items[i : i + 2]):
                e = html.escape
                meta = " · ".join(x for x in [s.get("category", ""), f"Updated {s['updated']}" if s.get("updated") else ""] if x)
                col.markdown(
                    f'<div class="sop-card"><div class="sop-title">📄 {e(s["title"])}</div>'
                    f'<div class="sop-meta">{e(meta)}</div><div class="sop-desc">{e(s.get("desc", ""))}</div></div>',
                    unsafe_allow_html=True,
                )
                path = SOP_DIR / s["file"]
                if path.exists():
                    col.download_button("Download PDF", path.read_bytes(), file_name=s["file"], mime="application/pdf", key=f"sop-{s['file']}")
                else:
                    col.caption(f"File not found: sops/{s['file']}")

st.markdown('<div class="foot-note">Maintained by Kevin Li · Questions or requests? Contact Kevin.</div>', unsafe_allow_html=True)
