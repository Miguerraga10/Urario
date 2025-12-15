import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
import textwrap

def colores_futuristas():
    # Paleta de colores neón/futuristas
    return [
        "#00fff7",
        "#ff00ea",
        "#39ff14",
        "#faff00",
        "#ff005b",
        "#00b3ff",
        "#ff9100",
        "#a020f0",
        "#00ff85",
        "#ff61a6",
    ]

def mostrar_horario(horario, materias, materias_seleccionadas_final, usar_colores):
    """Muestra la ventana con el horario generado y permite cambiar
    grupos de materias.
    
    """
    # Tema futurista
    app = tb.Window(themename="cyborg")
    colores_materias = {}
    paleta = colores_futuristas()
    def color_futuro(materia):
        if not usar_colores or not materia:
            return "#222831"  # fondo oscuro
        if materia not in colores_materias:
            colores_materias[materia] = paleta[len(colores_materias) % len(paleta)]
        return colores_materias[materia]

    def actualizar_horario(materia):
        grupo_seleccionado = grupo_vars[materia.nombre].get()
        # Buscar el grupo en grupos_originales si existe, si no, en grupos
        grupos_fuente = getattr(materia, 'grupos_originales', materia.grupos)
        grupo_nuevo = next((g for g in grupos_fuente if g.grupo == grupo_seleccionado), None)
        grupo_a_remover = next((g for g in horario.grupos if any(c.nombre == materia.nombre for c in g.horarios)), None)

        if grupo_a_remover:
            for clase in grupo_a_remover.horarios:
                horario.eliminar_clase(clase)

        if grupo_nuevo and not horario.verificar_grupo(grupo_nuevo):
            messagebox.showerror("Error", f"No se pudo agregar el grupo {grupo_nuevo.grupo} de {materia.nombre}. Verifica los conflictos de horario.")
            ventana.deiconify()
            grupo_vars[materia.nombre].set(materias_seleccionadas_dict.get(materia.nombre, ""))
            return
        elif grupo_nuevo:
            materias_seleccionadas_dict[materia.nombre] = grupo_nuevo.grupo
            horario.agregar_grupo(grupo_nuevo)

        actualizar_visualizacion(horario, usar_colores)

    def actualizar_visualizacion(horario, usar_colores):
        for widget in frame_horario.winfo_children():
            widget.destroy()

        dias_con_clases = [dia for dia in horario.dias if any(horario.dias[dia].values())]
        todas_las_horas = horario.horas()
        horas_con_clases = [hora for hora in todas_las_horas if any(horario.dias[dia].get(hora) for dia in dias_con_clases)]
        horas_rango = todas_las_horas[todas_las_horas.index(horas_con_clases[0]):todas_las_horas.index(horas_con_clases[-1]) + 1] if horas_con_clases else []

        tb.Label(frame_horario, text="Hora", font=("Orbitron", 11, "bold"), width=10, bootstyle=PRIMARY, borderwidth=1, relief="solid").grid(row=0, column=0, sticky="nsew")
        for i, dia in enumerate(dias_con_clases, start=1):
            tb.Label(frame_horario, text=dia, font=("Orbitron", 11, "bold"), bootstyle=INFO, borderwidth=1, relief="solid").grid(row=0, column=i, sticky="nsew")

        fila = 1
        i = 0
        while i < len(horas_rango):
            hora_inicio = horas_rango[i]
            span = 1
            while i + span < len(horas_rango) and all(horario.dias[dia].get(horas_rango[i]) == horario.dias[dia].get(horas_rango[i + span]) for dia in dias_con_clases):
                span += 1
            hora_fin = horas_rango[i + span] if i + span < len(horas_rango) else horas_rango[i + span - 1]
            tb.Label(frame_horario, text=f"{hora_inicio} - {hora_fin}", font=("Orbitron", 10), width=10, bootstyle=SECONDARY, borderwidth=1, relief="solid").grid(row=fila, column=0, sticky="nsew", rowspan=span)
            for j, dia in enumerate(dias_con_clases, start=1):
                materia = horario.dias[dia].get(hora_inicio, "")
                color = color_futuro(materia) if materia else "#23272e"
                if materia:
                    frame_celda = tb.Frame(frame_horario, borderwidth=1, relief="solid", style="TFrame")
                    frame_celda.grid(row=fila, column=j, sticky="nsew", rowspan=span)
                    tb.Label(frame_celda, text=textwrap.fill(materia, width=15), font=("Orbitron", 10, "bold"), background=color, foreground="#fff", bootstyle=INFO).pack(fill="both", expand=True)
                else:
                    tb.Label(frame_horario, text="", font=("Orbitron", 10), width=15, borderwidth=1, relief="solid", background=color, bootstyle=SECONDARY).grid(row=fila, column=j, sticky="nsew", rowspan=span)
            fila += span
            i += span
        frame_horario.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    ventana = tb.Toplevel(app)
    ventana.title("Horario Generado - Futurista")
    grupo_vars = {}
    # Construcción robusta del diccionario
    materias_seleccionadas_dict = {}
    for item in materias_seleccionadas_final:
        if isinstance(item, tuple) and len(item) == 2:
            nombre, grupo = item
            materias_seleccionadas_dict[nombre] = grupo
        elif hasattr(item, 'nombre') and hasattr(item, 'grupo'):
            materias_seleccionadas_dict[item.nombre] = item.grupo
    frame_principal = tb.Frame(ventana)
    frame_principal.pack(fill="both", expand=True)
    canvas = tb.Canvas(frame_principal, background="#181c22")
    scrollbar_y = tb.Scrollbar(frame_principal, orient="vertical", command=canvas.yview, bootstyle=PRIMARY)
    canvas.configure(yscrollcommand=scrollbar_y.set)
    scrollbar_y.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    frame_contenedor = tb.Frame(canvas, style="TFrame")
    canvas.create_window((0, 0), window=frame_contenedor, anchor="nw")
    frame_materias = tb.Frame(frame_contenedor, style="TFrame")
    frame_materias.pack(fill='x', padx=10, pady=5)
    tb.Label(frame_materias, text="Seleccionar Grupos:", font=("Orbitron", 11, "bold"), bootstyle=WARNING).pack(anchor="w")
    columnas = 4  # Más materias por fila
    frames_columnas = [tb.Frame(frame_materias, style="TFrame") for _ in range(columnas)]
    for f in frames_columnas:
        f.pack(side="left", fill="both", expand=True)
    for idx, materia in enumerate(materias):
        frame_opcion = tb.Frame(frames_columnas[idx % columnas], style="TFrame")
        frame_opcion.pack(fill='x', pady=2)
        tb.Label(frame_opcion, text=materia.nombre, font=("Orbitron", 10), bootstyle=PRIMARY, width=12).pack(side="left", padx=2)
        # Usar grupos_originales si existe, si no, usar grupos
        grupos_fuente = getattr(materia, 'grupos_originales', materia.grupos)
        grupos_disponibles = [""] + [grupo.grupo for grupo in grupos_fuente]
        valor_defecto = materias_seleccionadas_dict.get(materia.nombre, "")
        if valor_defecto not in grupos_disponibles:
            valor_defecto = ""
        var_grupo = tb.StringVar(ventana, value=valor_defecto)
        menu_grupo = tb.Combobox(frame_opcion, textvariable=var_grupo, values=grupos_disponibles, state="readonly", bootstyle=SUCCESS, width=7)
        menu_grupo.pack(side="left", padx=2)
        grupo_vars[materia.nombre] = var_grupo
        menu_grupo.bind("<<ComboboxSelected>>", lambda event, materia=materia: actualizar_horario(materia))
    frame_horario = tb.Frame(frame_contenedor, style="TFrame")
    frame_horario.pack(fill="both", expand=True)
    actualizar_visualizacion(horario, usar_colores)
    frame_contenedor.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
    app.mainloop()

