import streamlit as st

# --- CONFIGURACIÓN BÁSICA ---
st.set_page_config(page_title="Acceso con contraseña", page_icon="🔒")

# --- BLOQUE DE CONTRASEÑA ---
st.title("🔒 Acceso restringido")

# Campo para ingresar la contraseña (el texto se oculta)
password = st.text_input("Introduce la contraseña:", type="password")

# Contraseña correcta (puedes cambiarla o encriptarla si quieres)
CORRECT_PASSWORD = "felicid4desAMOR"

# Verificación
if password:
    if password == CORRECT_PASSWORD:
        st.success("✅ Acceso concedido. Bienvenido mi amor 😍.")
        # Aquí puedes colocar el contenido protegido
        st.write("Ahora puedes acceder a las secciones internas de la app.")
    else:
        st.error("❌ Contraseña incorrecta. Intenta de nuevo.")
else:
    st.info("Por favor, ingresa tu contraseña para continuar.")
