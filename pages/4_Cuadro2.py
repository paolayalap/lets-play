import streamlit as st
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import defaultdict

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
# 1) PISTAS (7 horizontales y 7 verticales) — tal como pediste
# ===================================================================================
CLUES = [
    ("Cada fin de mes es el...", "buffetaco"),
    ("La mezcla de nuestros colores favoritos es el color...", "morado"),
    ("Desde siempre te ha gustado un juego de nintendo llamado", "metroid"),
    ("Tu dices rana y yo...", "salto"),
    ("Los tacos son ricos, pero no más que...", "tu"),
    ("Cuando viajemos a Alemania fijo hay que ir por una...", "chela"),
    ("Debemos encontrar la receta del... de &café", "blackfrost"),
    ("Si por nosotros fuera, ya estuvieramos...", "casados"),
    ("Este juego tiene varias adaptaciones como: la puerta del infierno y aniquilación", "doom"),
    ("En las noches o en tiempo libres se juega...para repartir democracia", "helldivers"),
    ("...es un sanguinario señor de la guerra proveninente de tiempos olvidados al que los siglos han visto nacer en tres ocasiones y morir en otras dos", "mordekaiser"),
    ("No hay mejor escudería en fórmula 1 que...", "mclaren"),
    ("Es como un mundo donde construímos nuestra casa, nuestro huerto y luchamos contra monstruos", "minecraft"),
    ("Es el comandante supremo de los Autobots en su lucha contra los Decepticons", "optimusprime"),
]

# ===================================================================================
# 2) Normalización: a minúscula, sin tildes, solo letras [a-z]
# ===================================================================================
def normalize_answer(s: str) -> str:
    s = s.lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")  # quita acentos
    s = "".join(ch for ch in s if "a" <= ch <= "z")  # solo letras
    return s

WORDS = [(q, normalize_answer(a)) for q, a in CLUES]
for q, w in WORDS:
    if not w:
        st.error(f"La respuesta de la pista '{q}' quedó vacía tras normalizar. Revísala.")
        st.stop()

# ===================================================================================
# 3) Construcción del crucigrama forzando 7 H y 7 V (colocación greedy con cruces)
# ===================================================================================
H, V = "H", "V"
placed = []                     # {word, clue, orient, row, col}
grid = {}                       # (r, c) -> char
letters_positions = defaultdict(list)  # char -> [(r,c), ...]

def can_place(word, r, c, orient):
    for i, ch in enumerate(word):
        rr = r + (i if orient == V else 0)
        cc = c + (i if orient == H else 0)
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

def try_place_with_cross(word, clue, desired_orient):
    # Cruces SOLO en desired_orient
    for i, ch in enumerate(word):
        for (rr, cc) in letters_positions.get(ch, []):
            r0 = rr - (i if desired_orient == V else 0)
            c0 = cc - (i if desired_orient == H else 0)
            if can_place(word, r0, c0, desired_orient):
                place_word(word, clue, r0, c0, desired_orient)
                return True
    return False

def naive_place(word, clue, desired_orient):
    # Busca un hueco razonable para colocar en la orientación deseada
    if not grid:
        base_r = 0
    else:
        base_r = min(r for r, _ in grid) - 10
    for r in range(base_r, base_r + 120):
        for c in range(-len(word) - 30, 120):
            if can_place(word, r, c, desired_orient):
                place_word(word, clue, r, c, desired_orient)
                return True
    return False

# Coloca la primera palabra horizontal como ancla
q0, w0 = WORDS[0]
place_word(w0, q0, 0, 0, H)

# Siguientes 6 palabras como horizontales, y las 7 restantes verticales
h_words = WORDS[1:7]    # 6 más (total 7 H)
v_words = WORDS[7:]     # 7 V

for q, w in h_words:
    if not try_place_with_cross(w, q, H):
        if not naive_place(w, q, H):
            st.error(f"No pude colocar la palabra (H) '{w}'.")
            st.stop()

for q, w in v_words:
    if not try_place_with_cross(w, q, V):
        if not naive_place(w, q, V):
            st.error(f"No pude colocar la palabra (V) '{w}'.")
            st.stop()

# Compacta a una grilla rectangular
min_r = min(r for r, _ in grid)
max_r = max(r for r, _ in grid)
min_c = min(c for _, c in grid)
max_c = max(c for _, c in grid)
ROWS = max_r - min_r + 1
COLS = max_c - min_c + 1

solution = {}
for (r, c), ch in grid.items():
    solution[(r - min_r, c - min_c)] = ch

# ===================================================================================
# 4) Numeración de palabras Across/Down a partir de la grilla final
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

def collect_word(r, c, orient):
    s = []
    rr, cc = r, c
    while 0 <= rr < ROWS and 0 <= cc < COLS and is_letter(rr, cc):
        s.append(solution[(rr, cc)])
        if orient == H:
            if cc + 1 >= COLS or not is_letter(rr, cc + 1): break
            cc += 1
        else:
            if rr + 1 >= ROWS or not is_letter(rr + 1, cc): break
            rr += 1
    return "".join(s)

num_map = {}
across_list = []
down_list = []
counter = 1

for r in range(ROWS):
    for c in range(COLS):
        started_here = False
        if starts_across(r, c):
            w = collect_word(r, c, H)
            across_list.append((counter, w))
            num_map[(r, c)] = counter
            counter += 1
            started_here = True
        if starts_down(r, c):
            w = collect_word(r, c, V)
            if not started_here:
                num_map[(r, c)] = counter
                counter += 1
            down_list.append((num_map[(r, c)], w))

# ===================================================================================
# 5) Estado de usuario y entradas (solo minúscula sin tildes; 1 letra por casilla)
# ===================================================================================
def sanitize_cell(s: str) -> str:
    s = s.lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = "".join(ch for ch in s if "a" <= ch <= "z")
    return s[:1]

if "cw_inputs" not in st.session_state or st.session_state.get("cw_shape") != (ROWS, COLS):
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

    for r in range(ROWS):
        cols = st.columns(COLS, gap="small")
        for c in range(COLS):
            with cols[c]:
                if (r, c) in solution:
                    if (r, c) in num_map:
                        st.markdown(
                            f"<div style='font-size:11px;opacity:.7;margin-bottom:-8px'>{num_map[(r,c)]}</div>",
                            unsafe_allow_html=True
                        )
                    key = f"cw_{r}_{c}"
                    default_val = st.session_state.cw_inputs.get((r, c), "")
                    val = st.text_input(
                        label=" ",
                        key=key,
                        value=default_val,
                        max_chars=1,
                        label_visibility="collapsed",
                    )
                    val = sanitize_cell(val)
                    if val != st.session_state.cw_inputs.get((r, c), ""):
                        st.session_state.cw_inputs[(r, c)] = val
                else:
                    st.markdown(
                        "<div style='width:100%; aspect-ratio:1/1; background:#111; border-radius:6px;'></div>",
                        unsafe_allow_html=True
                    )

    st.write("")
    # ===== Botonera de validación / limpiar / volver =====
    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        if st.button("✅ Validar"):
            total = len(solution)
            correct = sum(1 for pos, ch in solution.items()
                          if st.session_state.cw_inputs.get(pos, "") == ch)
            if correct == total:
                st.session_state.crossword_solved = True
                st.session_state.cuadro2_solved = True      # <- 🔓 habilita Cuadro 3
                st.success("🎉 ¡Crucigrama completado!")
            else:
