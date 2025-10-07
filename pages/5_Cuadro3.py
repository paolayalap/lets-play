import streamlit as st

st.set_page_config(page_title="Cuadro 3", page_icon="3️⃣", layout="wide")

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Necesitas iniciar sesión para acceder a esta página.")
    try:
        st.switch_page("app.py")
    except Exception:
        st.stop()

st.title("3️⃣ Cuadro 3 — Tu contenido aquí")
st.write("Pon aquí el contenido del Cuadro 3.")

if st.button("⬅️ Volver a Contenido"):
    try:
        st.switch_page("pages/2_Contenido.py")
    except Exception:
        st.rerun()
