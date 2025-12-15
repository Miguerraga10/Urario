import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import messagebox, ttk, simpledialog, Menu
from Interfaces.Utils_GUI import *

class HorarioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Horarios")
        self.setup_variables()
        self.setup_frames()
        self.setup_widgets()
        self.setup_menu()
        self.actualizar_formulario_unal()
        self.actualizar_visibilidad_historial()
        self.materias = cargar_materias(self)
        self.actualizar_lista()

    def setup_variables(self):
        self.universidad_seleccionada = "UNAL"
        self.valores_unal = {'nivel': '', 'sede': '', 'facultad': '', 'carrera': ''}
        self.colores_materias = {}
        self.materias = []

    def setup_frames(self):
        self.frame_unal_formulario = tk.Frame(self.root)
        self.frame_udea_formulario = tk.Frame(self.root)
        # Solo uno estará visible a la vez
        self.frame_unal_formulario.grid(row=1, column=0, columnspan=4, pady=2, sticky="w")
        self.frame_udea_formulario.grid_forget()  # Oculto por defecto
        self.frame_datos = tk.Frame(self.root)
        self.frame_datos.grid(row=3, column=2, pady=10)
        self.setup_interval_widgets()  # Añadir los widgets de intervalos aquí
        self.setup_udea_formulario()

    def setup_interval_widgets(self):
        # Cargar intervalos libres desde archivo si existe
        try:
            import json
            if os.path.exists('intervalos_libres.json'):
                with open('intervalos_libres.json', 'r', encoding='utf-8') as f:
                    self.lista_horas_libres = json.load(f)
            else:
                self.lista_horas_libres = []
        except Exception as e:
            print(f"Error cargando intervalos_libres.json: {e}")
            self.lista_horas_libres = []
        # Materias
        tk.Label(self.frame_datos, text="Materias:").grid(row=0, column=0, padx=5)
        self.min_materias_entry = tk.Entry(self.frame_datos, width=5)
        self.min_materias_entry.insert(tk.END, "1")
        self.min_materias_entry.grid(row=0, column=1, padx=3)
        tk.Label(self.frame_datos, text="-").grid(row=0, column=2)
        self.max_materias_entry = tk.Entry(self.frame_datos, width=5)
        self.max_materias_entry.insert(tk.END, "10")
        self.max_materias_entry.grid(row=0, column=3, padx=3)
        # Créditos
        tk.Label(self.frame_datos, text="Créditos:").grid(row=1, column=0, padx=5)
        self.min_creditos_entry = tk.Entry(self.frame_datos, width=5)
        self.min_creditos_entry.insert(tk.END, "1")
        self.min_creditos_entry.grid(row=1, column=1, padx=3)
        tk.Label(self.frame_datos, text="-").grid(row=1, column=2)
        self.max_creditos_entry = tk.Entry(self.frame_datos, width=5)
        self.max_creditos_entry.insert(tk.END, "30")
        self.max_creditos_entry.grid(row=1, column=3, padx=3)
        # Horas de estudio
        tk.Label(self.frame_datos, text="Horas de estudio:").grid(row=2, column=0, padx=5)
        self.min_horas_entry = tk.Entry(self.frame_datos, width=5)
        self.min_horas_entry.insert(tk.END, "08:00")
        self.min_horas_entry.grid(row=2, column=1, padx=3)
        tk.Label(self.frame_datos, text="-").grid(row=2, column=2)
        self.max_horas_entry = tk.Entry(self.frame_datos, width=5)
        self.max_horas_entry.insert(tk.END, "20:00")
        self.max_horas_entry.grid(row=2, column=3, padx=3)
        # Días
        tk.Label(self.frame_datos, text="Días:").grid(row=3, column=0, padx=5)
        self.min_dias_entry = tk.Entry(self.frame_datos, width=5)
        self.min_dias_entry.insert(tk.END, "1")
        self.min_dias_entry.grid(row=3, column=1, padx=3)
        self.min_dias_entry.config(state='disabled')
        tk.Label(self.frame_datos, text="-").grid(row=3, column=2)
        self.max_dias_entry = tk.Entry(self.frame_datos, width=5)
        self.max_dias_entry.insert(tk.END, "5")
        self.max_dias_entry.grid(row=3, column=3, padx=3)

        # Horas libres obligatorias (a la derecha de la lista de materias)
        self.frame_horas_libres = tk.Frame(self.root)
        self.frame_horas_libres.grid(row=0, column=4, rowspan=8, padx=(10, 0), sticky="nsw")
        tk.Label(self.frame_horas_libres, text="Horas libres obligatorias:").pack(anchor="w", pady=(0, 5))
        self.listbox_horas_libres = tk.Listbox(self.frame_horas_libres, width=32, height=12)
        self.listbox_horas_libres.pack(pady=(0, 5))
        self.listbox_horas_libres.bind("<Button-3>", self.menu_hora_libre)
        self.listbox_horas_libres.bind("<Button-2>", self.menu_hora_libre)
        self.menu_hora_libre_popup = tk.Menu(self.frame_horas_libres, tearoff=0)
        self.menu_hora_libre_popup.add_command(label="Editar", command=self.editar_hora_libre)
        self.menu_hora_libre_popup.add_command(label="Eliminar", command=self.eliminar_hora_libre)
        self.btn_add_hora_libre = tk.Button(self.frame_horas_libres, text="Añadir intervalo", command=self.abrir_dialogo_hora_libre)
        self.btn_add_hora_libre.pack(pady=(0, 2), fill="x")
        self.btn_clear_horas_libres = tk.Button(self.frame_horas_libres, text="Eliminar todos", command=self.eliminar_todas_horas_libres)
        self.btn_clear_horas_libres.pack(pady=(0, 2), fill="x")
        # Mostrar los intervalos cargados en el Listbox
        self.actualizar_listbox_horas_libres()

    def actualizar_listbox_horas_libres(self):
        self.listbox_horas_libres.delete(0, tk.END)
        for h in self.lista_horas_libres:
            dias = ', '.join(h['dias'])
            self.listbox_horas_libres.insert(tk.END, f"{h['inicio']} - {h['fin']} ({dias})")
        # Guardar automáticamente al actualizar
        try:
            import json
            with open('intervalos_libres.json', 'w', encoding='utf-8') as f:
                json.dump(self.lista_horas_libres, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando intervalos_libres.json: {e}")

    def setup_udea_formulario(self):
        # Cargar facultades y carreras de UdeA
        import json
        with open("Datos/FacultadesUdeA.json", encoding="utf-8") as f:
            self.facultades_udea = json.load(f)
        with open("Datos/CarrerasUdeA.json", encoding="utf-8") as f:
            self.carreras_udea = json.load(f)
        # Widgets para UdeA
        tk.Label(self.frame_udea_formulario, text="Facultad UdeA:").grid(row=0, column=0, padx=5, sticky="w")
        self.combo_facultad_udea = ttk.Combobox(self.frame_udea_formulario, values=self.facultades_udea, state="readonly", width=30)
        self.combo_facultad_udea.grid(row=0, column=1, padx=5, sticky="w")
        self.combo_facultad_udea.bind("<<ComboboxSelected>>", self.actualizar_formulario_udea)
        tk.Label(self.frame_udea_formulario, text="Carrera UdeA:").grid(row=1, column=0, padx=5, sticky="w")
        self.combo_carrera_udea = ttk.Combobox(self.frame_udea_formulario, values=[], state="readonly", width=30)
        self.combo_carrera_udea.grid(row=1, column=1, padx=5, sticky="w")

    def abrir_dialogo_hora_libre(self, editar_idx=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("Añadir intervalo de hora libre" if editar_idx is None else "Editar intervalo de hora libre")
        tk.Label(dialog, text="Hora inicio (HH:MM):").grid(row=0, column=0, padx=5, pady=5)
        entry_inicio = tk.Entry(dialog, width=8)
        entry_inicio.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(dialog, text="Hora fin (HH:MM):").grid(row=1, column=0, padx=5, pady=5)
        entry_fin = tk.Entry(dialog, width=8)
        entry_fin.grid(row=1, column=1, padx=5, pady=5)
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        checks = []
        var_todos = tk.BooleanVar()
        def marcar_todos():
            for v, _ in checks:
                v.set(var_todos.get())
        chk_todos = tk.Checkbutton(dialog, text="Todos", variable=var_todos, command=marcar_todos)
        chk_todos.grid(row=2, column=0, padx=5, pady=5)
        for i, dia in enumerate(dias):
            var = tk.BooleanVar()
            chk = tk.Checkbutton(dialog, text=dia, variable=var)
            chk.grid(row=3 + i // 4, column=i % 4, padx=2, pady=2, sticky="w")
            checks.append((var, dia))
        if editar_idx is not None:
            h = self.lista_horas_libres[editar_idx]
            entry_inicio.insert(0, h['inicio'])
            entry_fin.insert(0, h['fin'])
            for v, d in checks:
                if d in h['dias']:
                    v.set(True)
        def guardar():
            inicio = entry_inicio.get().strip()
            fin = entry_fin.get().strip()
            dias_seleccionados = [d for v, d in checks if v.get()]
            if not inicio or not fin or not dias_seleccionados:
                messagebox.showerror("Error", "Debes ingresar hora inicio, hora fin y al menos un día.")
                return
            if editar_idx is not None:
                self.lista_horas_libres[editar_idx] = {
                    'inicio': inicio,
                    'fin': fin,
                    'dias': dias_seleccionados
                }
            else:
                self.lista_horas_libres.append({
                    'inicio': inicio,
                    'fin': fin,
                    'dias': dias_seleccionados
                })
            self.actualizar_listbox_horas_libres()
            dialog.destroy()
        btn_guardar = tk.Button(dialog, text="Guardar", command=guardar)
        btn_guardar.grid(row=6, column=0, columnspan=2, pady=10)

    def menu_hora_libre(self, event):
        try:
            idx = self.listbox_horas_libres.nearest(event.y)
            self.listbox_horas_libres.selection_clear(0, tk.END)
            self.listbox_horas_libres.selection_set(idx)
            self.menu_hora_libre_popup.tk_popup(event.x_root, event.y_root)
            self._hora_libre_idx = idx
        finally:
            self.menu_hora_libre_popup.grab_release()

    def editar_hora_libre(self):
        idx = getattr(self, '_hora_libre_idx', None)
        if idx is not None:
            self.abrir_dialogo_hora_libre(editar_idx=idx)

    def eliminar_hora_libre(self):
        idx = getattr(self, '_hora_libre_idx', None)
        if idx is not None:
            del self.lista_horas_libres[idx]
            self.actualizar_listbox_horas_libres()

    def eliminar_todas_horas_libres(self):
        self.lista_horas_libres.clear()
        self.actualizar_listbox_horas_libres()

    def setup_widgets(self):
        self.btn_universidad = tk.Button(self.root, text=f"Universidad: {self.universidad_seleccionada}", command=self.toggle_universidad)
        self.btn_universidad.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.btn_abrir_manual = tk.Button(self.root, text="Añadir manualmente", command=self.abrir_ventana_añadir_manual)
        self.btn_abrir_manual.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        self.chk_colores = tk.Checkbutton(self.root, text="Usar colores", command=self.alternar_colores)
        self.chk_colores.grid(row=4, column=0, columnspan=2, pady=5)
        self.chk_colores.select()
        self.chk_cupos = tk.Checkbutton(self.root, text="Verificar cupos", command=self.alternar_cupos)
        self.chk_cupos.grid(row=4, column=1, columnspan=2, pady=5)
        self.chk_cupos.select()
        self.chk_virtual = tk.Checkbutton(self.root, text="Materias virtuales", command=self.alternar_virtuales)
        self.chk_virtual.grid(row=5, column=0, columnspan=2, pady=5)
        self.chk_virtual.select()
        self.lista_materias = tk.Listbox(self.root, width=35, height=16)
        self.scrollbar_materias = tk.Scrollbar(self.root, orient="vertical", command=self.lista_materias.yview)
        self.lista_materias.config(yscrollcommand=self.scrollbar_materias.set)
        self.lista_materias.grid(row=0, column=2, rowspan=1, padx=(10,0))
        self.scrollbar_materias.grid(row=0, column=3, rowspan=1, sticky="ns")
        self.btn_clear = tk.Button(self.root, text="Eliminar Todos", command=self.limpiar_materias)
        self.btn_clear.grid(row=1, column=2, padx=5)
        self.btn_generate = tk.Button(self.root, text="Generar Horario", command=self.ejecutar)
        self.btn_generate.grid(row=6, column=0, columnspan=6, pady=10)
        self.btn_historial = tk.Button(self.root, text="Pegar Historial Académico", command=self.pegar_historial)
        self.btn_historial.grid(row=7, column=0, columnspan=6, pady=5)

    def setup_menu(self):
        self.menu_contextual = Menu(self.root, tearoff=0)
        self.menu_contextual.add_command(label="Tipo: ", state="disabled")
        self.menu_contextual.add_command(label="Cambiar Obligatoriedad", command=self.cambiar_obligatoriedad)
        self.menu_contextual.add_command(label="Modificar Nombre", command=self.modificar_nombre)
        self.menu_contextual.add_command(label="Modificar Créditos", command=self.modificar_creditos)
        self.menu_contextual.add_command(label="Eliminar", command=self.eliminar_seleccionada)
        self.lista_materias.bind("<Button-3>", self.mostrar_menu)
        self.lista_materias.bind("<Button-2>", self.mostrar_menu)
        self.root.bind("<Button-1>", self.deseleccionar_lista)

    # Métodos de ejemplo (debes completar con los de tu lógica actual)
    def toggle_universidad(self):
        self.universidad_seleccionada = "UdeA" if self.universidad_seleccionada == "UNAL" else "UNAL"
        self.btn_universidad.config(text=f"Universidad: {self.universidad_seleccionada}")
        self.actualizar_visibilidad_historial()
        self.actualizar_formulario_unal()
        self.actualizar_formulario_udea()

    def actualizar_formulario_unal(self):
        actualizar_formulario_unal(self)

    def actualizar_visibilidad_historial(self):
        actualizar_visibilidad_historial(self)

    def abrir_ventana_añadir_manual(self):
        abrir_ventana_añadir_manual(self)

    def alternar_colores(self):
        alternar_colores(self)

    def alternar_cupos(self):
        alternar_cupos(self)

    def alternar_virtuales(self):
        alternar_virtuales(self)

    def limpiar_materias(self):
        limpiar_materias(self)

    def ejecutar(self):
        intervalos = self.get_interval_values()
        # Pasar la lista de horas libres a la función de generación de horarios
        intervalos['horas_libres'] = self.lista_horas_libres if hasattr(self, 'lista_horas_libres') else []
        ejecutar(self, intervalos)

    def pegar_historial(self):
        pegar_historial(self)

    def actualizar_lista(self):
        actualizar_lista(self)

    def cambiar_obligatoriedad(self):
        cambiar_obligatoriedad(self)

    def modificar_nombre(self):
        modificar_nombre(self)

    def modificar_creditos(self):
        modificar_creditos(self)

    def eliminar_seleccionada(self):
        eliminar_seleccionada(self)

    def mostrar_menu(self, event):
        mostrar_menu(self, event)

    def deseleccionar_lista(self, event):
        deseleccionar_lista(self, event)

    def get_interval_values(self):
        return {
            'min_materias': int(self.min_materias_entry.get().strip()),
            'max_materias': int(self.max_materias_entry.get().strip()),
            'min_creditos': int(self.min_creditos_entry.get().strip()),
            'max_creditos': float(self.max_creditos_entry.get().strip()),
            'min_horas': self.min_horas_entry.get().strip(),
            'max_horas': self.max_horas_entry.get().strip(),
            'min_dias': int(self.min_dias_entry.get().strip()),
            'max_dias': int(self.max_dias_entry.get().strip()),
            'horas_libres': self.lista_horas_libres if hasattr(self, 'lista_horas_libres') else []
        }

    def actualizar_formulario_udea(self):
        if self.universidad_seleccionada == "UdeA":
            self.frame_unal_formulario.grid_forget()
            self.frame_udea_formulario.grid(row=1, column=0, columnspan=4, pady=2, sticky="w")
        else:
            self.frame_udea_formulario.grid_forget()
            self.frame_unal_formulario.grid(row=1, column=0, columnspan=4, pady=2, sticky="w")

# Para ejecutar la app desde M10horariosplus.py:
def main():
    root = tk.Tk()
    app = HorarioApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
