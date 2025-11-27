import tkinter as tk
import random
import time

#
GAME_DURATION = 300
CIRCLE_LIFETIME = 700
CIRCLE_RADIUS = 40

MASCOT_INTERVAL = 10000
MASCOT_DISPLAY_MS = 4500
MASCOT_STEP_MS = 18
MASCOT_STEP_PX = 24


COLORS = {
    "root_bg":"#FFAFD7",
    "title_fg": "#7C184A",
    "top_text_fg": "#7C184A",
    "button_bg": "#7C184A",
    "button_fg": "#FFFFFF",
    "button_active_bg": "#FF7AC2",
    "canvas_bg": "#000000",
    "circle_fill": "#FF4FA8",
    "circle_outline": "#FFFFFF",
    "shadow_text": "#170414",
}

# frases rosadas/fucsia
FRASES = [
    "¡Tú puedes!",
    "¡Genial!",
    "¡Sigue así!",
    "¡Increíble!",
    "¡Buen combo!"
]


NEON_COLORS = ["#FF4FA8", "#FF7AC2", "#FFC1E3", "#FF8CD1", "#FF5FB8"]

# ---------- ESTADO ----------
ultimo_circle_id = None
juego_activo = False
puntuacion = 0
fallos = 0
combo = 0
inicio = 0
tiempo_restante = GAME_DURATION

# ---------- FUNCIONES DEL JUEGO ----------
def iniciar_juego():
    global puntuacion, fallos, combo, inicio, tiempo_restante, juego_activo
    puntuacion = 0
    fallos = 0
    combo = 0
    inicio = time.time()
    tiempo_restante = GAME_DURATION
    juego_activo = True

    boton_inicio.config(state="disabled")
    label_puntuacion.config(text="Puntuación: 0")
    label_tiempo.config(text=f"Tiempo: {GAME_DURATION}")

    panel_fin.pack_forget()
    actualizar_tiempo()
    spawn_circle()

    root.after(MASCOT_INTERVAL, mascot_loop)


def spawn_circle():
    global ultimo_circle_id
    if not juego_activo:
        return

    canvas.delete("circle")
    x = random.randint(CIRCLE_RADIUS, CANVAS_W - CIRCLE_RADIUS)
    y = random.randint(CIRCLE_RADIUS, CANVAS_H - CIRCLE_RADIUS)

    circle = canvas.create_oval(
        x - CIRCLE_RADIUS, y - CIRCLE_RADIUS,
        x + CIRCLE_RADIUS, y + CIRCLE_RADIUS,
        fill=COLORS["circle_fill"], outline=COLORS["circle_outline"], width=3, tags="circle"
    )

    ultimo_circle_id = circle
    canvas.tag_bind(circle, "<Button-1>", hit_circle)

    root.after(CIRCLE_LIFETIME, lambda cid=circle: remover_circle(cid))


def hit_circle(event):
    global puntuacion, ultimo_circle_id, combo
    if not juego_activo:
        return

    combo += 1
    puntuacion += 1 + combo

    label_puntuacion.config(text=f"Puntuación: {puntuacion}")

    show_combo_text()

    if ultimo_circle_id is not None:
        try:
            canvas.delete(ultimo_circle_id)
        except:
            pass
        ultimo_circle_id = None

    spawn_circle()


def remover_circle(circle_id):
    global fallos, ultimo_circle_id, combo
    if not juego_activo:
        return

    if circle_id == ultimo_circle_id:
        fallos += 1
        combo = 0
        try:
            canvas.delete(circle_id)
        except:
            pass
        ultimo_circle_id = None
        spawn_circle()


def actualizar_tiempo():
    global tiempo_restante, juego_activo
    tiempo_restante = GAME_DURATION - int(time.time() - inicio)

    if tiempo_restante <= 0:
        juego_activo = False
        label_tiempo.config(text="Tiempo: 0")
        canvas.delete("circle")
        fin_del_juego()
        return

    label_tiempo.config(text=f"Tiempo: {tiempo_restante}")
    root.after(1000, actualizar_tiempo)


def obtener_rango(score, misses):
    if score == 0:
        return "D"
    precision = score / (score + misses)
    if precision >= 0.90:
        return "S"
    if precision >= 0.75:
        return "A"
    if precision >= 0.60:
        return "B"
    if precision >= 0.40:
        return "C"
    return "D"


def fin_del_juego():
    rango = obtener_rango(puntuacion, fallos)
    panel_fin_label.config(
        text=f"Puntuación: {puntuacion}\nFallos: {fallos}\nRango: {rango}"
    )
    panel_fin.pack(pady=12)
    boton_inicio.config(state="normal")


