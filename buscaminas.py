import tkinter as tk
from tkinter import messagebox
import random
import time

# Patrón de diseño Observer
class Observer:
    def update(self):
        pass


# Lógica del juego Buscaminas
class LogicaJuegoBuscaminas:
    def __init__(self, n=8, minas_no=8):
        self.n = n
        self.minas_no = minas_no
        self.numeros = [[0 for _ in range(n)] for _ in range(n)]
        self.valores_celda = [[' ' for _ in range(n)] for _ in range(n)]
        self.flags = []
        self.terminado = False
        self.tiempo_inicio = 0
        self.observers = []
        self.configurar_minas()
        self.configurar_valores()

     # Método para agregar observadores
    def attach(self, observer):
        self.observers.append(observer)

    # Método para notificar a los observadores
    def notify_observers(self):
        for observer in self.observers:
            observer.update()

    def configurar_minas(self):
        count = 0
        while count < self.minas_no:
            val = random.randint(0, self.n * self.n - 1)
            r, col = divmod(val, self.n)
            if self.numeros[r][col] != -1:
                count += 1
                self.numeros[r][col] = -1

    def configurar_valores(self):
        for r in range(self.n):
            for col in range(self.n):
                if self.numeros[r][col] == -1:
                    continue
                if r > 0 and self.numeros[r - 1][col] == -1:
                    self.numeros[r][col] += 1
                if r < self.n - 1 and self.numeros[r + 1][col] == -1:
                    self.numeros[r][col] += 1
                if col > 0 and self.numeros[r][col - 1] == -1:
                    self.numeros[r][col] += 1
                if col < self.n - 1 and self.numeros[r][col + 1] == -1:
                    self.numeros[r][col] += 1
                if r > 0 and col > 0 and self.numeros[r - 1][col - 1] == -1:
                    self.numeros[r][col] += 1
                if r > 0 and col < self.n - 1 and self.numeros[r - 1][col + 1] == -1:
                    self.numeros[r][col] += 1
                if r < self.n - 1 and col > 0 and self.numeros[r + 1][col - 1] == -1:
                    self.numeros[r][col] += 1
                if r < self.n - 1 and col < self.n - 1 and self.numeros[r + 1][col + 1] == -1:
                    self.numeros[r][col] += 1

    def clic_celda(self, r, col):
        if not self.tiempo_inicio:
            self.tiempo_inicio = time.time()

        if self.terminado:
            return

        if [r, col] in self.flags:
            return

        if self.numeros[r][col] == -1:
            self.valores_celda[r][col] = 'M'
            self.mostrar_minas()
            self.mostrar_mensaje("Tocaste una mina. ¡Juego terminado!")
            self.terminado = True
        else:
            self.revelar_celda(r, col)
            self.verificar_fin_juego()
            self.notify_observers()

    def revelar_celda(self, r, col):
        if self.valores_celda[r][col] == ' ':
            if self.numeros[r][col] == 0:
                self.revelar_vecinos(r, col)
            else:
                self.valores_celda[r][col] = str(self.numeros[r][col])

    def revelar_vecinos(self, r, col):
        if 0 <= r < self.n and 0 <= col < self.n and self.valores_celda[r][col] == ' ':
            self.valores_celda[r][col] = str(self.numeros[r][col])
            if self.numeros[r][col] == 0:
                for i in range(max(0, r - 1), min(self.n, r + 2)):
                    for j in range(max(0, col - 1), min(self.n, col + 2)):
                        self.revelar_vecinos(i, j)

    def mostrar_minas(self):
        for r in range(self.n):
            for col in range(self.n):
                if self.numeros[r][col] == -1:
                    self.valores_celda[r][col] = 'M'

    def mostrar_mensaje(self, mensaje):
        messagebox.showinfo("Juego terminado", mensaje)

    def verificar_fin_juego(self):
        count_reveladas = sum(1 for r in range(self.n) for col in range(self.n) if self.valores_celda[r][col] != ' ')
        if count_reveladas == self.n * self.n - self.minas_no:
            self.mostrar_minas()
            tiempo_transcurrido = time.time() - self.tiempo_inicio
            self.mostrar_mensaje(f"¡Felicidades! ¡GANASTE!\nTiempo: {tiempo_transcurrido:.2f} segundos")
            self.terminado = True


# Interfaz de usuario Buscaminas
class InterfazUsuarioBuscaminas(tk.Tk, Observer):
    def __init__(self, logica_juego):
        super().__init__()
        self.title("Buscaminas")
        self.logica_juego = logica_juego
        self.logica_juego.attach(self)
        self.crear_widgets()

    def crear_widgets(self):
        self.botones = [[None for _ in range(self.logica_juego.n)] for _ in range(self.logica_juego.n)]

        for r in range(self.logica_juego.n):
            for col in range(self.logica_juego.n):
                boton = tk.Button(self, text="", width=3, height=2,
                                  command=lambda r=r, col=col: self.logica_juego.clic_celda(r, col))
                boton.grid(row=r, column=col)
                self.botones[r][col] = boton

        self.label_tiempo = tk.Label(self, text="Tiempo: 0.00 segundos")
        self.label_tiempo.grid(row=self.logica_juego.n, columnspan=self.logica_juego.n, sticky="w")

        self.boton_reiniciar = tk.Button(self, text="Reiniciar", command=self.reiniciar_juego)
        self.boton_reiniciar.grid(row=self.logica_juego.n + 1, columnspan=self.logica_juego.n, sticky="w")

        self.crear_temporizador()

    def update(self):
        for r in range(self.logica_juego.n):
            for col in range(self.logica_juego.n):
                self.botones[r][col].config(text=self.logica_juego.valores_celda[r][col],
                                            state=tk.DISABLED if self.logica_juego.terminado else tk.NORMAL)
        self.actualizar_temporizador()

    def crear_temporizador(self):
        self.after(100, self.actualizar_temporizador)

    def actualizar_temporizador(self):
        if self.logica_juego.tiempo_inicio and not self.logica_juego.terminado:
            tiempo_transcurrido = time.time() - self.logica_juego.tiempo_inicio
            self.label_tiempo.config(text=f"Tiempo: {tiempo_transcurrido:.2f} segundos")
            self.after(100, self.actualizar_temporizador)

    def reiniciar_juego(self):
        self.logica_juego = LogicaJuegoBuscaminas()
        self.logica_juego.attach(self)
        self.update()


def main():
    logica_juego = LogicaJuegoBuscaminas()
    interfaz_usuario = InterfazUsuarioBuscaminas(logica_juego)
    interfaz_usuario.mainloop()


if __name__ == "__main__":
    main()
