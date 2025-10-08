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
# 1) PISTAS (7 horizontales y 7 verticales) — en el orden que diste
#    Primeras 7 -> horizontales, últimas 7 -> verticales
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

def normalize_answer(s: str) -> str:
    s = s.lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")  # sin acentos
    s = "".join(ch for ch in s if "a" <= ch <= "z")  # solo letras
    return s

WORDS_ALL = [(q, normalize_answer(a)) for q, a in CLUES]
for q, w in WORDS_ALL:
    if not w:
        st.error(f"La respuesta de la pista '{q}' quedó vacía tras normalizar. Revísala.")
        st.stop()

ACROSS = WORDS_ALL[:7]   # 7 horizontales
DOWN   = WORDS_ALL[7:]   # 7 verticales

# ===================================================================================
# 2) Generador de crucigrama con separación (no se pegan palabras)
#    Reglas:
#    - Las horizontales se colocan en filas distintas (con huecos antes/después).
#    - Las verticales deben cruzar alguna horizontal (preferido) y no crear adyacencias horizontales
#      fuera del cruce. También dejamos celda libre antes y después de cada palabra.
# ===================================================================================
H, V = "H", "V"
grid = {}                       # (r,c) -> letra
letters_positions = defaultdict(list)  # ch -> [(r,c)]
placed = []                     # {word, clue, orient, row, col}

def occ(r,c): return (r,c) in grid

def can_place(word, r, c, orient):
    L = len(word)
    for i, ch in enumerate(word):
        rr = r + (i if orient == V else 0)
        cc = c + (i if orient == H else 0)
        if occ(rr, cc) and grid[(rr, cc)] != ch:
            return False
        # Para evitar pegado, si esta celda sería nueva (no existe aún),
        # no puede tener vecinos laterales formando palabra horizontal accidental.
        if not occ(rr, cc):
            if occ(rr, cc-1) or occ(rr, cc+1):
                # salvo que esos vecinos pertenezcan al cruce exacto (misma letra),
                # lo bloqueamos para no crear "palabras pegadas".
                # Aquí simplificamos: si hay vecino, no permitimos (evita "sin texto").
                return False
    # Celda anterior y posterior (antes/después de la palabra) deben estar vacías
    before = (r, c-1) if orient == H else (r-1, c)
    after  = (r, c+L) if orient == H else (r+L, c)
    if occ(*before) or occ(*after):
        return False
    return True

def place_word(word, clue, r, c, orient):
    placed.append({"word": word, "clue": clue, "orient": orient, "row": r, "col": c})
    for i, ch in enumerate(word):
        rr = r + (i if orient == V else 0)
        cc = c + (i if orient == H else 0)
        grid[(rr, cc)] = ch
        letters_positions[ch].append((rr, cc))

def place_across_rows():
    # Colocamos cada ACROSS en una fila distinta, con un pequeño offset alterno
    row = 0
    offset = 0
    for clue, w in ACROSS:
        # buscamos una columna donde quepa con separación
        placed_ok = False
        for col in range(offset, offset + 60):  # margen amplio
            if can_place(w, row, col, H):
                place_word(w, clue, row, col, H)
                placed_ok = True
                break
        if not placed_ok:
            st.error(f"No pude colocar la horizontal '{w}'.")
            st.stop()
        row += 2           # deja una fila vacía entre horizontales
        offset = (offset + 3) % 10  # mueve ligeramente el inicio
    return

def place_down_words():
    for clue, w in DOWN:
        placed_ok = False
        # intenta cruzar con cualquier letra existente
        for i, ch in enumerate(w):
            for (rr, cc) in letters_positions.get(ch, []):
                r0 = rr - i
                c0 = cc
                if can_place(w, r0, c0, V):
                    place_word(w, clue, r0, c0, V)
                    placed_ok = True
                    break
            if placed_ok: break
        if not placed_ok:
            # Si no logra cruzar, intenta ponerla en una columna libre sin adyacencias
            # (aún así serán 7 V, pero quizá con menos cruces).
            for col in range(-20, 40):
                for row in range(-20, 40):
                    if can_place(w, row, col, V):
                        place_word(w, clue, row, col, V)
                        placed_ok = True
                        break
                if placed_ok: break
        if not placed_ok:
            st.error(f"No pude colocar la vertical '{w}'.")
            st.stop()

# Ejecuta la colocación
place_across_rows()
place_down_words()

# Compacta a bounding box
min_r = min(r for r, _ in grid.keys())
max_r = max(r for r, _ in grid.keys())
min_c = min(c for _, c in grid.keys())
max_c = max(c for _, c in grid.keys())
ROWS = max_r - min_r + 1
COLS = max_c - min_c + 1

solution = {(r - min_r, c - min_c): ch for (r, c), ch in grid.items()}

# ===================================================================================
# 3) Numeración de "across" y "down" desde la grilla final
# ===================================================================================
def is_letter(r, c): return (r, c) in solution

def starts_across(r, c):
    if not is_letter(r, c): return False
    if c > 0 and is_letter(r, c-1): return False
    if c+1 < COLS and is_letter(r, c+1): return True
    return False

def starts_down(r, c):
    if not is_letter(r, c): return False
    if r > 0 and is_letter(r-1, c): return False
    if r+1 < ROWS and is_letter(r+1, c): return True
    return False

