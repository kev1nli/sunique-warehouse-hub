"""Read a sales order from inFlow (cabinet account). Key comes from Streamlit secrets."""
from __future__ import annotations

from datetime import datetime

import requests
import streamlit as st

VERSION = "2024-03-12"
LOCATIONS = {
    "03ad0558-c1dc-483d-81a5-38b818444984": "2045 Westgate",
    "b12dae7a-ea38-46f1-ab41-e4e9ea6df45c": "739 Parkway",
}


def _key() -> str:
    try:
        return str(st.secrets.get("INFLOW_KEY", "")).strip()
    except Exception:
        return ""


def configured() -> bool:
    try:
        return bool(st.secrets.get("INFLOW_KEY")) and bool(st.secrets.get("INFLOW_COMPANY"))
    except Exception:
        return False


def get_order(order_number: str):
    """Return a dict with the fields the planner needs, or {'error': ...}."""
    if not configured():
        return {"error": "inFlow is not connected (missing secrets)."}
    url = f"https://cloudapi.inflowinventory.com/{st.secrets['INFLOW_COMPANY']}/sales-orders"
    try:
        r = requests.get(url, params={"filter[orderNumber]": order_number.strip().upper(), "include": "lines.product"},
                         headers={"Authorization": f"Bearer {_key()}",
                                  "Accept": f"application/json;version={VERSION}"}, timeout=20)
        if r.status_code == 401:
            k = _key()
            return {"error": "inFlow rejected the API key (401). The saved INFLOW_KEY is "
                             f"{len(k)} characters long and ends with '{k[-2:]}'. A full inFlow key is "
                             "about 66 characters and ends with '-1'. Fix it in the app's Secrets."}
        r.raise_for_status()
        rows = r.json()
    except Exception as e:
        return {"error": f"inFlow lookup failed: {e}"}
    if not rows:
        return {"error": f"{order_number} was not found in inFlow."}
    o = rows[0]
    assembly_qty = 0.0
    boxes = 0.0
    for line in o.get("lines") or []:
        name = ((line.get("product") or {}).get("name") or "").upper()
        qty = float((line.get("quantity") or {}).get("standardQuantity") or 0)
        if name == "Z_ASSEMBLY FEE":
            assembly_qty += qty
        elif (line.get("product") or {}).get("itemType") == "stockedProduct":
            boxes += qty
    ship = o.get("shippingAddress") or {}
    address = ", ".join(x for x in [ship.get("address1"), ship.get("city"),
                                     " ".join(y for y in [ship.get("state"), ship.get("postalCode")] if y)] if x)
    order_date = None
    if o.get("orderDate"):
        order_date = datetime.fromisoformat(o["orderDate"][:19]).date()
    return {
        "order_number": o.get("orderNumber"),
        "order_date": order_date,
        "contact": o.get("contactName") or "",
        "phone": o.get("phone") or "",
        "sales_rep": (o.get("customFields") or {}).get("custom1") or "",
        "address": address,
        "po": o.get("poNumber") or "",
        "assembled": assembly_qty > 0,
        "assembly_qty": assembly_qty,
        "boxes": boxes,
        "location": LOCATIONS.get(o.get("locationId"), ""),
        "status": o.get("inventoryStatus") or "",
    }
