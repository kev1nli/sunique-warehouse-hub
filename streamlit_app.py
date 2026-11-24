import base64
import html
from pathlib import Path

import streamlit as st

from apps import APPS

st.set_page_config(page_title="Sunique Warehouse Hub", page_icon="favicon.png", layout="wide")

BRAND = "#4E5B30"  # Sunique 主题绿
LOGO_B64 = base64.b64encode((Path(__file__).parent / "logo.png").read_bytes()).decode()

GROUPS = [
    ("live", "可以使用 Live"),
    ("build", "开发中 Building"),
    ("plan", "规划中 Planned"),
]
LABEL = {"live": "可用", "build": "开发中", "plan": "规划中"}

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
  <div class="sub">仓库工具中心 · 选择你要用的应用</div>
</div>""",
    unsafe_allow_html=True,
)

q = st.text_input("搜索应用 Search apps", placeholder="搜索应用，例如：运费、订单、排程", label_visibility="collapsed").strip().lower()


def matches(a):
    if not q:
        return True
    text = " ".join([a["name"], a["zh"], a["desc"], *a["tags"]]).lower()
    return q in text


def card(a):
    e = html.escape
    if a["url"]:
        foot = f'<a href="{e(a["url"])}" target="_blank">打开 Open ↗</a>'
    elif a["status"] == "live":
        foot = '<span class="muted">链接待添加</span>'
    elif a["status"] == "build":
        foot = '<span class="muted">正在开发，敬请期待</span>'
    else:
        foot = '<span class="muted">下一步计划</span>'
    tags = "".join(f"<span>{e(t)}</span>" for t in a["tags"])
    return f"""
<div class="hub-card {a['status']}">
  <div class="hub-head">
    <div><div class="hub-name">{e(a['name'])}</div><div class="hub-zh">{e(a['zh'])}</div></div>
    <div class="hub-icon">{a['icon']}</div>
  </div>
  <div class="hub-desc">{e(a['desc'])}</div>
  <div class="hub-tags">{tags}</div>
  <div class="hub-foot">{foot}<span class="pill {a['status']}">{LABEL[a['status']]}</span></div>
</div>"""


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
    st.info("没有匹配的应用。No apps match that search.")

st.markdown('<div class="foot-note">维护人 Kevin Li · 有问题或新需求请直接联系 Kevin</div>', unsafe_allow_html=True)
