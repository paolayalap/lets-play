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
            # Redirige a la página protegida
            try:
                st.switch_page("pages/2_Contenido.py")  # Streamlit ≥ 1.26
            except Exception:
                st.experimental_rerun()
        else:
            st.error("❌ Contraseña incorrecta. Intenta de nuevo.")
else:
    # Si ya está autenticada, manda directo al contenido
    try:
        st.switch_page("pages/2_Contenido.py")
    except Exception:
        st.info("✅ Ya autenticado. Abre la página 'Contenido' en el menú.")
