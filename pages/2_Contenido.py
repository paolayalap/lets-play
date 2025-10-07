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

# --- Encabezado con fecha actual ---
now = datetime.now(TZ)
st.markdown(f"### 📅 Fecha actual (America/Guatemala): **{now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}**")

st.divider()

# =========================
#  CUADROS → BOTONES
# =========================
colors = ["#FDE68A", "#A7F3D0", "#BFDBFE", "#FBCFE8"]  # pastel: amarillo, verde, azul, rosa
titles = ["Cuadro 1", "Cuadro 2", "Cuadro 3", "Cuadro 4"]

cols = st.columns(4, gap="large")

# CSS para estilizar SOLO estos 4 botones, usando wrappers con id único
st.markdown("""
<style>
:root { --card-h: 140px; }
#card1 .stButton>button, #card2 .stButton>button, #card3 .stButton>button, #card4 .stButton>button {
    height: var(--card-h);
    border-radius: 16px;
    font-weight: 800;
    font-size: 20px;
    box-shadow: 0 2px 6px rgba(0,0,0,.08);
    border: 0;
}
#card1 .stButton>button { background: #FDE68A; color:#111; }
#card2 .stButton>button { background: #A7F3D0; color:#111; }
#card3 .stButton>button { background: #BFDBFE; color:#111; }
#card4 .stButton>button { background: #FBCFE8; color:#111; }
#card1 .stButton>button:hover,
#card2 .stButton>button:hover,
#card3 .stButton>button:hover,
#card4 .stButton>button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(0,0,0,.12);
}
#card1 .stButton>button:active,
#card2 .stButton>button:active,
#card3 .stButton>button:active,
#card4 .stButton>button:active {
    transform: translateY(0);
}
</style>
""", unsafe_allow_html=True)

if "selected_card" not in st.session_state:
    st.session_state.selected_card = None

for i, col in enumerate(cols, start=1):
    with col:
        st.markdown(f"<div id='card{i}'>", unsafe_allow_html=True)
        clicked = st.button(f"{i} · {titles[i-1]}", key=f"card_btn_{i}", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if clicked:
            st.session_state.selected_card = i
            st.toast(f"Has presionado el botón {i}: {titles[i-1]}")

            # try:
            #     st.switch_page(f"pages/{i+2}_Subpagina{i}.py")
            # except Exception:
            #     pass

st.divider()

# =========================
#  CONTADOR REGRESIVO
# =========================
st.markdown("### ⏳ Tiempo restante para **14 de octubre de 2025**")
target = datetime(2025, 10, 14, 0, 0, 0, tzinfo=TZ)
placeholder = st.empty()

def render_countdown(delta: timedelta):
    total_ms = int(delta.total_seconds() * 1000)
    if total_ms < 0:
        placeholder.success("🎉 ¡14 de octubre de 2025 ha llegado!")
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
