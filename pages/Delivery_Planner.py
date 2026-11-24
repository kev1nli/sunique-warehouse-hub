import io
from datetime import date, datetime

import pandas as pd
import streamlit as st

import delivery_engine as eng
import delivery_geo as geo
import delivery_inflow as inflow

st.set_page_config(page_title="Delivery Planner · Sunique", page_icon="favicon.png", layout="wide")

BRAND = "#4E5B30"
st.markdown(
    f"""
<style>
.block-container {{max-width: 1100px; padding-top: 2rem;}}
.dp-head {{display: flex; align-items: baseline; justify-content: space-between; border-bottom: 3px solid {BRAND};
  padding-bottom: 8px; margin-bottom: 18px;}}
.dp-head h1 {{font-size: 1.6rem; margin: 0; color: {BRAND};}}
.dp-head a {{color: {BRAND}; font-weight: 600; text-decoration: none;}}
.dp-step {{font-size: .8rem; letter-spacing: .15em; text-transform: uppercase; color: {BRAND}; font-weight: 700; margin: 18px 0 6px;}}
.pick {{border: 2px solid {BRAND}; background: #f1f4ea; border-radius: 10px; padding: 16px 20px; margin: 8px 0 16px;}}
.pick b {{font-size: 1.2rem; color: {BRAND};}}
.chip {{display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: .78rem; font-weight: 600;}}
.stButton button[kind="primary"] {{background: {BRAND}; border-color: {BRAND};}}
</style>
<div class="dp-head"><h1>In-Town Delivery Planner</h1><a href="/" target="_self">← Warehouse Hub</a></div>
""",
    unsafe_allow_html=True,
)

# ---------- access ----------
try:
    password = st.secrets.get("APP_PASSWORD", "")
except Exception:
    password = ""
if not password:
    st.warning("This page is locked until a password is set. Kevin: add APP_PASSWORD in the app's Streamlit secrets.")
    st.stop()
if not st.session_state.get("dp_ok"):
    pw = st.text_input("Password", type="password")
    if pw and pw == password:
        st.session_state.dp_ok = True
        st.rerun()
    elif pw:
        st.error("Wrong password.")
    st.stop()

s = eng.Settings()
with st.expander("Rules"):
    c1, c2, c3 = st.columns(3)
    s.detour_limit_min = c1.number_input("Max extra driving to join a day (min)", 5, 120, 25, 5)
    s.horizon_days = c2.number_input("Business days offered", 3, 30, 10, 1)
    s.far_limit_min = c3.number_input("One-way drive above this goes to Kevin (min)", 30, 300, 120, 10)
    closed = st.text_input("Extra closed dates (MM/DD/YYYY, comma separated)", "")
    eng.EXTRA_CLOSED.clear()
    for part in closed.split(","):
        try:
            eng.EXTRA_CLOSED.add(datetime.strptime(part.strip(), "%m/%d/%Y").date())
        except ValueError:
            pass
    st.caption("Holidays already closed: New Year's Day, Memorial Day, July 4, Labor Day, Thanksgiving + the day after, Dec 24–25.")

# ---------- 1. current schedule ----------
st.markdown('<div class="dp-step">1 · Current schedule</div>', unsafe_allow_html=True)
up = st.file_uploader("Upload the latest Delivery Record Form (.xlsx)", type=["xlsx"])
if up is not None:
    st.session_state.dp_file = up.getvalue()
    st.session_state.dp_file_name = up.name

SLOT_BY_TEXT = {t.replace(" ", "").lower(): i for i, (t, *_rest) in enumerate(eng.SLOTS)}


def load_schedule(raw: bytes) -> pd.DataFrame:
    df = pd.read_excel(io.BytesIO(raw), sheet_name="In Town")
    df = df.iloc[:, :14]
    df.columns = ["cat", "so", "loc", "contact", "phone", "sales", "date", "time", "qty", "asm", "hand", "fee", "status", "notes"]
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["slot"] = df["time"].astype(str).str.replace(" ", "").str.lower().map(SLOT_BY_TEXT)
    df = df.dropna(subset=["date", "slot"])
    df["slot"] = df["slot"].astype(int)
    return df


today = date.today()
schedule = None
if "dp_file" in st.session_state:
    try:
        schedule = load_schedule(st.session_state.dp_file)
        upcoming = schedule[schedule["date"] > today]
        st.caption(f"Using {st.session_state.dp_file_name}: {len(upcoming)} upcoming bookings after {today:%m/%d}.")
    except Exception as e:
        st.error(f"Could not read the 'In Town' sheet: {e}")
else:
    st.info("Upload the schedule first so the planner knows which slots are taken.")

# ---------- 2. order ----------
st.markdown('<div class="dp-step">2 · Order</div>', unsafe_allow_html=True)
c1, c2 = st.columns([2, 1])
so = c1.text_input("Sales order #", placeholder="SO-018966").strip().upper()
lookup = c2.button("Look up in inFlow", use_container_width=True, disabled=not so)
if lookup:
    st.session_state.dp_order = inflow.get_order(so)
order = st.session_state.get("dp_order") or {}
if order.get("error"):
    st.warning(order["error"] + " You can still fill in the details below.")
    order = {}
