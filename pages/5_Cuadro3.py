import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import random, time
from PIL import Image

st.set_page_config(page_title="Cuadro 3 — Memoria", page_icon="🧠", layout="wide")

# ====== Guard: login y gating desde Cuadro 2 ======
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Necesitas iniciar sesión para acceder a esta página.")
    try: st.switch_page("app.py")
    except Exception: st.stop()

if not st.session_state.get("cuadro2_solved", False):
    st.error("Debes completar el Juego 2 antes de entrar al Juego 3.")
    if st.button("⬅️ Ir al Cuadro 2"):
        try: st.switch_page("pages/4_Cuadro2.py")
        except Exception: st.rerun()
    st.stop()

TZ = ZoneInfo("America/Guatemala")
st.title("Juego de Memoria 📷")
st.caption(f"Hora local: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')}")
st.subheader("Empareja las fotos")
st.write("En este juego mi lindo, hay fotos de nosotros de momentos increíbles💖. La idea es que al terminar el juego tengas un pequeño collage nuestro de recuerdos de este año amor💫.")

# ====== Configuración de imágenes (10 pares -> 20 cartas) ======
IMG_PATHS = [
    "assets/1.jpeg",
    "assets/2.jpeg",
    "assets/3.jpeg",
    "assets/4.jpeg",
    "assets/5.jpeg",
    "assets/6.jpeg",
    "assets/7.jpeg",
    "assets/8.jpeg",
    "assets/9.jpeg",
    "assets/10.jpeg",
]
NUM_PAIRS = len(IMG_PATHS)
COLS = 5          # 5 columnas x 4 filas
CARD_SIZE = 140   # tamaño visual (px aprox)

# ====== Estilos para las cartas ======
st.markdown(f"""
<style>
.mem-grid .card-btn button {{
    height: {CARD_SIZE}px; width: 100%;
    border-radius: 16px; border: 0;
    box-shadow: 0 3px 8px rgba(0,0,0,.12);
    background: linear-gradient(180deg, #e5e7eb, #d1d5db);
    font-size: 32px; font-weight: 900;
}}
.mem-grid .img-wrap {{
    width: 100%;
    aspect-ratio: 1/1;
    overflow: hidden; border-radius: 16px;
    box-shadow: 0 3px 8px rgba(0,0,0,.12);
    border: 2px solid rgba(0,0,0,.05);
}}
.mem-grid .img-wrap.matched {{
    border-color: #16a34a;
    box-shadow: 0 0 0 3px rgba(22,163,74,.25);
}}
</style>
""", unsafe_allow_html=True)

# ====== Estado ======
def init_game():
    # baraja con dos copias de cada id de imagen
    ids = list(range(NUM_PAIRS)) * 2
    random.shuffle(ids)
    st.session_state.mem_cards = [
        {"img_id": i, "revealed": False, "matched": False} for i in ids
    ]
    st.session_state.mem_revealed = []  # índices de cartas reveladas (0,1 o 2)
    st.session_state.mem_moves = 0
    st.session_state.mem_matches = 0
    st.session_state.flip_deadline = None
    st.session_state.cuadro3_solved = False

if "mem_cards" not in st.session_state:
    init_game()

cards = st.session_state.mem_cards

# Si hay dos destapadas que no coinciden y pasó el tiempo, volver a tapar
if st.session_state.flip_deadline and time.time() >= st.session_state.flip_deadline:
    a, b = st.session_state.mem_revealed
    cards[a]["revealed"] = False
    cards[b]["revealed"] = False
    st.session_state.mem_revealed = []
    st.session_state.flip_deadline = None
    st.rerun()

# ====== Header con estadísticas y acciones ======
c1, c2, c3, c4 = st.columns([1,1,1,2])
with c1:
    st.metric("Pares encontrados", f"{st.session_state.mem_matches}/{NUM_PAIRS}")
with c2:
    st.metric("Movimientos", st.session_state.mem_moves)
with c3:
    if st.button("🔄 Reiniciar"):
        init_game()
        st.rerun()
with c4:
    if st.button("⬅️ Volver a Contenido"):
        try: st.switch_page("pages/2_Contenido.py")
        except Exception: st.rerun()

st.write("")

# ====== Grid de cartas ======
rows = (len(cards) + COLS - 1) // COLS
container = st.container()
container.markdown("<div class='mem-grid'>", unsafe_allow_html=True)

for r in range(rows):
    cols = st.columns(COLS, gap="large")
    for c in range(COLS):
        idx = r * COLS + c
        if idx >= len(cards):
            continue
        card = cards[idx]
        img_path = IMG_PATHS[card["img_id"]]

        with cols[c]:
            if card["revealed"] or card["matched"]:
                # Mostrar imagen
                klass = "img-wrap matched" if card["matched"] else "img-wrap"
                st.markdown(f"<div class='{klass}'>", unsafe_allow_html=True)
                st.image(Image.open(img_path), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                # Botón "boca abajo"
                with st.container():
                    st.markdown("<div class='card-btn'>", unsafe_allow_html=True)
                    if st.button("?", key=f"mem_{idx}", use_container_width=True):
                        # No dejes destapar si ya hay 2 abiertas o si está en espera de flip
                        if len(st.session_state.mem_revealed) < 2 and not st.session_state.flip_deadline:
                            card["revealed"] = True
                            st.session_state.mem_revealed.append(idx)

                            if len(st.session_state.mem_revealed) == 2:
                                a, b = st.session_state.mem_revealed
                                st.session_state.mem_moves += 1
                                if cards[a]["img_id"] == cards[b]["img_id"]:
                                    # ¡Match!
                                    cards[a]["matched"] = True
                                    cards[b]["matched"] = True
                                    st.session_state.mem_revealed = []
                                    st.session_state.mem_matches += 1
                                    if st.session_state.mem_matches == NUM_PAIRS:
                                        st.session_state.cuadro3_solved = True
                                        st.balloons()
                                        st.success("🎉 ¡Completaste todas las parejas!")
                                else:
                                    # Programar volteo
                                    st.session_state.flip_deadline = time.time() + 0.8
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

container.markdown("</div>", unsafe_allow_html=True)

st.write("")
# ====== Botón Siguiente cuadro ======
disabled_next = not st.session_state.get("cuadro3_solved", False)
if st.button("➡️ Siguiente cuadro", disabled=disabled_next):
    try:
        st.switch_page("pages/6_Cuadro4.py")
    except Exception:
        st.rerun()
