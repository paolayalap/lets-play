import streamlit as st

st.set_page_config(page_title="Cuadro 4", page_icon="4️⃣", layout="wide")

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Necesitas iniciar sesión para acceder a esta página.")
    try:
        st.switch_page("app.py")
    except Exception:
        st.stop()

st.title("4️⃣ Cuadro 4 — Tu contenido aquí")
st.write("Pon aquí el contenido del Cuadro 4.")

if st.button("⬅️ Volver a Contenido"):
    try:
        st.switch_page("pages/2_Contenido.py")
    except Exception:
        st.rerun()
