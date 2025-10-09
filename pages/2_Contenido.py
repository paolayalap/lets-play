import streamlit as st
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import time

st.set_page_config(page_title="Contenido protegido", page_icon="🗝️", layout="wide")

# --- Guard: si no hay sesión, regresa al login ---
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Necesitas iniciar sesión para acceder a esta página.")
    try:
        st.switch_page("app.py")
    except Exception:
        st.stop()

# --- Zona horaria: Guatemala ---
TZ = ZoneInfo("America/Guatemala")

# 👉 El Cuadro 1 se activa desde el 14/oct/2025 (inclusive)
AVAILABLE_FROM = datetime(2025, 10, 14, 0, 0, 0, tzinfo=TZ)

# --- Encabezado con fecha actual ---
now = datetime.now(TZ)
st.markdown(f"### 📅 Fecha actual: **{now.strftime('%Y-%m-%d %H:%M:')[:-3]}**")

st.divider()

# =========================
#  CUADROS → BOTONES (ÚNICO BLOQUE)
# =========================
st.markdown("""
<style>
:root { --card-h: 140px; }
/* Estilo base para los 4 botones dentro de sus wrappers #card1..#card4 */
#card1 .stButton>button, #card2 .stButton>button, #card3 .stButton>button, #card4 .stButton>button {
    height: var(--card-h); width: 100%;
    border-radius: 16px !important;
    font-weight: 800 !important; font-size: 20px !important;
    box-shadow: 0 2px 6px rgba(0,0,0,.08) !important;
    border: 0 !important; background-image: none !important;
}
/* Colores pastel (forzados) */
#card1 .stButton>button { background-color: #FDE68A !important; color: #111 !important; }
#card2 .stButton>button { background-color: #A7F3D0 !important; color: #111 !important; }
#card3 .stButton>button { background-color: #BFDBFE !important; color: #111 !important; }
#card4 .stButton>button { background-color: #FBCFE8 !important; color: #111 !important; }
/* Hover / Active */
#card1 .stButton>button:hover, #card2 .stButton>button:hover,
#card3 .stButton>button:hover, #card4 .stButton>button:hover {
    filter: brightness(0.97); transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(0,0,0,.12) !important;
}
#card1 .stButton>button:active, #card2 .stButton>button:active,
#card3 .stButton>button:active, #card4 .stButton>button:active {
    transform: translateY(0); filter: none;
}
</style>
""", unsafe_allow_html=True)

titles = ["Cuadro 1", "Cuadro 2", "Cuadro 3", "Cuadro 4"]
cols = st.columns(4, gap="large")

# Mapa: botón -> página destino
page_map = {
    1: "pages/3_Cuadro1.py",
    2: "pages/4_Cuadro2.py",
    3: "pages/5_Cuadro3.py",
    4: "pages/6_Cuadro4.py",
}

def go_to(i: int):
    # Si es el Cuadro 1 y aún no es 14/oct/2025, solo muestra el mensaje
    if i == 1 and datetime.now(TZ) < AVAILABLE_FROM:
        st.info("Espera mi amor, ya falta poco, te amo mucho ❤️")
        return

    # 1 -> Rompecabezas, 2 -> Crucigrama, 3 -> Memoria, 4 -> siguiente actividad...
    if i == 2 and not st.session_state.get("puzzle_solved", False):
        st.warning("Debes completar el Cuadro 1 (rompecabezas) antes de continuar.")
        return
    if i == 3 and not st.session_state.get("cuadro2_solved", False):
        st.warning("Debes completar el Cuadro 2 (crucigrama) antes de continuar.")
        return
    if i == 4 and not st.session_state.get("cuadro3_solved", False):
        st.warning("Debes completar el Cuadro 3 (memoria) antes de continuar.")
        return

    try:
        st.switch_page(page_map[i])
    except Exception:
        st.info("No puedes navegar automáticamente. Abre la página desde el menú lateral.")

KEY_PREFIX = "cards_v3"  # prefijo único para las keys

