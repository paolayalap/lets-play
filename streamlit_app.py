import streamlit as st

st.set_page_config(page_title="Acceso con contraseña", page_icon="🔒")

st.title("🔒 Acceso restringido")

# Contraseña correcta
CORRECT_PASSWORD = "felicid4desAMOR"

# Si no hay una variable de sesión, créala
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Si el usuario aún no se autenticó, pide la contraseña
if not st.session_state.authenticated:
    password = st.text_input("Introduce la contraseña:", type="password")
    if password:
        if password == CORRECT_PASSWORD:
            st.session_state.authenticated = True
            st.success("✅ Acceso concedido. Bienvenido mi amor 😍.")
        else:
            st.error("❌ Contraseña incorrecta. Intenta de nuevo.")
else:
    # Contenido protegido
    st.success("💖 Acceso autorizado.")
    st.write("Ahora puedes acceder a las secciones internas de la app.")
    if st.button("Cerrar sesión"):
        st.session_state.authenticated = False
