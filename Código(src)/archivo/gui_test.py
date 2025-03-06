import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedTk
from Base_Datos import conectar, leer_datos
import threading
import csv
import os

class ScreenerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screener 2025")
        self.root.geometry("1200x700")
        self.root.configure(bg="#1e1e1e")

        # Estilo moderno
        style = ttk.Style()
        style.theme_use("equilux")
        style.configure("TLabel", background="#1e1e1e", foreground="#ffffff")
        style.configure("TButton", background="#3a3a3a", foreground="#ffffff")
        style.configure("Treeview", background="#2a2a2a", foreground="#ffffff", fieldbackground="#2a2a2a")
        style.map("Treeview", background=[("selected", "#4a4a4a")])

        # Barra de menú
        menubar = tk.Menu(root, bg="#3a3a3a", fg="#ffffff")
        root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0, bg="#3a3a3a", fg="#ffffff")
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Exportar a CSV", command=self.exportar_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=root.quit)

        # Barra lateral con íconos (usamos texto como placeholder para íconos)
        self.sidebar = ttk.Frame(root, width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        ttk.Label(self.sidebar, text="Screener 2025", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Button(self.sidebar, text="🔄 Actualizar", command=self.actualizar_datos).pack(pady=5)
        ttk.Button(self.sidebar, text="🔍 Filtrar", command=self.filtrar_datos).pack(pady=5)
        ttk.Button(self.sidebar, text="ℹ️ Ver Noticia", command=self.mostrar_noticia).pack(pady=5)

        # Contenido principal
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Tabla de datos
        self.tree = ttk.Treeview(self.main_frame, columns=("Fecha", "Ticker", "Precio", "Cambio", "Volumen", "Categoria", "Noticia"), show="headings")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Ticker", text="Ticker")
        self.tree.heading("Precio", text="Precio")
        self.tree.heading("Cambio", text="Cambio %")
        self.tree.heading("Volumen", text="Volumen")
        self.tree.heading("Categoria", text="Categoría")
        self.tree.heading("Noticia", text="Noticia")
        self.tree.column("Noticia", width=300)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Cargar datos iniciales
        self.cargar_datos()

    def cargar_datos(self):
        """Carga datos de TablaFinviz en la tabla."""
        conn = conectar()
        if conn:
            datos = leer_datos(conn, "TablaFinviz")
            for item in self.tree.get_children():
                self.tree.delete(item)
            for fila in datos:
                self.tree.insert("", tk.END, values=(fila[0], fila[1], fila[2], fila[3], fila[4], fila[6], fila[7]))
            conn.close()

    def actualizar_datos(self):
        """Ejecuta buscar_tickers en un hilo separado."""
        threading.Thread(target=self._actualizar_datos_thread, daemon=True).start()

    def _actualizar_datos_thread(self):
        from main import buscar_tickers
        buscar_tickers()
        self.cargar_datos()

    def filtrar_datos(self):
        """Abre una ventana para filtrar datos avanzados."""
        filter_window = tk.Toplevel(self.root)
        filter_window.title("Filtrar Datos")
        filter_window.geometry("400x300")
        filter_window.configure(bg="#1e1e1e")

        ttk.Label(filter_window, text="Filtrar por:").pack(pady=5)
        # Filtro por Ticker
        ttk.Label(filter_window, text="Ticker:").pack(pady=2)
        ticker_entry = ttk.Entry(filter_window)
        ticker_entry.pack(pady=2)
        # Filtro por CambioPorcentaje
        ttk.Label(filter_window, text="Cambio % (ej. >5):").pack(pady=2)
        cambio_entry = ttk.Entry(filter_window)
        cambio_entry.pack(pady=2)
        # Filtro por Volumen
        ttk.Label(filter_window, text="Volumen (ej. >1000000):").pack(pady=2)
        volumen_entry = ttk.Entry(filter_window)
        volumen_entry.pack(pady=2)

        ttk.Button(filter_window, text="Aplicar Filtro", command=lambda: self.aplicar_filtro(
            ticker_entry.get(), cambio_entry.get(), volumen_entry.get()
        )).pack(pady=10)

    def aplicar_filtro(self, ticker, cambio, volumen):
        """Filtra datos según criterios."""
        conn = conectar()
        if conn:
            condiciones = []
            if ticker:
                condiciones.append(f"Ticker LIKE '%{ticker}%'")
            if cambio:
                try:
                    valor = float(cambio.strip("><="))
                    operador = cambio[0] if cambio[0] in "><=" else "="
                    condiciones.append(f"CAST(CambioPorcentaje AS FLOAT) {operador} {valor}")
                except ValueError:
                    messagebox.showerror("Error", "Cambio % debe ser un número válido (ej. >5)")
                    return
            if volumen:
                try:
                    valor = int(volumen.strip("><=").replace(",", ""))
                    operador = volumen[0] if volumen[0] in "><=" else "="
                    condiciones.append(f"CAST(REPLACE(Volumen, ',', '') AS BIGINT) {operador} {valor}")
                except ValueError:
                    messagebox.showerror("Error", "Volumen debe ser un número válido (ej. >1000000)")
                    return

            query = " AND ".join(condiciones) if condiciones else None
            datos = leer_datos(conn, "TablaFinviz", query)
            for item in self.tree.get_children():
                self.tree.delete(item)
            for fila in datos:
                self.tree.insert("", tk.END, values=(fila[0], fila[1], fila[2], fila[3], fila[4], fila[6], fila[7]))
            conn.close()

    def mostrar_noticia(self):
        """Muestra la noticia seleccionada en una ventana."""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            noticia = item["values"][6]  # Columna Noticia
            noticia_window = tk.Toplevel(self.root)
            noticia_window.title("Noticia")
            noticia_window.geometry("500x300")
            noticia_window.configure(bg="#1e1e1e")
            ttk.Label(noticia_window, text="Noticia", font=("Arial", 12, "bold")).pack(pady=5)
            noticia_text = tk.Text(noticia_window, height=10, bg="#2a2a2a", fg="#ffffff", wrap="word")
            noticia_text.insert(tk.END, noticia)
            noticia_text.config(state="disabled")
            noticia_text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        else:
            messagebox.showinfo("Info", "Selecciona un ticker para ver su noticia.")

    def exportar_csv(self):
        """Exporta los datos de la tabla a un archivo CSV."""
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filepath:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Fecha", "Ticker", "Precio", "Cambio %", "Volumen", "Categoría", "Noticia"])
                for item in self.tree.get_children():
                    writer.writerow(self.tree.item(item)["values"])
            messagebox.showinfo("Éxito", f"Datos exportados a {filepath}")

if __name__ == "__main__":
    root = ThemedTk(theme="equilux")
    app = ScreenerApp(root)
    root.mainloop()