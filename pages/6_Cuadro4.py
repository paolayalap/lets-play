import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import random

st.set_page_config(page_title="Cuadro 4 — Mini Pac-Man", page_icon="🎮", layout="wide")

# ====== Guard: login + gating desde Cuadro 3 ======
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Necesitas iniciar sesión para acceder a esta página.")
    try: st.switch_page("app.py")
    except Exception: st.stop()

if not st.session_state.get("cuadro3_solved", False):
    st.error("Debes completar el Cuadro 3 (memoria) antes de jugar este nivel.")
    if st.button("⬅️ Ir al Cuadro 3"):
        try: st.switch_page("pages/5_Cuadro3.py")
        except Exception: st.rerun()
    st.stop()

TZ = ZoneInfo("America/Guatemala")
st.title("🎮 Mini Pac-Man")
st.caption(f"Hora local: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')}")

# =========================
#   Laberinto (9x19)
#   #: muro   .: pellet   o: power pellet   P: jugador   G: fantasma
# =========================
MAZE = [
    "###################",
    "#P........#......o#",
    "#.###.###.#.###.###",
    "#.................#",
    "###.#.#####.#.###.#",
    "#...#...G...#.....#",
    "#.###.#.#.#.#.###.#",
    "#.....# G #.....o.#",
    "###################",
]
ROWS, COLS = len(MAZE), len(MAZE[0])

CELL = 30  # px para cada casilla

# ====== Estado y utilidades ======
def find_positions():
    pellets, powers, walls = set(), set(), set()
    player = None
    ghosts = []
    for r in range(ROWS):
        for c in range(COLS):
            ch = MAZE[r][c]
            if ch == "#": walls.add((r, c))
            elif ch == ".": pellets.add((r, c))
            elif ch == "o": powers.add((r, c))
            elif ch == "P": player = (r, c)
            elif ch == "G": ghosts.append((r, c))
    return player, ghosts, pellets, powers, walls

def init_game():
    p, gs, pe, po, wa = find_positions()
    st.session_state.pm_player = p
    st.session_state.pm_ghosts = [{"pos": g, "home": g, "dir": None} for g in gs]
    st.session_state.pm_pellets = set(pe)
    st.session_state.pm_powers = set(po)
    st.session_state.pm_walls = set(wa)
    st.session_state.pm_score = 0
    st.session_state.pm_lives = 3
    st.session_state.pm_power_timer = 0  # turnos “power”
    st.session_state.pm_game_over = False
    st.session_state.pm_win = False
    st.session_state.pm_moves = 0
    st.session_state.cuadro4_solved = False

if "pm_player" not in st.session_state:
    init_game()

def is_wall(rc): return rc in st.session_state.pm_walls
def in_bounds(r, c): return 0 <= r < ROWS and 0 <= c < COLS
def add(a, b): return (a[0] + b[0], a[1] + b[1])

DIRS = {"up":(-1,0),"down":(1,0),"left":(0,-1),"right":(0,1)}
DIR_KEYS = {"⬆️":"up","⬇️":"down","⬅️":"left","➡️":"right"}

# ====== Lógica de movimiento ======
def step_player(dkey):
    if st.session_state.pm_game_over or st.session_state.pm_win: return
    if dkey not in DIRS: return
    dr, dc = DIRS[dkey]
    r, c = st.session_state.pm_player
    nr, nc = r + dr, c + dc
    if not in_bounds(nr, nc) or is_wall((nr, nc)):
        return  # golpea muro, no se mueve
    st.session_state.pm_player = (nr, nc)
    st.session_state.pm_moves += 1

    # Comer pellet / power
    if (nr, nc) in st.session_state.pm_pellets:
        st.session_state.pm_pellets.remove((nr, nc))
        st.session_state.pm_score += 10
    if (nr, nc) in st.session_state.pm_powers:
        st.session_state.pm_powers.remove((nr, nc))
        st.session_state.pm_score += 50
        st.session_state.pm_power_timer = 15  # turnos en modo “power”

def ghost_options(pos):
    opts = []
    for d in DIRS.values():
        nxt = add(pos, d)
        if in_bounds(*nxt) and not is_wall(nxt):
            opts.append(nxt)
    return opts

def move_ghosts():
    """Fantasmas con movimiento simple:
       - Si power_timer>0 huyen (maximizan distancia Manhattan).
       - Si power_timer==0 persiguen (minimizan distancia).
       - Si no hay mejoría, eligen opción aleatoria válida.
    """
    pr, pc = st.session_state.pm_player
    new_positions = []
    for g in st.session_state.pm_ghosts:
        options = ghost_options(g["pos"])
        if not options:
            new_positions.append(g["pos"])
            continue
        # función objetivo
        def score(cell):
            r, c = cell
            dist = abs(r - pr) + abs(c - pc)
            return -dist if st.session_state.pm_power_timer == 0 else dist
        # mejor opción
        best_val = None
        best = []
        for opt in options:
            val = score(opt)
            if best_val is None or val > best_val:
                best_val = val; best = [opt]
            elif val == best_val:
                best.append(opt)
        new_positions.append(random.choice(best))
    # aplicar
    for i, g in enumerate(st.session_state.pm_ghosts):
        g["pos"] = new_positions[i]

