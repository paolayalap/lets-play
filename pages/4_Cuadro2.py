import streamlit as st
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Cuadro 2 — Crucigrama", page_icon="🧠", layout="wide")

# ====== Guard: login y gating desde el Cuadro 1 ======
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Necesitas iniciar sesión para acceder a esta página.")
    try: st.switch_page("app.py")
    except Exception: st.stop()

if not st.session_state.get("puzzle_solved", False):
    st.error("Debes completar el Cuadro 1 (rompecabezas) antes de entrar al Crucigrama.")
    if st.button("⬅️ Ir al Cuadro 1"):
        try: st.switch_page("pages/3_Cuadro1.py")
        except Exception: st.rerun()
    st.stop()

TZ = ZoneInfo("America/Guatemala")
st.title("🧠 Crucigrama")
st.caption(f"Hora local: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')}")

# ===================================================================================
# 1) REEMPLAZA ESTA LISTA CON TUS PREGUNTAS Y RESPUESTAS (sin tildes mejor; igual se limpia)
#    - La respuesta puede traer espacios o tildes; se normaliza a letras [a-z] sin acento.
# ===================================================================================
CLUES = [
    # ("pregunta", "respuesta")
    ("Cada fin de mes es el...","buffetaco"),
    ("La mezcla de nuestros colores favoritos es el color...","morado"),
    ("Desde siempre te ha gustado un juego de nintendo llamado","metroid"),
    ("Tu dices rana y yo...","salto"),
    ("Los tacos son ricos, pero no más que...","tu"),
    ("Cuando viajemos a Alemania fijo hay que ir por una...","chela"),
    ("Debemos encontrar la receta del... de &café","blackfrost"),
    ("Si por nosotros fuera, ya estuvieramos...","casados"),
    ("Este juego tiene varias adaptaciones como: la puerta del infierno y aniquilación","doom"),
    ("En las noches o en tiempo libres se juega...para repartir democracia","helldivers"),
    ("...es un sanguinario señor de la guerra proveninente de tiempos olvidados al que los siglos han visto nacer en tres ocasiones y morir en otras dos","mordekaiser"),
    ("No hay mejor escudería en fórmula 1 que...","mclaren"),
    ("Es como un mundo donde construímos nuestra casa, nuestro huerto y luchamos contra monstruos","minecraft"),
    ("Es el comandante supremo de los Autobots en su lucha contra los Decepticons","optimusprime"),
]

# ===================================================================================
# 2) Normalización: a minúscula, sin tildes, solo letras [a-z]
# ===================================================================================
def normalize_answer(s: str) -> str:
    s = s.lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")  # quita acentos
    # quedarnos con solo letras a-z
    s = "".join(ch for ch in s if "a" <= ch <= "z")
    return s

# Prepara estructura: [(clue_text, word)]
WORDS = []
for q, a in CLUES:
    w = normalize_answer(a)
    if not w:
        st.error(f"La respuesta '{a}' quedó vacía tras normalizar. Revísala.")
        st.stop()
    WORDS.append((q, w))

# ===================================================================================
# 3) Construcción simple del crucigrama (colocación greedy con cruces cuando coinciden letras)
#    Representación en coordenadas libres y luego se recorta a una grilla compacta.
# ===================================================================================
from collections import defaultdict

H = "H"  # horizontal
V = "V"  # vertical

placed = []  # lista de dicts: {word, clue, orient, row, col}
grid = {}    # (r, c) -> char  (letras)
letters_positions = defaultdict(list)  # char -> [(r,c), ...]

def can_place(word, r, c, orient):
    # Verifica si puede colocarse la palabra en (r,c) con orientación dada, sin conflictos de letras
    for i, ch in enumerate(word):
        rr = r + (i if orient == V else 0)
        cc = c + (i if orient == H else 0)
        # Si ya hay letra, debe coincidir
        if (rr, cc) in grid and grid[(rr, cc)] != ch:
            return False
    return True

def place_word(word, clue, r, c, orient):
    placed.append({"word": word, "clue": clue, "orient": orient, "row": r, "col": c})
    for i, ch in enumerate(word):
        rr = r + (i if orient == V else 0)
        cc = c + (i if orient == H else 0)
        grid[(rr, cc)] = ch
        letters_positions[ch].append((rr, cc))

def try_place_with_cross(word, clue):
    # Intenta cruzar con cualquier letra ya en la grilla
    for i, ch in enumerate(word):
        for (rr, cc) in letters_positions.get(ch, []):
            # Si allí hay horizontal, ponemos vertical y viceversa
            for orient in (H, V):
                # cruzar perpendicularmente preferido
                orient_try = V if orient == H else H
                r0 = rr - (i if orient_try == V else 0)
                c0 = cc - (i if orient_try == H else 0)
                if can_place(word, r0, c0, orient_try):
                    place_word(word, clue, r0, c0, orient_try)
                    return True
    return False

def naive_place(word, clue):
    # Coloca horizontalmente la palabra en la primera fila libre grande
    # Busca hueco simple sin conflicto
    base_r = 0
    if grid:
        # ponla cerca de la fila máxima existente para no crecer infinito
        base_r = max(r for r, _ in grid.keys()) + 2
    for r in range(base_r, base_r + 50):
        for c in range(-len(word)-5, len(word)+30):
            if can_place(word, r, c, H):
                place_word(word, clue, r, c, H)
                return True
    return False

# Coloca la primera palabra centrada horizontal
first_q, first_w = WORDS[0]
place_word(first_w, first_q, 0, 0, H)

for q, w in WORDS[1:]:
    if not try_place_with_cross(w, q):
        if not naive_place(w, q):
            st.error(f"No pude colocar la palabra '{w}'. Intenta cambiar el orden o palabras.")
            st.stop()

