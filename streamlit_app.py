import html

import streamlit as st

from apps import APPS

st.set_page_config(page_title="Sunique Warehouse Hub", page_icon="🏭", layout="wide")

GROUPS = [
    ("live", "可以使用 Live"),
    ("build", "开发中 Building"),
    ("plan", "规划中 Planned"),
]
LABEL = {"live": "可用", "build": "开发中", "plan": "规划中"}

st.markdown(
    """
<style>
.block-container {max-width: 1100px; padding-top: 2rem;}
.hub-card {
  border: 1px solid rgba(128,128,128,.25); border-left: 5px solid var(--stripe);
  border-radius: 10px; padding: 16px 18px; height: 100%;
  background: rgba(128,128,128,.04); display: flex; flex-direction: column; gap: 6px;
}
.hub-card.live {--stripe: #2e7d4f;} .hub-card.build {--stripe: #c27c0e;} .hub-card.plan {--stripe: #8a9299;}
.hub-head {display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;}
.hub-name {font-size: 1.1rem; font-weight: 600; line-height: 1.3;}
.hub-zh {font-size: .85rem; opacity: .7;}
.hub-icon {font-size: 1.6rem;}
.hub-desc {font-size: .92rem; opacity: .8; margin: 4px 0;}
.hub-tags span {font-size: .75rem; padding: 2px 8px; margin-right: 4px; border-radius: 4px;
  border: 1px solid rgba(128,128,128,.3); opacity: .8;}
.hub-foot {margin-top: auto; padding-top: 8px; display: flex; justify-content: space-between; align-items: center; font-size: .9rem;}
.hub-foot a {font-weight: 600; text-decoration: none;}
.pill {font-size: .75rem; font-weight: 600; padding: 2px 10px; border-radius: 999px;}
.pill.live {background: #e3f2e8; color: #2e7d4f;} .pill.build {background: #fbeed6; color: #9a5b00;} .pill.plan {background: #ebe9e5; color: #5f676d;}
.muted {opacity: .6;}
</style>
""",
    unsafe_allow_html=True,
)

st.title("🏭 Sunique Warehouse Hub")
st.caption("仓库工具中心 · 选择你要用的应用")

q = st.text_input("搜索应用 Search apps", placeholder="例如：运费、订单、排程", label_visibility="collapsed").strip().lower()


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
    st.subheader(title)
    for i in range(0, len(items), 3):
        cols = st.columns(3)
        for col, a in zip(cols, items[i : i + 3]):
            col.markdown(card(a), unsafe_allow_html=True)
    shown += len(items)

if shown == 0:
    st.info("没有匹配的应用。No apps match that search.")

st.divider()
st.caption("维护人 Kevin Li · 有问题或新需求请直接联系 Kevin。")