def collect_word(r, c, orient):
    s = []
    rr, cc = r, c
    while 0 <= rr < ROWS and 0 <= cc < COLS and is_letter(rr, cc):
        s.append(solution[(rr, cc)])
        if orient == "H":
            if cc+1 >= COLS or not is_letter(rr, cc+1): break
            cc += 1
        else:
            if rr+1 >= ROWS or not is_letter(rr+1, cc): break
            rr += 1
    return "".join(s)

num_map = {}
across_list = []
down_list = []
counter = 1

for r in range(ROWS):
    for c in range(COLS):
        started = False
        if starts_across(r, c):
            w = collect_word(r, c, "H")
            across_list.append((counter, w))
            num_map[(r, c)] = counter
            counter += 1
            started = True
        if starts_down(r, c):
            w = collect_word(r, c, "V")
            if not started:
                num_map[(r, c)] = counter
                counter += 1
            down_list.append((num_map[(r, c)], w))

# Mapas palabra->pista (para mostrar texto correcto)
ACROSS_WORD_TO_CLUE = {normalize_answer(ans): q for q, ans in ACROSS}
DOWN_WORD_TO_CLUE   = {normalize_answer(ans): q for q, ans in DOWN}

# ===================================================================================
# 4) Entradas del usuario (solo minúscula sin tildes)
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
# 5) UI: grilla (izquierda) + pistas (derecha)  ⟵ REEMPLAZA DESDE AQUÍ
# ===================================================================================
left, right = st.columns([3, 2], gap="large")

with left:
    st.subheader("Completa el crucigrama")
    st.write("_Escribe solo minúsculas y sin tildes. Una letra por casilla._")

    # ====== Estilos para que las casillas se vean grandes y la letra centrada ======
    st.markdown("""
    <style>
    /* Contenedor para limitar el alcance del estilo */
    #cwgrid [data-testid="stTextInput"] > div > input {
        width: 48px;              /* ancho de la casilla */
        height: 48px;             /* alto de la casilla (cuadrada) */
        padding: 0 !important;
        text-align: center;
        font-weight: 800;
        font-size: 24px;          /* tamaño de la letra */
        line-height: 48px;
        background-color: #ffffff !important;
        color: #111 !important;
        border: 1px solid rgba(0,0,0,.25) !important;
        border-radius: 8px !important;
    }
    #cwgrid .blocked {
        width: 48px; height: 48px;
        background:#111; border-radius:8px;
    }
    #cwgrid .cellnum {
        font-size:11px; opacity:.7; margin-bottom:-6px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div id='cwgrid'>", unsafe_allow_html=True)

    for r in range(ROWS):
        cols = st.columns(COLS, gap="small")
        for c in range(COLS):
            with cols[c]:
                if (r, c) in solution:
                    # numerito si inicia palabra
                    if (r, c) in num_map:
                        st.markdown(f"<div class='cellnum'>{num_map[(r,c)]}</div>", unsafe_allow_html=True)

                    key = f"cw_{r}_{c}"

                    # 1) valor actual del widget (o vacío si primera vez)
                    cur_val = st.session_state.get(key, "")
                    # 2) pintamos el widget (no pasamos 'value' fijo para no bloquear su estado)
                    _ = st.text_input(" ", key=key, max_chars=1, label_visibility="collapsed")

                    # 3) saneamos y reflejamos de vuelta en el widget si cambió
                    new_val = "".join(
                        ch for ch in unicodedata.normalize("NFD", st.session_state.get(key, "").lower())
                        if "a" <= ch <= "z"
                    )[:1]
                    if new_val != st.session_state.get(key, ""):
                        st.session_state[key] = new_val

                    # 4) guardamos también en nuestra matriz de solución del usuario
                    st.session_state.cw_inputs[(r, c)] = st.session_state.get(key, "")
                else:
                    st.markdown("<div class='blocked'></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    # ===== Botonera: validar | limpiar | volver
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
                st.warning(f"Letras correctas: {correct}/{total}. Sigue intentando.")
    with c2:
        if st.button("🗑️ Borrar entradas"):
            # limpia tanto nuestro buffer como los widgets
            for k in list(st.session_state.cw_inputs.keys()):
                st.session_state.cw_inputs[k] = ""
            for r in range(ROWS):
                for c in range(COLS):
                    key = f"cw_{r}_{c}"
                    if key in st.session_state:
                        st.session_state[key] = ""
            st.session_state.crossword_solved = False
            st.rerun()
    with c3:
        if st.button("⬅️ Volver a Contenido"):
            try: st.switch_page("pages/2_Contenido.py")
            except Exception: st.rerun()

    # Siguiente cuadro (solo si está resuelto)
    disabled_next = not st.session_state.get("crossword_solved", False)
    if st.button("➡️ Siguiente cuadro", disabled=disabled_next):
        try:
            st.switch_page("pages/5_Cuadro3.py")
        except Exception:
            st.rerun()

with right:
    st.subheader("Pistas")
    st.markdown("**Horizontales (7)**")
    for num, w in across_list:
        clue_text = ACROSS_WORD_TO_CLUE.get(w, "(sin texto)")
        st.markdown(f"**{num}.** {clue_text}")

    st.markdown("---")
    st.markdown("**Verticales (7)**")
    for num, w in down_list:
        clue_text = DOWN_WORD_TO_CLUE.get(w, "(sin texto)")
        st.markdown(f"**{num}.** {clue_text}")
