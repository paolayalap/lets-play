

#st.set_page_config(page_title="Cuadro 1", page_icon="1️⃣", layout="wide")

# Guard
#if "authenticated" not in st.session_state or not st.session_state.authenticated:
#    st.warning("Necesitas iniciar sesión para acceder a esta página.")
#    try:
#        st.switch_page("app.py")
#    except Exception:
#        st.stop()

#st.title("1️⃣ Cuadro 1 — Tu contenido aquí")
#st.write("Pon aquí el contenido del Cuadro 1 (gráficas, métricas, formularios, etc.).")

#if st.button("⬅️ Volver a Contenido"):
#    try:
#        st.switch_page("pages/2_Contenido.py")
#    except Exception:
#        st.rerun()

#####################
import streamlit as st
from PIL import Image, ImageOps
from datetime import datetime
from zoneinfo import ZoneInfo
import random, io

st.set_page_config(page_title="Cuadro 1 — Rompecabezas", page_icon="🧩", layout="wide")

# ======= Guard de autenticación =======
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Necesitas iniciar sesión para acceder a esta página.")
    try:
        st.switch_page("app.py")
    except Exception:
        st.stop()

TZ = ZoneInfo("America/Guatemala")
st.title("🧩 Rompecabezas")
st.caption(f"Hora local: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')}")
st.subheader("Arma el rompecabezas")
st.write("Bueno mi lindo, este es el primer juego. Como dirías tu ¡Sencillo!👌 Jajaja son bromas corazón. Para darte contexto, esta es una imagen o una representación visual de nuestra casita ideal. Esta es una idea generada por IA, a mi me gusta mucho sobretodo porque se parece a la casita de Minecraft (aunque le falta el huerto🪴 con nuestras vacas🐮, caballitos🐴 y cerditos🐷).")
st.write("Es una idea de nuestra casita, porque nuestro hogar somos tu y yo sin importar donde estemos❤️🏘️❤️.")

# ======= Config fija (6x6) =======
N = 3              # <-- fijo, sin slider
SIZE = 720         # tamaño del lienzo cuadrado en px (ajusta si quieres más/menos grande)

# ======= Carga de imagen =======
def load_base_image() -> Image.Image:
    url = st.secrets.get("PUZZLE_IMAGE_URL", "")
    if url:
        try:
            import urllib.request
            with urllib.request.urlopen(url) as resp:
                return Image.open(io.BytesIO(resp.read())).convert("RGB")
        except Exception as e:
            st.warning(f"No pude leer PUZZLE_IMAGE_URL: {e}. Intento con archivo local…")
    try:
        return Image.open("assets/rompecabezas.jpg").convert("RGB")
    except Exception:
        st.error("No encontré assets/rompecabezas.jpg. Sube la imagen ahí o define PUZZLE_IMAGE_URL en Secrets.")
        up = st.file_uploader("Sube la imagen del rompecabezas (JPG/PNG)", type=["jpg","jpeg","png"])
        if up:
            return Image.open(up).convert("RGB")
        st.stop()

base_img = load_base_image().resize((SIZE, SIZE), Image.LANCZOS)

# ======= Construcción de tiles =======
def make_tiles(img: Image.Image, n: int):
    step = img.width // n
    tiles = []
    for r in range(n):
        for c in range(n):
            box = (c*step, r*step, (c+1)*step, (r+1)*step)
            tiles.append(img.crop(box))
    return tiles

tiles_master = make_tiles(base_img, N)
SOLVED = list(range(N*N))

# ======= Estado del puzzle =======
def init_puzzle():
    st.session_state.puzzle_n = N
    st.session_state.tiles_order = SOLVED.copy()
    while st.session_state.tiles_order == SOLVED:
        random.shuffle(st.session_state.tiles_order)
    st.session_state.sel = None      # casilla seleccionada (índice pos 0..N*N-1)
    st.session_state.moves = 0
    st.session_state.puzzle_solved = False

if "puzzle_n" not in st.session_state or st.session_state.puzzle_n != N:
    init_puzzle()

# ======= Controles superiores =======
left, sp, right = st.columns([1,2,1])

with left:
    if st.button("🔀 Mezclar"):
        init_puzzle()
        st.rerun()
    st.metric("Movimientos", st.session_state.get("moves", 0))

with right:
    # Habilitar solo si está resuelto
    disabled = not st.session_state.get("puzzle_solved", False)
    if st.button("➡️ Siguiente cuadro", disabled=disabled):
        try:
            st.switch_page("pages/4_Cuadro2.py")
        except Exception:
            st.rerun()

st.divider()

# ======= Render del tablero =======
def bordered(im: Image.Image, color=(255, 80, 80), px=4):
    return ImageOps.expand(im, border=px, fill=color)

rows = [st.columns(N, gap="small") for _ in range(N)]

for r in range(N):
    for c in range(N):
        pos = r*N + c
        tile_idx = st.session_state.tiles_order[pos]
        tile_img = tiles_master[tile_idx]

        # Si esta casilla está seleccionada, le ponemos borde
        if st.session_state.sel is not None and st.session_state.sel == pos:
            tile_img = bordered(tile_img)

        with rows[r][c]:
            st.image(tile_img, use_container_width=True)
            # El botón no tiene texto visible, solo ocupa el ancho para el click
            if st.button(" ", key=f"tile_btn_{pos}", help=f"Seleccionar casilla {pos+1}", use_container_width=True):
                # Primera selección
                if st.session_state.sel is None:
                    st.session_state.sel = pos
                    st.rerun()
                else:
                    a = st.session_state.sel
                    b = pos
                    # Si son diferentes, intercambiar
                    if a != b:
                        order = st.session_state.tiles_order
                        order[a], order[b] = order[b], order[a]
                        st.session_state.moves += 1
                    # Quitar selección
                    st.session_state.sel = None
                    # ¿Quedó resuelto?
                    if st.session_state.tiles_order == SOLVED:
                        st.session_state.puzzle_solved = True
                        st.balloons()
                        st.success(f"🎉 ¡Rompecabezas resuelto en {st.session_state.moves} movimientos!")
                    st.rerun()

# Mensaje de estado
if not st.session_state.puzzle_solved:
    st.info("Selecciona una casilla y luego otra para **intercambiar** las piezas (solo esas dos).")
else:
    st.success("✅ Listo. Ya puedes pasar al **Cuadro 2**.")