def check_collisions():
    p = st.session_state.pm_player
    eaten = []
    for g in st.session_state.pm_ghosts:
        if g["pos"] == p:
            if st.session_state.pm_power_timer > 0:
                eaten.append(g)  # fantasma comido
                st.session_state.pm_score += 200
            else:
                # Pac-Man pierde vida
                st.session_state.pm_lives -= 1
                if st.session_state.pm_lives <= 0:
                    st.session_state.pm_game_over = True
                respawn()
                return  # turno termina
    # Enviar fantasmas comidos a su “home”
    for g in eaten:
        g["pos"] = g["home"]

def respawn():
    # regresa jugador y fantasmas a su spawn, sin tocar pellets
    p, gs, _, _, _ = find_positions()
    st.session_state.pm_player = p
    for i, g in enumerate(st.session_state.pm_ghosts):
        st.session_state.pm_ghosts[i]["pos"] = st.session_state.pm_ghosts[i]["home"]
    st.session_state.pm_power_timer = 0

def turn(dkey):
    if st.session_state.pm_game_over or st.session_state.pm_win: return
    step_player(dkey)
    # Comer/ganar tras mover jugador
    if not st.session_state.pm_pellets and not st.session_state.pm_powers:
        st.session_state.pm_win = True
        st.session_state.cuadro4_solved = True
        return
    # mover fantasmas y checar colisiones
    move_ghosts()
    check_collisions()
    # decrementar power
    if st.session_state.pm_power_timer > 0:
        st.session_state.pm_power_timer -= 1

# ====== Render del tablero ======
def render_board():
    # CSS
    st.markdown(f"""
    <style>
    .board {{
        display: grid;
        grid-template-columns: repeat({COLS}, {CELL}px);
        grid-auto-rows: {CELL}px;
        gap: 6px;
        user-select: none;
    }}
    .cell {{
        width: {CELL}px; height: {CELL}px; border-radius: 7px;
        display:flex; align-items:center; justify-content:center;
        background: #111;  /* por defecto bloqueada */
    }}
    .floor {{ background: #0b132b; }}
    .wall  {{ background: #1d4ed8; }} /* azul muro */
    .pellet::after {{
        content:''; width:8px; height:8px; border-radius:50%; background:#fef08a;
        box-shadow: 0 0 6px #fde68a;
    }}
    .power::after {{
        content:''; width:14px; height:14px; border-radius:50%; background:#fbbf24;
        box-shadow: 0 0 10px #f59e0b;
    }}
    .pacman {{
        width: 70%; height: 70%; border-radius: 50%; background: #facc15; /* amarillo */
        box-shadow: inset -6px -6px 0 rgba(0,0,0,.12);
    }}
    .ghost {{
        width: 70%; height: 70%; background:#ef4444; border-radius: 16px 16px 6px 6px;
        position:relative; overflow:hidden;
    }}
    .ghost.blue {{ background:#22d3ee; }}
    .fright .ghost {{ filter: hue-rotate(40deg) saturate(0.6) brightness(1.1); }}
    </style>
    """, unsafe_allow_html=True)

    # mapa de celdas base (muro/piso/pellets)
    pellets = st.session_state.pm_pellets
    powers  = st.session_state.pm_powers
    walls   = st.session_state.pm_walls
    P       = st.session_state.pm_player
    Gs      = [g["pos"] for g in st.session_state.pm_ghosts]

    html = ['<div class="board {}">'.format("fright" if st.session_state.pm_power_timer>0 else "")]
    for r in range(ROWS):
        for c in range(COLS):
            pos = (r,c)
            if pos in walls:
                html.append('<div class="cell wall"></div>')
                continue
            classes = ["cell","floor"]
            inner = ""
            if pos == P:
                inner = '<div class="pacman"></div>'
            elif pos in Gs:
                idx = Gs.index(pos)
                gcls = "ghost blue" if idx==1 else "ghost"
                inner = f'<div class="{gcls}"></div>'
            elif pos in pellets:
                classes.append("pellet")
            elif pos in powers:
                classes.append("power")
            html.append(f'<div class="{" ".join(classes)}">{inner}</div>')
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)

# ====== HUD y controles ======
top = st.columns([1,1,1,2])
with top[0]:
    st.metric("Puntaje", st.session_state.pm_score)
with top[1]:
    st.metric("Vidas", st.session_state.pm_lives)
with top[2]:
    st.metric("Power", st.session_state.pm_power_timer)

render_board()

st.write("")
ctrl = st.columns([1,1,1,2])
with ctrl[0]:
    if st.button("🔄 Reiniciar"):
        init_game(); st.rerun()
with ctrl[1]:
    if st.button("⬅️ Volver a Contenido"):
        try: st.switch_page("pages/2_Contenido.py")
        except Exception: st.rerun()

st.write("")
pad = st.columns(3)
with pad[0]:
    st.write("")
    if st.button("⬅️"): turn("left"); st.rerun()
with pad[1]:
    if st.button("⬆️"): turn("up"); st.rerun()
    if st.button("⬇️"): turn("down"); st.rerun()
with pad[2]:
    st.write("")
    if st.button("➡️"): turn("right"); st.rerun()

# Mensajes de estado
if st.session_state.pm_win:
    st.success("🎉 ¡Has comido todos los puntos! Nivel completado.")
    st.session_state.cuadro4_solved = True
elif st.session_state.pm_game_over:
    st.error("💀 Te quedaste sin vidas. ¡Inténtalo de nuevo!")

# ====== 👇 ADICIÓN: mostrar la imagen cuando ya se comieron todos los puntos ======
if st.session_state.pm_win:
    st.image("assets/10.jpeg", use_container_width=True)