# Compacta a una grilla con offset mínimo
min_r = min(r for r, _ in grid)
max_r = max(r for r, _ in grid)
min_c = min(c for _, c in grid)
max_c = max(c for _, c in grid)
ROWS = max_r - min_r + 1
COLS = max_c - min_c + 1

# Map de letras esperadas
solution = {}
for (r, c), ch in grid.items():
    solution[(r - min_r, c - min_c)] = ch

# ===================================================================================
# 4) Numeración de pistas (across / down) + matriz para inputs
# ===================================================================================
def is_letter(r, c):
    return (r, c) in solution

def starts_across(r, c):
    if not is_letter(r, c): return False
    if c > 0 and is_letter(r, c - 1): return False
    if c + 1 < COLS and is_letter(r, c + 1): return True
    return False

def starts_down(r, c):
    if not is_letter(r, c): return False
    if r > 0 and is_letter(r - 1, c): return False
    if r + 1 < ROWS and is_letter(r + 1, c): return True
    return False

num_map = {}   # (r,c) -> number if inicia palabra
across_list = []
down_list = []
counter = 1

# Para relacionar pista con palabra, generamos strings de cada inicio
def collect_word(r, c, orient):
    s = []
    rr, cc = r, c
    while rr < ROWS and cc < COLS and is_letter(rr, cc):
        s.append(solution[(rr, cc)])
        if orient == H:
            cc += 1
            if cc >= COLS or not is_letter(rr, cc): break
        else:
            rr += 1
            if rr >= ROWS or not is_letter(rr, cc): break
    return "".join(s)

for r in range(ROWS):
    for c in range(COLS):
        started = False
        if starts_across(r, c):
            w = collect_word(r, c, H)
            across_list.append((counter, w))
            num_map[(r, c)] = counter
            counter += 1
            started = True
        if starts_down(r, c):
            w = collect_word(r, c, V)
            # si no se numeró ya como across en la misma celda, numera igual nuevo
            if not started:
                num_map[(r, c)] = counter
                counter += 1
            # el número es el que haya quedado en num_map
            down_list.append((num_map[(r, c)], w))

# ===================================================================================
# 5) Estado de usuario y entradas (solo minúscula sin tildes; 1 letra por celda)
# ===================================================================================
def sanitize_cell(s: str) -> str:
    s = s.lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = "".join(ch for ch in s if "a" <= ch <= "z")
    return s[:1]  # solo 1 char

# matriz de entradas
if "cw_inputs" not in st.session_state or \
   st.session_state.get("cw_shape") != (ROWS, COLS):
    st.session_state.cw_inputs = {k: "" for k in solution.keys()}
    st.session_state.cw_shape = (ROWS, COLS)
    st.session_state.crossword_solved = False

# ===================================================================================
# 6) UI: grilla a la izquierda, pistas a la derecha
# ===================================================================================
left, right = st.columns([3, 2], gap="large")

with left:
    st.subheader("Completa el crucigrama")
    st.write("_Escribe solo minúsculas y sin tildes. Una letra por casilla._")

    # Dibuja grilla fila por fila
    for r in range(ROWS):
        cols = st.columns(COLS, gap="small")
        for c in range(COLS):
            with cols[c]:
                if is_letter(r, c):
                    # etiqueta pequeñita con número si inicia palabra
                    if (r, c) in num_map:
                        st.markdown(f"<div style='font-size:11px;opacity:.7;margin-bottom:-8px'>{num_map[(r,c)]}</div>", unsafe_allow_html=True)

                    key = f"cw_{r}_{c}"
                    default_val = st.session_state.cw_inputs.get((r, c), "")
                    val = st.text_input(
                        label=" ",  # sin texto visible
                        key=key,
                        value=default_val,
                        max_chars=1,
                        label_visibility="collapsed",
                    )
                    val = sanitize_cell(val)
                    if val != st.session_state.cw_inputs.get((r, c), ""):
                        st.session_state.cw_inputs[(r, c)] = val
                else:
                    # Celda bloqueada (negra)
                    st.markdown(
                        "<div style='width:100%; aspect-ratio:1/1; background:#111; border-radius:6px;'></div>",
                        unsafe_allow_html=True
                    )

    st.write("")
    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        if st.button("✅ Validar"):
            total = len(solution)
            correct = sum(1 for pos, ch in solution.items() if st.session_state.cw_inputs.get(pos, "") == ch)
            if correct == total:
                st.session_state.crossword_solved = True
                st.success("🎉 ¡Crucigrama completado!")
            else:
                st.warning(f"Letras correctas: {correct}/{total}. Sigue intentando.")
    with c2:
        if st.button("🗑️ Borrar entradas"):
            for k in list(st.session_state.cw_inputs.keys()):
                st.session_state.cw_inputs[k] = ""
            st.session_state.crossword_solved = False
            st.rerun()
    with c3:
        if st.button("⬅️ Volver a Contenido"):
            try: st.switch_page("pages/2_Contenido.py")
            except Exception: st.rerun()

with right:
    st.subheader("Pistas")
    st.markdown("**Horizontales**")
    for num, w in across_list:
        # intenta encontrar la clue original que tenga esa palabra
        # (como el generador es simple, usamos la primera coincidencia)
        clue_text = next((q for q, ww in WORDS if ww == w), "(sin texto)")
        st.markdown(f"**{num}.** {clue_text}")

    st.markdown("---")
    st.markdown("**Verticales**")
    for num, w in down_list:
        clue_text = next((q for q, ww in WORDS if ww == w), "(sin texto)")
        st.markdown(f"**{num}.** {clue_text}")

# Si lo deseas, puedes desbloquear más cuadros al completar el crucigrama:
# if st.session_state.crossword_solved:
#     st.session_state.cuadro2_solved = True
