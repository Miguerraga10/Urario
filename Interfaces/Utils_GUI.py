import json
import pyperclip
from tkinter import messagebox, simpledialog
from Clases.Clase import Clase
from Clases.Grupo import Grupo
from Clases.Horario import Horario
from Clases.Materia import Materia
from Metodos.Metodos import extraer_informacion, guardar_materias
from Revisa_Materias import materias_posibles_desde_historial, cargar_materias_posibles_por_carrera
import random, os
import tkinter as tk
from tkinter import ttk
from constantes import niveles_unal, sedes_unal, facultades_unal, carreras_por_facultad

def determinar_sede_por_salon(lugar_original, es_udea=False):
    """
    Determina la sede/lugar basado en el formato del salón.
    
    Args:
        lugar_original (str): El lugar original del JSON
        es_udea (bool): True si es de UdeA, False si es Nacional
    
    Returns:
        str: La sede determinada
    """
    if es_udea:
        return "UdeA"
    
    lugar = lugar_original.upper().strip()
    
    # Si contiene "CURSOS DIRIGIDOS" o "VIRTUAL"
    if "CURSOS DIRIGIDOS" in lugar or "VIRTUAL" in lugar or "SEDE" in lugar:
        return "Virtual"
    
    # Si tiene formato con M antes del número (ej: M8-102, M7-502B, M12-401)
    import re
    patron_minas = r'\bM\d+-\d+[A-Z]*\b'
    if re.search(patron_minas, lugar):
        return "Minas"
    
    # Si no cumple las condiciones anteriores, es volador
    return "Volador"


