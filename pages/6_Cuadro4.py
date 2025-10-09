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
    dr, d