# ---------- TEXTO MOTIVACIONAL ----------
def show_message_in_canvas():
    if not juego_activo:
        return

    frase = random.choice(FRASES)
    x = random.randint(80, CANVAS_W - 80)
    y = random.randint(60, CANVAS_H - 60)

    tag = f"msg_{int(time.time()*1000)}"
    shadow_tag = tag + "_s"

    canvas.create_text(
        x+2, y+2, text=frase, fill=COLORS["shadow_text"],
        font=("Arial", 22, "bold"), tags=shadow_tag
    )

    color = random.choice(NEON_COLORS)
    canvas.create_text(
        x, y, text=frase, fill=color,
        font=("Arial", 22, "bold"), tags=tag
    )

    root.after(1500, lambda: (canvas.delete(tag), canvas.delete(shadow_tag)))


# ---------- COMBO ANIMACIÓN TIPO OSU ----------
def show_combo_text():
    if combo <= 1:
        return

    x = CANVAS_W // 2
    y = 60

    tag = f"combo_{int(time.time()*1000)}"
    shadow_tag = tag + "_s"

    # Texto inicial
    color = random.choice(NEON_COLORS)
    base_font = ("Arial Black", 26)
    canvas.create_text(
        x+2, y+2, text=f"COMBO x{combo}", fill=COLORS["shadow_text"],
        font=base_font, tags=shadow_tag
    )
    canvas.create_text(
        x, y, text=f"COMBO x{combo}", fill=color,
        font=base_font, tags=tag
    )

    # Efecto "burst" circular
    burst_tag = tag + "_b"
    r0 = 10
    canvas.create_oval(
        x - r0, y - r0, x + r0, y + r0,
        outline=color, width=3, tags=burst_tag
    )

    steps = 18          # durará ~ 18 * 30ms ≈ 540ms
    dt = 30
    max_font = 44       # tamaño máximo "pop"
    min_font = 26       # tamaño base
    up_steps = 9        # fase de crecimiento
    down_steps = steps - up_steps

    colors_cycle = NEON_COLORS[:]

    def animate(i, current_color):
        # actualizar color cíclico para el glow
        if i % 3 == 0:
            current_color = colors_cycle[i % len(colors_cycle)]

        # progresión de tamaño tipo ease-out / ease-in simple
        if i <= up_steps:
            size = int(min_font + (max_font - min_font) * (i / up_steps))
            y_offset = -int(8 * (i / up_steps))  # pequeño empuje hacia arriba
        else:
            t = i - up_steps
            size = int(max_font - (max_font - min_font) * (t / down_steps))
            y_offset = -int(8 * (1 - (t / down_steps)))

        # actualizar texto y sombra
        canvas.itemconfigure(tag, font=("Arial Black", size), fill=current_color)
        canvas.coords(tag, x, y + y_offset)
        canvas.itemconfigure(shadow_tag, font=("Arial Black", size))
        canvas.coords(shadow_tag, x + 2, y + y_offset + 2)

        # actualizar burst (círculo que se expande y se atenúa)
        r = r0 + i * 5
        canvas.coords(burst_tag, x - r, y - r, x + r, y + r)
        # simular desvanecimiento con grosor decreciente
        w = max(1, 3 - i // 6)
        canvas.itemconfigure(burst_tag, outline=current_color, width=w)

        if i < steps:
            root.after(dt, lambda: animate(i + 1, current_color))
        else:
            # limpiar elementos
            canvas.delete(tag)
            canvas.delete(shadow_tag)
            canvas.delete(burst_tag)

    animate(0, color)


# ---------- MASCOTA ----------
PIXEL_GRID = [
    [None, "#ffdce6", "#ffdce6", "#ffdce6", "#ffdce6", "#ffdce6", "#ffdce6", None],
    ["#ffc4dd", "#ffdce6", "#ffdce6", "#ffdce6", "#ffdce6", "#ffdce6", "#ffdce6", "#ffc4dd"],
    ["#ffc4dd", "#ffe6f2", "#ffe6f2", "#ffe6f2", "#ffe6f2", "#ffe6f2", "#ffe6f2", "#ffc4dd"],
    [None, "#ffe6f2", "#001a33", "#ffe6f2", "#ffe6f2", "#001a33", "#ffe6f2", None],
    [None, "#ffe6f2", "#001a33", "#ffe6f2", "#ffe6f2", "#001a33", "#ffe6f2", None],
    [None, "#ffe6f2", "#ff9fb0", "#ffe6f2", "#ffe6f2", "#ff9fb0", "#ffe6f2", None],
    [None, None, "#ffe6f2", "#ffe6f2", "#ffe6f2", "#ffe6f2", None, None],
    [None, "#ffd7e8", "#ffd7e8", "#ffd7e8", "#ffd7e8", "#ffd7e8", "#ffd7e8", None],
    [None, "#ffd7e8", "#ffd7e8", "#ffd7e8", "#ffd7e8", "#ffd7e8", "#ffd7e8", None],
]

PIXEL_SIZE = 10
SCALE = 2

mascot_animating = False


def draw_pixel_mascot(canvas_obj):
    canvas_obj.delete("all")
    for r in range(len(PIXEL_GRID)):
        for c in range(len(PIXEL_GRID[0])):
            col = PIXEL_GRID[r][c]
            if col:
                x1 = c * PIXEL_SIZE * SCALE
                y1 = r * PIXEL_SIZE * SCALE
                x2 = x1 + PIXEL_SIZE * SCALE
                y2 = y1 + PIXEL_SIZE * SCALE
                canvas_obj.create_rectangle(
                    x1, y1, x2, y2, fill=col, outline=col
                )


def mascot_loop():
    if not juego_activo:
        return
    show_mascot()
    show_message_in_canvas()
    root.after(MASCOT_INTERVAL, mascot_loop)


def show_mascot():
    global mascot_animating
    if mascot_animating or not juego_activo:
        return

    mascot_animating = True
    draw_pixel_mascot(mascot_canvas)

    start_x = ROOT_W + 40
    dest_x = LEFT_MARGIN + CANVAS_W + 20
    mascot_frame.place(x=start_x, y=TOP_BAR_H + 20)

    def step_in(x):
        if x <= dest_x:
            mascot_frame.place(x=dest_x, y=TOP_BAR_H + 20)
            root.after(MASCOT_DISPLAY_MS, lambda: step_out(dest_x))
            return
        mascot_frame.place(x=x, y=TOP_BAR_H + 20)
        root.after(MASCOT_STEP_MS, lambda: step_in(x - MASCOT_STEP_PX))

    def step_out(x):
        global mascot_animating
        end_x = ROOT_W + 60
        if x >= end_x:
            mascot_frame.place_forget()
            mascot_animating = False
            return
        mascot_frame.place(x=x + MASCOT_STEP_PX, y=TOP_BAR_H + 20)
        root.after(MASCOT_STEP_MS, lambda: step_out(x + MASCOT_STEP_PX))

    step_in(start_x)


# ---------- INTERFAZ ----------
ROOT_W = 980
ROOT_H = 700
CANVAS_W = 600
CANVAS_H = 520
TOP_BAR_H = 140
LEFT_MARGIN = 80

root = tk.Tk()
root.title("Mini OSU - Arcade Pink")
root.geometry(f"{ROOT_W}x{ROOT_H}")
root.configure(bg=COLORS["root_bg"])

top_frame = tk.Frame(root, bg=COLORS["root_bg"], height=TOP_BAR_H)
top_frame.pack(side="top", fill="x")

title_label = tk.Label(
    top_frame, text="MINI OSU",
    font=("Arial Black", 36), fg=COLORS["title_fg"], bg=COLORS["root_bg"]
)
title_label.pack(pady=(12, 5))

controls_frame = tk.Frame(top_frame, bg=COLORS["root_bg"])
controls_frame.pack()

label_tiempo = tk.Label(
    controls_frame, text=f"Tiempo: {GAME_DURATION}",
    font=("Arial Black", 30), fg=COLORS["top_text_fg"], bg=COLORS["root_bg"]
)
label_tiempo.grid(row=0, column=0, padx=24)

label_puntuacion = tk.Label(
    controls_frame, text="Puntuación: 0",
    font=("Arial Black", 30), fg=COLORS["top_text_fg"], bg=COLORS["root_bg"]
)
label_puntuacion.grid(row=0, column=1, padx=24)

boton_inicio = tk.Button(
    controls_frame, text="Iniciar juego",
    font=("Arial", 16, "bold"),
    bg=COLORS["button_bg"], fg=COLORS["button_fg"], activebackground=COLORS["button_active_bg"],
    command=iniciar_juego
)
boton_inicio.grid(row=0, column=2, padx=16)

main_frame = tk.Frame(root, bg=COLORS["root_bg"])
main_frame.pack(fill="both", expand=False, pady=(10, 0))

canvas = tk.Canvas(
    main_frame, width=CANVAS_W, height=CANVAS_H,
    bg=COLORS["canvas_bg"], highlightthickness=0
)
canvas.pack(side="left", padx=(LEFT_MARGIN, 20), pady=10)

mascot_frame = tk.Frame(main_frame, width=200, height=260, bg=COLORS["root_bg"])
mascot_canvas = tk.Canvas(
    mascot_frame,
    width=len(PIXEL_GRID[0]) * PIXEL_SIZE * SCALE,
    height=len(PIXEL_GRID) * PIXEL_SIZE * SCALE,
    bg=COLORS["root_bg"], highlightthickness=0
)
mascot_canvas.pack(padx=10, pady=10)

panel_fin = tk.Frame(root, bg=COLORS["root_bg"])
panel_fin_label = tk.Label(
    panel_fin, text="", font=("Arial", 20),
    fg=COLORS["top_text_fg"], bg=COLORS["root_bg"]
)
panel_fin_label.pack()

root.mainloop()