def cargar_materias_desde_json(archivo_json):
    if not os.path.exists(archivo_json):
        with open(archivo_json, "w", encoding="utf-8") as f:
            json.dump([], f)
    with open(archivo_json, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            materias = [
                Materia(
                    nombre=m["nombre"],
                    codigo=m["codigo"],
                    tipologia=m["tipologia"],
                    creditos=m["creditos"],
                    facultad=m["facultad"],
                    carrera=m["carrera"],
                    fechaExtraccion=m["fechaExtraccion"],
                    cuposDisponibles=m["cuposDisponibles"],
                    grupos=[
                        Grupo(
                            grupo=g["grupo"],
                            horarios=[
                                Clase(
                                    nombre=h["materia"],
                                    dia=h["dia"],
                                    hora_inicio=h.get("hora_inicio", h.get("inicio")),
                                    hora_fin=h.get("hora_fin", h.get("fin")),
                                    lugar=determinar_sede_por_salon(h["lugar"])
                                ) for h in g["horarios"]
                            ],
                            creditos=m["creditos"],
                            cupos=g["cupos"],
                            profesor=g["profesor"],
                            duracion=g["duracion"],
                            jornada=g["jornada"]
                        ) for g in m["grupos"]
                    ],
                    obligatoria=m.get("obligatoria", False)
                ) for m in data
            ]
            return materias
        except json.JSONDecodeError:
            return []


def cargar_materias(self):
    # Intentar cargar desde la base de datos si está disponible (despliegue en Render + MongoDB)
    try:
        from web_app import db as web_db
        docs = web_db.get_all_materias()
        data = docs
    except Exception:
        archivo = os.path.join(os.path.dirname(__file__), '..', 'materias.json')
        if not os.path.exists(archivo):
            with open(archivo, "w", encoding="utf-8") as f:
                json.dump([], f)
        with open(archivo, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

    self.materias = [
        Materia(
            nombre=m["nombre"],
            codigo=m.get("codigo", ""),
            tipologia=m.get("tipologia", ""),
            creditos=m.get("creditos", 0),
            facultad=m.get("facultad", ""),
            carrera=m.get("carrera", ""),
            fechaExtraccion=m.get("fechaExtraccion", ""),
            cuposDisponibles=m.get("cuposDisponibles", 0),
            grupos=[
                Grupo(
                    grupo=g.get("grupo"),
                    horarios=[
                        Clase(
                            nombre=h.get("materia", m.get("nombre")),
                            dia=h.get("dia"),
                            hora_inicio=h.get("hora_inicio", h.get("inicio")),
                            hora_fin=h.get("hora_fin", h.get("fin")),
                            lugar=determinar_sede_por_salon(h.get("lugar"))
                        ) for h in g.get("horarios", [])
                    ],
                    creditos=m.get("creditos", 0),
                    cupos=g.get("cupos", 0),
                    profesor=g.get("profesor"),
                    duracion=g.get("duracion"),
                    jornada=g.get("jornada")
                ) for g in m.get("grupos", [])
            ],
            obligatoria=m.get("obligatoria", False)
        ) for m in data
    ]
    self.lista_materias.delete(0, 'end')
    for materia in self.materias:
        self.lista_materias.insert('end', f"{materia.nombre} - {materia.creditos} créditos")
    return self.materias

def actualizar_lista(self):
    self.lista_materias.delete(0, 'end')
    for materia in self.materias:
        self.lista_materias.insert('end', f"{materia.nombre} - {self.universidad_seleccionada} - {materia.creditos} créditos")

def alternar_colores(self):
    if not hasattr(self, 'usar_colores'):
        self.usar_colores = True
    self.usar_colores = not self.usar_colores

def alternar_cupos(self):
    if not hasattr(self, 'usar_cupos'):
        self.usar_cupos = True
    self.usar_cupos = not self.usar_cupos

def alternar_virtuales(self):
    if not hasattr(self, 'usar_virtuales'):
        self.usar_virtuales = True
    self.usar_virtuales = not self.usar_virtuales

def limpiar_materias(self):
    self.materias.clear()
    self.actualizar_lista()
    guardar_materias(self.materias)

def ejecutar(self, intervalos):
    # Importación local para evitar ciclo
    from M10horariosplus import generar_horarios
    generar_horarios(
        self.materias,
        mincreditos=intervalos['min_creditos'],
        maxcreditos=intervalos['max_creditos'],
        minmaterias=intervalos['min_materias'],
        maxmaterias=intervalos['max_materias'],
        hora_inicio=intervalos['min_horas'],
        hora_fin=intervalos['max_horas'],
        usar_cupos=getattr(self, 'usar_cupos', False),
        maxdias=intervalos['max_dias'],
        usar_virtuales=getattr(self, 'usar_virtuales', True),
        horas_libres=intervalos.get('horas_libres', [])
    )

def pegar_historial(self):
    texto = pyperclip.paste()
    if not texto.strip():
        messagebox.showwarning("Advertencia", "El portapapeles está vacío.")
        return []
    materias_aprobadas, _, _ = materias_posibles_desde_historial(texto)
    if materias_aprobadas:
        # No guardar en archivo del repo; el frontend web guardará en localStorage
        msg = f"Se detectaron las siguientes materias aprobadas:\n" + "\n".join(materias_aprobadas)
        try:
            messagebox.showinfo("Materias Aprobadas", msg)
        except Exception:
            pass
        return materias_aprobadas
    else:
        try:
            messagebox.showinfo("Materias Aprobadas", "No se detectaron materias aprobadas en el texto pegado.")
        except Exception:
            pass
        return []

def abrir_ventana_añadir_manual(self):
    ventana_manual = tk.Toplevel(self.root if hasattr(self, 'root') else self.lista_materias.master)
    ventana_manual.title("Añadir Materia Manualmente")
    ventana_manual.grab_set()

    text_input_manual = tk.Text(ventana_manual, height=16, width=40)
    text_input_manual.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
    try:
        texto_clipboard = pyperclip.paste()
        text_input_manual.insert('end', texto_clipboard)
    except Exception:
        pass

    estado_obligatoria = {'valor': True}
    def toggle_obligatoria_manual():
        estado_obligatoria['valor'] = not estado_obligatoria['valor']
        btn_obligatoria_manual.config(text="Obligatoria" if estado_obligatoria['valor'] else "Optativa")

    btn_obligatoria_manual = tk.Button(ventana_manual, text="Obligatoria", command=toggle_obligatoria_manual)
    btn_obligatoria_manual.grid(row=1, column=0, columnspan=2, pady=5)

    def agregar_materia_manual():
        texto = text_input_manual.get("1.0", 'end').strip()
        if not texto:
            messagebox.showwarning("Advertencia", "El campo de texto está vacío.")
            return
        materianueva = extraer_informacion(texto, estado_obligatoria['valor'], getattr(self, 'universidad_seleccionada', 'UNAL'))
        for materia in self.materias:
            if materia.nombre == materianueva.nombre:
                messagebox.showwarning("Advertencia", f"La materia '{materia.nombre}' ya está en la lista.")
                return
        self.materias.append(materianueva)
        self.actualizar_lista()
        guardar_materias(self.materias)
        ventana_manual.destroy()

    btn_add_manual = tk.Button(ventana_manual, text="Añadir Materia", command=agregar_materia_manual)
    btn_add_manual.grid(row=2, column=0, columnspan=2, pady=5)

def cambiar_obligatoriedad(self):
    index = self.lista_materias.curselection()[0]
    self.materias[index].obligatoria = not self.materias[index].obligatoria
    guardar_materias(self.materias)
    self.actualizar_lista()

def modificar_nombre(self):
    index = self.lista_materias.curselection()[0]
    nuevo_nombre = simpledialog.askstring("Modificar Nombre", "Ingrese el nuevo nombre de la materia:", initialvalue=self.materias[index].nombre)
    if nuevo_nombre:
        self.materias[index].nombre = nuevo_nombre
        for grupo in self.materias[index].grupos:
            for clase in grupo.clases:
                clase.materia = nuevo_nombre
        guardar_materias(self.materias)
        self.actualizar_lista()

def modificar_creditos(self):
    index = self.lista_materias.curselection()[0]
    nuevo_credito = simpledialog.askinteger("Modificar Créditos", "Ingrese el nuevo número de créditos:", initialvalue=self.materias[index].creditos, minvalue=1, maxvalue=10)
    if nuevo_credito is not None:
        self.materias[index].creditos = nuevo_credito
        for grupo in self.materias[index].grupos:
            grupo.creditos = nuevo_credito
        guardar_materias(self.materias)
        self.actualizar_lista()

def eliminar_seleccionada(self):
    index = self.lista_materias.curselection()[0]
    if messagebox.askyesno("Confirmar eliminación", f"¿Seguro que quieres eliminar '{self.materias[index].nombre}'?"):
        del self.materias[index]
        guardar_materias(self.materias)
        self.actualizar_lista()

def mostrar_menu(self, event):
    seleccion = self.lista_materias.curselection()
    if seleccion:
        indice = seleccion[0]
        materia = self.materias[indice]
        tipo_materia = "Obligatoria" if materia.obligatoria else "Optativa"
        self.menu_contextual.entryconfig(0, label=f"Tipo: {tipo_materia}")
        self.menu_contextual.post(event.x_root, event.y_root)

def deseleccionar_lista(self, event):
    widget = event.widget
    if widget != self.lista_materias:
        self.lista_materias.selection_clear(0, 'end')

def actualizar_formulario_unal(self):
    # Limpia el frame del formulario UNAL
    for widget in self.frame_unal_formulario.winfo_children():
        widget.destroy()
    if self.universidad_seleccionada == "UNAL":
        # Vertical layout: cada campo en una fila
        tk.Label(self.frame_unal_formulario, text="Nivel:").grid(row=0, column=0, sticky="w", padx=2, pady=1)
        nivel_var = tk.StringVar(value=self.valores_unal['nivel'])
        nivel_menu = ttk.Combobox(self.frame_unal_formulario, textvariable=nivel_var, values=niveles_unal, state="readonly", width=30)
        nivel_menu.grid(row=0, column=1, padx=2, pady=1)

        tk.Label(self.frame_unal_formulario, text="Sede:").grid(row=1, column=0, sticky="w", padx=2, pady=1)
        sede_var = tk.StringVar(value=self.valores_unal['sede'])
        sede_menu = ttk.Combobox(self.frame_unal_formulario, textvariable=sede_var, values=sedes_unal, state="readonly", width=30)
        sede_menu.grid(row=1, column=1, padx=2, pady=1)

        tk.Label(self.frame_unal_formulario, text="Facultad:").grid(row=2, column=0, sticky="w", padx=2, pady=1)
        facultad_var = tk.StringVar(value=self.valores_unal['facultad'])
        facultad_menu = ttk.Combobox(self.frame_unal_formulario, textvariable=facultad_var, values=facultades_unal, state="readonly", width=50)
        facultad_menu.grid(row=2, column=1, padx=2, pady=1)

        tk.Label(self.frame_unal_formulario, text="Carrera:").grid(row=3, column=0, sticky="w", padx=2, pady=1)
        carrera_var = tk.StringVar(value=self.valores_unal['carrera'])
        carrera_menu = ttk.Combobox(self.frame_unal_formulario, textvariable=carrera_var, values=[], state="readonly", width=50)
        carrera_menu.grid(row=3, column=1, padx=2, pady=1)

        def actualizar_carreras(*args):
            fac = facultad_var.get()
            carreras = carreras_por_facultad.get(fac, [])
            carrera_menu['values'] = carreras
            if carrera_var.get() not in carreras:
                carrera_var.set("")
        facultad_var.trace_add('write', actualizar_carreras)
        actualizar_carreras()

        def guardar_valores(*args):
            self.valores_unal['nivel'] = nivel_var.get()
            self.valores_unal['sede'] = sede_var.get()
            self.valores_unal['facultad'] = facultad_var.get()
            self.valores_unal['carrera'] = carrera_var.get()
        nivel_var.trace_add('write', guardar_valores)
        sede_var.trace_add('write', guardar_valores)
        facultad_var.trace_add('write', guardar_valores)
        carrera_var.trace_add('write', guardar_valores)

        def cargar_materias_posibles_si_carrera(*args):
            nombre_carrera = carrera_var.get()
            if nombre_carrera:
                try:
                    with open("Materias_Vistas.txt", "r", encoding="utf-8") as f:
                        materias_aprobadas = [linea.strip() for linea in f if linea.strip()]
                except Exception:
                    materias_aprobadas = []
                from Revisa_Materias import cargar_materias_posibles_por_carrera
                posibles, archivo_carrera = cargar_materias_posibles_por_carrera(nombre_carrera, materias_aprobadas)
                self.materias = cargar_materias(self)
                self.actualizar_lista()
                if posibles is not None:
                    messagebox.showinfo("Materias posibles", f"Materias posibles cargadas para la carrera '{nombre_carrera}'.")
                else:
                    messagebox.showwarning("Carrera no encontrada", f"No se encontró el archivo de la carrera '{nombre_carrera}'.")
        carrera_var.trace_add('write', cargar_materias_posibles_si_carrera)
    else:
        # Si no es UNAL, no mostrar nada
        pass

def obtener_color(materia, usar_colores, colores_materias=None):
    """
    Asigna un color único a cada materia si usar_colores es True.
    colores_materias: dict opcional para mantener consistencia de colores.
    """
    if not usar_colores:
        return "white"
    if colores_materias is None:
        colores_materias = {}
    if materia and materia not in colores_materias:
        colores_materias[materia] = "#{:02X}{:02X}{:02X}".format(random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))
    return colores_materias.get(materia, "white")

def actualizar_visibilidad_historial(self):
    # Muestra u oculta el botón de historial según la universidad seleccionada
    if hasattr(self, 'btn_historial'):
        if self.universidad_seleccionada == "UNAL":
            self.btn_historial.grid()
        else:
            self.btn_historial.grid_remove()

def obtener_facultades_por_sede(sede):
    with open(r'd:\Miguel\Universidad\Gen_Horario\sia-extractor-main\data\carreras.json', encoding='utf-8') as f:
        carreras_data = json.load(f)
    return sorted(set(item['facultad'] for item in carreras_data if item['sede'] == sede))

def obtener_carreras_por_facultad_nivel_sede(facultad, nivel, sede):
    with open(r'd:\Miguel\Universidad\Gen_Horario\sia-extractor-main\data\carreras.json', encoding='utf-8') as f:
        carreras_data = json.load(f)
    return [item['carrera'] for item in carreras_data if item['facultad'] == facultad and item['nivel'] == nivel and item['sede'] == sede]