elif order:
    st.caption(
        f"inFlow: {order['order_number']} · ordered {order['order_date']:%m/%d/%Y} · contact {order['contact']} "
        f"{order['phone']} · sales {order['sales_rep']} · "
        + (f"ASSEMBLED ({order['assembly_qty']:g} cabinets)" if order["assembled"] else "flat pack")
    )

c1, c2, c3 = st.columns(3)
category = c1.selectbox("Product category", ["Cabinet", "Flooring", "Others"])
handling = c2.selectbox("Needs handling?", ["Yes", "No"]) == "Yes"
order_date = c3.date_input("Order date", value=order.get("order_date") or today)
address = st.text_input("Delivery address", value=order.get("address") or "",
                        placeholder="1008 W Hall St, McKinney, TX 75069")
c1, c2 = st.columns(2)
assembled = c1.checkbox("Assembled order (has Z_ASSEMBLY FEE)", value=bool(order.get("assembled")))
assembly_done = c2.date_input("Assembly finish date", value=None, disabled=not assembled) if assembled else None

go = st.button("Find delivery dates", type="primary", disabled=not (address and schedule is not None))

# ---------- 3. options ----------
if go:
    st.markdown('<div class="dp-step">3 · Available dates</div>', unsafe_allow_html=True)
    depot_addr, depot_pt = eng.DEPOTS["Flooring" if category == "Flooring" else "Cabinet"]
    with st.spinner("Locating the address…"):
        g = geo.geocode(address)
    if not g:
        st.error("Could not find that address. Check the street, city and ZIP.")
        st.stop()
    point = (g[0], g[1])
    if g[2] == "city":
        st.warning("Exact address not found; using the city center. Results are approximate.")

    days = eng.business_days(eng.next_business_day(today), int(s.horizon_days))
    plans = {d: eng.DayPlan(d) for d in days}
    rows = schedule[schedule["date"].isin(days)]
    with st.spinner("Checking booked stops…"):
        for _, r in rows.iterrows():
            loc = "" if pd.isna(r["loc"]) else str(r["loc"])
            gp = geo.geocode(loc) if loc.strip() else None
            plans[r["date"]].bookings.append(eng.Booking(
                slot=int(r["slot"]), label=str(r["so"]), address=loc,
                point=(gp[0], gp[1]) if gp else None, reserved=not loc.strip(),
                handling=str(r["hand"]).strip().lower() != "no"))
        pts = [depot_pt, point] + [b.point for p in plans.values() for b in p.bookings if b.point]
        dur, src = geo.make_dur(pts)

    earliest = eng.earliest_date(today, order_date, assembled, assembly_done)
    opts = eng.plan_options(plans, days, earliest, address, point, handling, depot_pt, dur, s)

    one_way = dur(depot_pt, point)
    st.caption(f"From {depot_addr}: about {one_way:.0f} min one way"
               + ("" if src == "osrm" else " (estimated; routing service unavailable)") + ".")
    if assembled and assembly_done is None:
        st.warning("Enter the assembly finish date to see dates for an assembled order.")

    rec = next((o for o in opts if o.status == "Recommended"), None)
    if rec:
        label = eng.SLOTS[rec.slot][0]
        st.markdown(
            f'<div class="pick">Recommended: <b>{rec.day:%a %m/%d} · {eng.SLOTS[rec.slot][1]}</b><br>'
            f'{rec.note}' + (f" · adds {rec.extra_min:.0f} min of driving" if rec.extra_min is not None else "")
            + "</div>", unsafe_allow_html=True)
        st.text_area("Confirmation text to send to sales",
                     f"Delivery is scheduled for {rec.day:%m/%d} {label.replace(' AM', '').replace(' PM', '').replace(' - ', '-')}.",
                     height=70)
    elif opts and opts[0].status == "Too far":
        st.error("This address is beyond the in-town drive limit. Kevin schedules it by hand.")
    else:
        st.error(f"No open date in the next {int(s.horizon_days)} business days. Kevin schedules it by hand.")

    colors = {"Recommended": ("#e6ebd9", BRAND), "Open": ("#eef4ff", "#1f5fae"), "Full": ("#f1f1ef", "#6b7064"),
              "Different direction": ("#fbeed6", "#8a5a00"), "Not ready": ("#f1f1ef", "#6b7064"),
              "Too far": ("#fde7e7", "#a12b2b")}
    table = pd.DataFrame([{
        "Date": f"{o.day:%a %m/%d}",
        "Status": o.status,
        "Slot": eng.SLOTS[o.slot][1] if o.slot is not None and o.status in ("Recommended", "Open") else "",
        "Extra driving (min)": str(round(o.extra_min)) if o.extra_min is not None and o.status != "Full" else "",
        "Booked that day": ", ".join(f"{eng.SLOTS[b.slot][1]} {b.label}" for b in sorted(plans[o.day].bookings, key=lambda b: b.slot)) if o.day in plans else "",
        "Why": o.note,
    } for o in opts])

    def paint(v):
        bg, fg = colors.get(v, ("", ""))
        return f"background-color: {bg}; color: {fg}; font-weight: 600" if bg else ""

    st.dataframe(table.style.map(paint, subset=["Status"]), hide_index=True, use_container_width=True,
                 column_config={"Status": st.column_config.TextColumn(width="medium"),
                                "Booked that day": st.column_config.TextColumn(width="large")})
    st.caption("Only Recommended and Open dates should be offered to the customer. "
               "For any other date, ask Kevin.")
