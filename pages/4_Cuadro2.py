import streamlit as st

st.set_page_config(page_title="Cuadro 2", page_icon="2️⃣", layout="wide")

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Necesitas iniciar sesión para acceder a esta página.")
    try: st.switch_page("app.py")
    except Exception: st.stop()

if not st.session_state.get("puzzle_solved", False):
    st.error("Debes completar el Cuadro 1 (rompecabezas) antes de entrar aquí.")
    if st.button("⬅️ Ir al Cuadro 1"):
        try: st.switch_page("pages/3_Cuadro1.py")
        except Exception: st.rerun()
    st.stop()

st.title("2️⃣ Cuadro 2 — Actividad desbloqueada")
st.write("Aquí va la actividad del Cuadro 2…")
