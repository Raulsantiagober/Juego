import tkinter as tk
import random
import time


GAME_DURATION = 300


CIRCLE_LIFETIME = 700 


CIRCLE_RADIUS = 40


def iniciar_juego():
    global puntuacion, tiempo_restante, inicio
    puntuacion = 0
    tiempo_restante = GAME_DURATION
    inicio = time.time()

    boton_inicio.pack_forget()
    label_info.pack_forget()

    actualizar_tiempo()
    spawn_circle()


def spawn_circle():
    if tiempo_restante <= 0:
        return

    canvas.delete("circle")

    x = random.randint(CIRCLE_RADIUS, 500 - CIRCLE_RADIUS)
    y = random.randint(CIRCLE_RADIUS, 450 - CIRCLE_RADIUS)

    circle = canvas.create_oval(
        x - CIRCLE_RADIUS, y - CIRCLE_RADIUS,
        x + CIRCLE_RADIUS, y + CIRCLE_RADIUS,
        fill="#ff66aa", outline="white", width=3,
        tags="circle"
    )

    canvas.tag_bind(circle, "<Button-1>", hit_circle)
    root.after(CIRCLE_LIFETIME, lambda: remove_circle(circle))


def hit_circle(event):
    global puntuacion
    puntuacion += 1
    label_puntuacion.config(text=f"Puntuación: {puntuacion}")

    canvas.delete("circle")
    root.after(CIRCLE_LIFETIME, spawn_circle)


def remove_circle(circle_id):
    if canvas.find_withtag("circle"):
        canvas.delete(circle_id)
        spawn_circle()


def actualizar_tiempo():
    global tiempo_restante
    tiempo_restante = GAME_DURATION - int(time.time() - inicio)

    if tiempo_restante <= 0:
        canvas.delete("circle")
        label_tiempo.config(text="Tiempo: 0")
        mostrar_fin()
        return

    label_tiempo.config(text=f"Tiempo: {tiempo_restante}")
    root.after(1000, actualizar_tiempo)


def mostrar_fin():
    fin = tk.Label(root, text="¡FIN DEL JUEGO!", font=("Arial", 26), fg="red", bg="#001a33")
    fin.place(x=150, y=230)





root = tk.Tk()
root.title("Mini OSU - Tkinter")
root.geometry("500x600")
root.configure(bg="#001a33") 


titulo = tk.Label(root, text="MINI OSU", font=("Arial", 26, "bold"), fg="white", bg="#001a33")
titulo.pack(pady=10)


label_tiempo = tk.Label(root, text="Tiempo: 300", font=("Arial", 18), fg="cyan", bg="#001a33")
label_tiempo.pack(anchor="w", padx=20)

label_puntuacion = tk.Label(root, text="Puntuación: 0", font=("Arial", 18), fg="cyan", bg="#001a33")
label_puntuacion.pack(anchor="w", padx=20, pady=(0, 10))

boton_inicio = tk.Button(root, text="Iniciar juego", font=("Arial", 18), command=iniciar_juego)
boton_inicio.pack(pady=10)

label_info = tk.Label(root, text="Haz clic en los círculos antes de que desaparezcan",
                      font=("Arial", 14), bg="#001a33", fg="white")
label_info.pack(pady=5)

canvas = tk.Canvas(root, width=500, height=450, bg="black")
canvas.pack()

root.mainloop()
