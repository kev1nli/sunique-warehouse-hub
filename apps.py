# ===== 应用清单：以后加新应用、改链接，只改这个文件 =====
# status: "live" = 可用, "build" = 开发中, "plan" = 规划中
# url: 应用的网址；还没有就留 ""

APPS = [
    {
        "name": "Warehouse Desk",
        "zh": "仓库工作台",
        "desc": "仓库日常工作入口：备货、提货和仓库任务一站处理。",
        "tags": ["仓库", "日常"],
        "status": "live",
        "url": "https://sunique-warehouse-desk-b7and5dkeaaqe4ay.southcentralus-01.azurewebsites.net/",
        "icon": "🗂️",
    },
    {
        "name": "Order Ready List",
        "zh": "备货完成清单",
        "desc": "查看哪些订单已备好可以提货或送货，销售和仓库共用。",
        "tags": ["订单", "提货"],
        "status": "live",
        "url": "https://sunique-order-ready.streamlit.app/warehouse",
        "icon": "✅",
    },
    {
        "name": "Freight Quote",
        "zh": "运费报价",
        "desc": "输入目的地和货量，快速估算送货或货运报价。",
        "tags": ["运费", "报价"],
        "status": "live",
        "url": "https://suniquefreight.streamlit.app/",
        "icon": "🚚",
    },
    {
        "name": "Delivery Schedule",
        "zh": "送货排程",
        "desc": "自动安排送货日期、路线和车辆，司机和销售都能看到最新排程。",
        "tags": ["送货", "排程"],
        "status": "build",
        "url": "",
        "icon": "📅",
    },
    {
        "name": "Assembly Schedule",
        "zh": "组装排程",
        "desc": "安排柜子组装任务和人手，跟踪每单组装进度。",
        "tags": ["组装", "排程"],
        "status": "plan",
        "url": "",
        "icon": "🔧",
    },
]
