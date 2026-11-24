# Sunique Warehouse Hub

One place for Sunique's warehouse apps and SOPs (Streamlit).

Live: https://sunique-warehouse-app.streamlit.app/

## Files
- `streamlit_app.py` – the hub page
- `apps.py` – list of apps (add an app or change a link here)
- `sops.py` – list of SOPs
- `sops/` – SOP PDF files
- `logo.png`, `favicon.png` – branding
- `requirements.txt` – dependencies

## Add an SOP
1. Upload the PDF into the `sops/` folder.
2. Add an entry to `SOPS` in `sops.py` (title, desc, category, file, updated).
3. Commit. Streamlit redeploys automatically.

## Add or update an app
Edit `apps.py` and commit.
