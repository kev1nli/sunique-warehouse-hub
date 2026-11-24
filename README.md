# Sunique Warehouse Hub

公司仓库工具的统一入口（Streamlit）。

## 文件
- `streamlit_app.py`：门户页面
- `apps.py`：应用清单，加新应用或改网址只改这里
- `requirements.txt`：依赖

## 部署到 Streamlit Community Cloud
1. 在 GitHub 新建一个仓库（例如 `sunique-warehouse-hub`），把这三个文件上传到根目录。
2. 打开 https://share.streamlit.io ，点 **Create app**，选这个仓库，Main file 填 `streamlit_app.py`。
3. 可以自定义网址，例如 `sunique-warehouse.streamlit.app`。
4. 部署后在 app 的 **Settings → Sharing** 里确认是 **Public**（任何人有链接都能打开，不需要登录）。

## 以后更新
在 GitHub 上编辑 `apps.py`，保存后 Streamlit 会自动重新部署。