for i, col in enumerate(cols, start=1):
    with col:
        st.markdown(f"<div id='card{i}'>", unsafe_allow_html=True)
        clicked = st.button(f"{i} · {titles[i-1]}", key=f"{KEY_PREFIX}_{i}", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if clicked:
            st.session_state.selected_card = i
            st.toast(f"Has presionado el botón {i}: {titles[i-1]}")
            go_to(i)

st.divider()

# =========================
#  CONTADOR REGRESIVO
# =========================
st.markdown("### ⏳ Tiempo restante para **14 de octubre de 2025**")
target = datetime(2025, 10, 9, 0, 0, 0, tzinfo=TZ)  # ← tu target de prueba actual
placeholder = st.empty()

def render_countdown(delta: timedelta):
    total_ms = int(delta.total_seconds() * 1000)
    if total_ms <= 0:
        placeholder.success("🎉 ¡14 de octubre de 2025 ha llegado!")
        st.balloons()
        return False

    days = delta.days
    secs_rem = delta.seconds
    hrs = secs_rem // 3600
    mins = (secs_rem % 3600) // 60
    secs = (secs_rem % 60)
    ms = delta.microseconds // 1000

    html = f"""
    <div style="font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace;
                font-size: 28px; font-weight: 700; text-align:center;">
        <span style="display:inline-block; min-width:120px;">{days:02d} <small style="font-weight:400;">días</small></span>
        :
        <span style="display:inline-block; min-width:120px;">{hrs:02d} <small style="font-weight:400;">horas</small></span>
        :
        <span style="display:inline-block; min-width:120px;">{mins:02d} <small style="font-weight:400;">min</small></span>
        :
        <span style="display:inline-block; min-width:120px;">{secs:02d} <small style="font-weight:400;">seg</small></span>
        :
        <span style="display:inline-block; min-width:140px;">{ms:03d} <small style="font-weight:400;">ms</small></span>
    </div>
    """
    placeholder.markdown(html, unsafe_allow_html=True)
    return True

# Toggle para activar/pausar actualización en vivo (cada 100 ms)
live = st.toggle("Actualizar contador en vivo (cada 100 ms)", value=True, help="Desactívalo si notas la app lenta.")

if live:
    t_end = time.time() + 3  # refresca ~3 s y luego re-ejecuta el script
    while time.time() < t_end:
        now = datetime.now(TZ)
        delta = target - now
        if not render_countdown(delta):
            break
        time.sleep(0.1)
    st.rerun()
else:
    now = datetime.now(TZ)
    delta = target - now
    render_countdown(delta)

# --- 👇 ADICIÓN: Globos animados en los bordes durante TODO el día del 'target' ---
if datetime.now(TZ).date() == target.date():
    st.markdown("""
    <style>
    .balloons-overlay{
        position: fixed; inset: 0; pointer-events: none; z-index: 9999;
    }
    .balloons-strip{
        position: absolute; top: 0; height: 100vh; width: 64px; display: block;
    }
    .balloons-left{ left: 0; }
    .balloons-right{ right: 0; }
    .b{
        position: absolute; left: 8px;
        font-size: 28px; opacity: .95;
        animation: rise linear infinite;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,.25));
    }
    @keyframes rise {
        0%   { transform: translateY(110vh) rotate(0deg); }
        100% { transform: translateY(-10vh) rotate(12deg); }
    }
    </style>

    <div class="balloons-overlay">
      <div class="balloons-strip balloons-left">
        <span class="b" style="animation-duration: 7s;  animation-delay: 0s;">🎈</span>
        <span class="b" style="animation-duration: 8.5s;animation-delay: 1s; left: 24px;">🎈</span>
        <span class="b" style="animation-duration: 9s;  animation-delay: 2.2s;">🎈</span>
        <span class="b" style="animation-duration: 7.8s;animation-delay: 3.4s; left: 20px;">🎈</span>
        <span class="b" style="animation-duration: 8.2s;animation-delay: 4.6s;">🎈</span>
      </div>
      <div class="balloons-strip balloons-right">
        <span class="b" style="animation-duration: 7.5s;animation-delay: .6s; left: 24px;">🎈</span>
        <span class="b" style="animation-duration: 9.2s;animation-delay: 1.8s;">🎈</span>
        <span class="b" style="animation-duration: 8s;  animation-delay: 2.9s; left: 18px;">🎈</span>
        <span class="b" style="animation-duration: 9s;  animation-delay: 3.7s;">🎈</span>
        <span class="b" style="animation-duration: 8.4s;animation-delay: 4.9s; left: 26px;">🎈</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# --- Controles útiles ---
st.write("")
cols2 = st.columns([1,1,2,2])
with cols2[0]:
    if st.button("🔁 Refrescar una vez"):
        st.rerun()
with cols2[1]:
    if st.button("🚪 Cerrar sesión"):
        st.session_state.authenticated = False
        try:
            st.switch_page("app.py")
        except Exception:
            st.rerun()