def mostrar_horario_qt(horario, materias, materias_seleccionadas_final, usar_colores):
    """
    Versión PyQt6 de la ventana de horario, con colores futuristas y selección de grupos.
    """
    import sys
    from PyQt6.QtWidgets import (
        QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTableWidget, QTableWidgetItem, QWidget, QHeaderView, QGridLayout
    )
    from PyQt6.QtGui import QColor, QFont
    from PyQt6.QtCore import Qt

    colores_materias = {}
    paleta = colores_futuristas()
    def color_futuro(materia):
        if not usar_colores or not materia:
            return QColor("#222831")
        if materia not in colores_materias:
            colores_materias[materia] = paleta[len(colores_materias) % len(paleta)]
        return QColor(colores_materias[materia])

    class HorarioDialog(QDialog):
        def __init__(self, horario, materias, materias_seleccionadas_final):
            super().__init__()
            self.setWindowTitle("Horario Generado - Futurista (PyQt6)")
            self.setStyleSheet("background-color: #181c22; color: #fff;")
            self.horario = horario
            self.materias = materias
            self.materias_seleccionadas_dict = {}
            for item in materias_seleccionadas_final:
                if isinstance(item, tuple) and len(item) == 2:
                    nombre, grupo = item
                    self.materias_seleccionadas_dict[nombre] = grupo
                elif hasattr(item, 'nombre') and hasattr(item, 'grupo'):
                    self.materias_seleccionadas_dict[item.nombre] = item.grupo
            self.grupo_vars = {}
            self.init_ui()

        def init_ui(self):
            layout = QVBoxLayout()
            # Selector de grupos en 4 columnas, nombre y grupo en la misma fila
            selector_widget = QWidget()
            grid = QGridLayout()
            selector_widget.setLayout(grid)
            columnas = 4
            for idx, materia in enumerate(self.materias):
                row = idx // columnas
                col = idx % columnas
                subwidget = QWidget()
                sublayout = QHBoxLayout()
                subwidget.setLayout(sublayout)
                # Nombre compacto
                nombre_dos_lineas = "\n".join(textwrap.wrap(materia.nombre, width=14, max_lines=2, placeholder="..."))
                label = QLabel(nombre_dos_lineas)
                label.setFont(QFont("Orbitron", 9, QFont.Weight.Bold))
                label.setStyleSheet("color: #00fff7; min-width: 70px; max-width: 100px; padding: 0px;")
                combo = QComboBox()
                combo.setStyleSheet("background-color: #23272e; color: #fff; border: 1px solid #00fff7; min-width: 50px; max-width: 70px; padding: 0px;")
                # Usar grupos_originales si existe, si no, usar grupos
                grupos_fuente = getattr(materia, 'grupos_originales', materia.grupos)
                grupos_disponibles = ["-"] + [str(grupo.grupo) for grupo in grupos_fuente]
                combo.addItems(grupos_disponibles)
                valor_defecto = self.materias_seleccionadas_dict.get(materia.nombre, "-")
                if valor_defecto in grupos_disponibles:
                    combo.setCurrentText(valor_defecto)
                self.grupo_vars[materia.nombre] = combo
                combo.currentTextChanged.connect(lambda _, m=materia: self.actualizar_horario(m))
                sublayout.addWidget(label)
                sublayout.addWidget(combo)
                grid.addWidget(subwidget, row, col)
            layout.addWidget(selector_widget)
            # Tabla de horario
            self.table = QTableWidget()
            self.table.setStyleSheet("QTableWidget {background-color: #181c22; color: #fff;} QHeaderView::section {background-color: #23272e; color: #00fff7; font-weight: bold;} QTableWidget::item {padding: 2px;}")
            layout.addWidget(self.table)
            self.setLayout(layout)
            self.actualizar_visualizacion()

        def actualizar_horario(self, materia):
            grupo_seleccionado = self.grupo_vars[materia.nombre].currentText()
            grupo_a_remover = next((g for g in self.horario.grupos if any(c.nombre == materia.nombre for c in g.horarios)), None)
            if grupo_a_remover:
                for clase in grupo_a_remover.horarios:
                    self.horario.eliminar_clase(clase)
            if grupo_seleccionado == "-":
                # Si se selecciona vacío, solo eliminar y refrescar
                self.materias_seleccionadas_dict[materia.nombre] = "-"
                self.actualizar_visualizacion()
                return
            # Buscar el grupo en grupos_originales si existe, si no, en grupos
            grupos_fuente = getattr(materia, 'grupos_originales', materia.grupos)
            grupo_nuevo = next((g for g in grupos_fuente if str(g.grupo) == grupo_seleccionado), None)
            if grupo_nuevo and not self.horario.verificar_grupo(grupo_nuevo):
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", f"No se pudo agregar el grupo {grupo_nuevo.grupo} de {materia.nombre}. Verifica los conflictos de horario.")
                self.grupo_vars[materia.nombre].setCurrentText(self.materias_seleccionadas_dict.get(materia.nombre, "-"))
                return
            elif grupo_nuevo:
                self.materias_seleccionadas_dict[materia.nombre] = grupo_nuevo.grupo
                self.horario.agregar_grupo(grupo_nuevo)
            self.actualizar_visualizacion()

        def actualizar_visualizacion(self):
            self.table.clear()
            dias_con_clases = [dia for dia in self.horario.dias if any(self.horario.dias[dia].values())]
            todas_las_horas = self.horario.horas()
            horas_con_clases = [hora for hora in todas_las_horas if any(self.horario.dias[dia].get(hora) for dia in dias_con_clases)]
            if not horas_con_clases:
                self.table.setRowCount(0)
                self.table.setColumnCount(0)
                return
            horas_rango = todas_las_horas[todas_las_horas.index(horas_con_clases[0]):todas_las_horas.index(horas_con_clases[-1]) + 1]
            filas = []
            i = 0
            while i < len(horas_rango):
                hora_inicio = horas_rango[i]
                span = 1
                for j in range(i + 1, len(horas_rango)):
                    iguales = True
                    for dia in dias_con_clases:
                        mat1 = self.horario.dias[dia].get(horas_rango[i], "")
                        mat2 = self.horario.dias[dia].get(horas_rango[j], "")
                        if mat1 != mat2:
                            iguales = False
                            break
                    if iguales:
                        span += 1
                    else:
                        break
                # Corrección: la hora final debe ser la última hora del bloque
                hora_fin = horas_rango[i + span - 1] if (i + span - 1) < len(horas_rango) else horas_rango[-1]
                filas.append((hora_inicio, hora_fin, span, i))
                i += span
            self.table.setRowCount(len(filas))
            self.table.setColumnCount(len(dias_con_clases) + 1)
            self.table.setHorizontalHeaderLabels(["Hora"] + dias_con_clases)
            for row_idx, (hora_inicio, hora_fin, span, i_hora) in enumerate(filas):
                # Intervalo de hora
                if hora_inicio == hora_fin:
                    hora_texto = hora_inicio
                else:
                    idx_inicio = horas_rango.index(hora_inicio)
                    idx_fin = horas_rango.index(hora_fin)
                    if idx_fin + 1 < len(horas_rango):
                        hora_texto = f"{hora_inicio} - {horas_rango[idx_fin + 1]}"
                    else:
                        hora_texto = f"{hora_inicio} - {hora_fin}"
                item_hora = QTableWidgetItem(hora_texto)
                item_hora.setFont(QFont("Orbitron", 10, QFont.Weight.Bold))
                item_hora.setBackground(QColor("#23272e"))
                item_hora.setForeground(QColor("#00fff7"))
                item_hora.setFlags(item_hora.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, 0, item_hora)
                for col_idx, dia in enumerate(dias_con_clases, start=1):
                    materia = self.horario.dias[dia].get(hora_inicio, "")
                    # Mostrar nombre completo, con salto de línea cada 18 caracteres
                    if materia:
                        nombre_multilinea = "\n".join(textwrap.wrap(materia, width=18))
                    else:
                        nombre_multilinea = ""
                    item = QTableWidgetItem(nombre_multilinea)
                    color = color_futuro(materia) if materia else QColor("#23272e")
                    item.setBackground(color)
                    # Letra negra para materias, blanco para vacías
                    if materia:
                        item.setForeground(QColor("#000"))
                    else:
                        item.setForeground(QColor("#fff"))
                    font = QFont("Orbitron", 10, QFont.Weight.Bold)
                    item.setFont(font)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row_idx, col_idx, item)
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            for col in range(1, self.table.columnCount()):
                self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
            self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            self.table.resizeRowsToContents()
            self.table.resizeColumnsToContents()
            # Efecto de profundidad: solo bordes, sin box-shadow (no soportado en Qt)
            self.table.setStyleSheet(
                "QTableWidget {background-color: #181c22; color: #fff;} "
                "QHeaderView::section {background-color: #23272e; color: #00fff7; font-weight: bold;} "
                "QTableWidget::item:selected { background: #00fff7; color: #181c22; } "
            )
    app = QApplication.instance() or QApplication([])
    dlg = HorarioDialog(horario, materias, materias_seleccionadas_final)
    dlg.resize(1100, 650)
    dlg.exec()
