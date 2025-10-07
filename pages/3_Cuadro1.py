import streamlit as st
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Cuadro 1", page_icon="1️⃣", layout="wide")

# Guard
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Necesitas iniciar sesión para acceder a esta página.")
    try:
        st.switch_page("app.py")
    except Exception:
        st.stop()

st.title("1️⃣ Cuadro 1 — Tu contenido aquí")
st.write("Pon aquí el contenido del Cuadro 1 (gráficas, métricas, formularios, etc.).")

if st.button("⬅️ Volver a Contenido"):
    try:
        st.switch_page("pages/2_Contenido.py")
    except Exception:
        st.rerun()
