import streamlit as st

st.set_page_config(page_title="Acceso con contraseña", page_icon="🔒")

st.title("🔒 Acceso restringido")

# Lee la contraseña desde secrets (configurada en el Cloud)
CORRECT_PASSWORD = st.secrets.get("password", "")

# Estado de sesión
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Si no está autenticada, pide contraseña
if not st.session_state.authenticated:
    with st.form("login_form"):
        password = st.text_input("Introduce la contraseña:", type="password")
        submitted = st.form_submit_button("Entrar")
    if submitted:
        if CORRECT_PASSWORD and password == CORRECT_PASSWORD:
            st.session_state.authenticated = True
            st.success("✅ Acceso concedido. Bienvenido mi amor 😍.")
            st.rerun()
        else:
            st.error("❌ Contraseña incorrecta. Intenta de nuevo.")
else:
    # Contenido protegido
    st.success("💖 Acceso autorizado.")
    st.write("Ahora puedes acceder a las secciones internas de la app.")
    if st.button("Cerrar sesión"):
        st.session_state.authenticated = False
        st.rerun()
