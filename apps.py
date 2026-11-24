# ===== App list: add new apps or change links here =====
# status: "live" = available, "build" = in development, "plan" = planned
# url: the app's web address; leave "" if it has none yet

APPS = [
    {
        "name": "Warehouse Desk",
        "desc": "Daily warehouse workspace for order prep, pickups and warehouse tasks.",
        "tags": ["Warehouse", "Daily"],
        "status": "live",
        "url": "https://sunique-warehouse-desk-b7and5dkeaaqe4ay.southcentralus-01.azurewebsites.net/",
        "icon": "🗂️",
    },
    {
        "name": "Order Ready List",
        "desc": "See which orders are prepped and ready for pickup or delivery. Shared by sales and warehouse.",
        "tags": ["Orders", "Pickup"],
        "status": "live",
        "url": "https://sunique-order-ready.streamlit.app/warehouse",
        "icon": "✅",
    },
    {
        "name": "Freight Quote",
        "desc": "Enter a destination and load size to get a quick delivery or freight estimate.",
        "tags": ["Freight", "Quote"],
        "status": "live",
        "url": "https://suniquefreight.streamlit.app/",
        "icon": "🚚",
    },
    {
        "name": "Delivery Schedule",
        "desc": "Beta: enter an order and get the delivery dates that fit the route, with a recommended date and time slot.",
        "tags": ["Delivery", "Schedule"],
        "status": "build",
        "url": "/Delivery_Planner",
        "icon": "📅",
    },
    {
        "name": "Assembly Schedule",
        "desc": "Schedule cabinet assembly jobs and crew, and track progress on each order.",
        "tags": ["Assembly", "Schedule"],
        "status": "plan",
        "url": "",
        "icon": "🔧",
    },
]
