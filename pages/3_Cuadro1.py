

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
from PIL import Image
from datetime import datetime
from zoneinfo import ZoneInfo
import random, io, time

st.set_page_config(page_title="Cuadro 1 — Rompecabezas", page_icon="🧩", layout="wide")

# Guard de autenticación
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Necesitas iniciar sesión para acceder a esta página.")
    try: st.switch_page("app.py")
    except Exception: st.stop()

#TZ = ZoneInfo("America/Guatemala")

st.title("🧩 Rompecabezas")
#st.caption(f"Hora local: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')}")

# --------------------
# CARGA DE IMAGEN
# --------------------
def load_base_image() -> Image.Image:
    # 1) Si definiste una URL en secrets
    url = st.secrets.get("PUZZLE_IMAGE_URL", "")
    if url:
        try:
            import urllib.request
            with urllib.request.urlopen(url) as resp:
                return Image.open(io.BytesIO(resp.read())).convert("RGB")
        except Exception as e:
            st.warning(f"No pude leer la URL de imagen. Motivo: {e}. Intento con archivo local…")
    # 2) Archivo local en el repo
    try:
        return Image.open("assets/rompecabezas.jpg").convert("RGB")
    except Exception:
        st.error("No encontré la imagen. Sube una o coloca assets/rompecabezas.jpg en el repo.")
        up = st.file_uploader("Sube la imagen del rompecabezas (JPG/PNG)", type=["jpg","jpeg","png"])
        if up:
            return Image.open(up).convert("RGB")
        st.stop()

base_img = load_base_image()

# --------------------
# CONFIG
# --------------------
N = st.sidebar.slider("Tamaño del rompecabezas (N×N)", min_value=3, max_value=6, value=3)
SIZE = 600  # lado del lienzo en px

def make_tiles(img: Image.Image, n: int, size: int):
    img = img.resize((size, size), Image.LANCZOS)
    step = size // n
    tiles = []
    for r in range(n):
        for c in range(n):
            box = (c*step, r*step, (c+1)*step, (r+1)*step)
            tiles.append(img.crop(box))
    return tiles

tiles_master = make_tiles(base_img, N, SIZE)
SOLVED = list(range(N*N))

# --------------------
# ESTADO
# --------------------
if "puzzle_state" not in st.session_state or st.session_state.get("puzzle_n") != N:
    st.session_state.puzzle_n = N
    st.session_state.tiles_order = SOLVED.copy()
    # Mezclar hasta que no quede resuelto
    while st.session_state.tiles_order == SOLVED:
        random.shuffle(st.session_state.tiles_order)
    st.session_state.sel = None
    st.session_state.moves = 0
    st.session_state.puzzle_solved = False

# --------------------
# UI
# --------------------
left, mid, right = st.columns([1,2,1])

with left:
    if st.button("🔀 Mezclar"):
        st.session_state.tiles_order = SOLVED.copy()
        while st.session_state.tiles_order == SOLVED:
            random.shuffle(st.session_state.tiles_order)
        st.session_state.sel = None
        st.session_state.moves = 0
        st.session_state.puzzle_solved = False
        st.rerun()

    st.metric("Movimientos", st.session_state.moves)

with right:
    # Botón Siguiente cuadro (solo si está resuelto)
    disabled = not st.session_state.get("puzzle_solved", False)
    if st.button("➡️ Siguiente cuadro", disabled=disabled):
        try: st.switch_page("pages/4_Cuadro2.py")
        except Exception: st.rerun()

# Render del tablero (click dos veces para intercambiar)
board = st.container()
tile_w = SIZE // N

# Para resaltar la selección, ponemos un borde cuando esté seleccionada
def with_border(im: Image.Image, color=(255, 80, 80)):
    # añadir borde de 4px
    from PIL import ImageOps
    return ImageOps.expand(im, border=4, fill=color)

# Dibujar en N columnas por fila
rows = [st.columns(N, gap="small") for _ in range(N)]

# Pintar grid y manejar clicks
for r in range(N):
    for c in range(N):
        pos = r*N + c               # posición en el tablero
        tile_idx = st.session_state.tiles_order[pos]  # índice de ficha
        tile_img = tiles_master[tile_idx]

        # si está seleccionada esta posición, poner borde
        sel = st.session_state.sel
        if sel is not None and sel == pos:
            tile_img = with_border(tile_img)

        with rows[r][c]:
            # mostramos la imagen
            st.image(tile_img, use_container_width=True)
            # botón para seleccionar esta casilla
            if st.button(" ", key=f"tile_{pos}", help=f"Seleccionar casilla {pos+1}", use_container_width=True):
                if st.session_state.sel is None:
                    st.session_state.sel = pos
                else:
                    a = st.session_state.sel
                    b = pos
                    if a != b:
                        # intercambiar fichas
                        order = st.session_state.tiles_order
                        order[a], order[b] = order[b], order[a]
                        st.session_state.moves += 1
                    st.session_state.sel = None

                    # comprobar si está resuelto
                    if st.session_state.tiles_order == SOLVED:
                        st.balloons()
                        st.success(f"🎉 ¡Rompecabezas resuelto en {st.session_state.moves} movimientos!")
                        st.session_state.puzzle_solved = True
                st.rerun()

# Mensaje de estado
if not st.session_state.puzzle_solved:
    st.info("Selecciona una casilla y luego otra para **intercambiar** las piezas.")
else:
    st.success("✅ Listo. Ya puedes pasar al **Cuadro 2** desde este botón o el menú.")

