"""
gui/panel_resultado.py
======================
Panel derecho de la aplicación. Muestra iteraciones,
solución óptima, gráfica 2D y exportación PDF.

Autor: JD Puerta
Versión: 1.1 - Agregado resaltado de columna pivote y muestra variables entrada/salida
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
from utils.exportar_pdf import exportar_reporte
from utils.vertices_2d import (
    enumerar_vertices_factibles_2d,
    ordenar_vertices_poligono,
)
from solver.sensibilidad import (
    calcular_intervalo_bi,
    calcular_intervalo_ci,
    calcular_intervalos_ci_grafico,
    obtener_restricciones_disponibles,
    obtener_variables_basicas,
)


class PanelResultado(ttk.Frame):
    """
    Panel de resultados de la aplicación.

    Attributes:
        problema (dict): Datos del problema actual.
        resultado (dict): Resultado del solver actual.
        canvas_grafica: Canvas de matplotlib embebido.
    """

    def __init__(self, parent):
        super().__init__(parent, relief='flat', borderwidth=1)

        self.problema = None
        self.resultado = None
        self.canvas_grafica = None

        self._construir_panel()

    def _construir_panel(self):
        """Construye la estructura inicial del panel."""
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        ttk.Label(
            self,
            text="Resultados",
            style='Header.TLabel'
        ).grid(row=0, column=0, pady=(10, 5), padx=10, sticky='w')

        # Canvas con scrollbar
        self.canvas = tk.Canvas(
            self, bg='#f5f5f5', highlightthickness=0
        )
        self.scrollbar = ttk.Scrollbar(
            self, orient='vertical', command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=1, column=0, sticky='nsew')
        self.scrollbar.grid(row=1, column=1, sticky='ns')

        self.frame_scroll = ttk.Frame(self.canvas)
        self.frame_scroll.columnconfigure(0, weight=1)

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.frame_scroll, anchor='nw'
        )

        self.frame_scroll.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.bind('<MouseWheel>', self._on_mousewheel)

        # Mensaje inicial
        ttk.Label(
            self.frame_scroll,
            text="Los resultados aparecerán aquí\ndespués de resolver el problema.",
            foreground='gray',
            font=('Segoe UI', 11),
            background='#f5f5f5'
        ).pack(pady=60)

    def _on_frame_configure(self, event):
        """Actualiza la región de scroll."""
        self.canvas.configure(
            scrollregion=self.canvas.bbox('all')
        )

    def _on_canvas_configure(self, event):
        """Ajusta el ancho del frame interno al canvas."""
        self.canvas.itemconfig(
            self.canvas_window, width=event.width
        )

    def _on_mousewheel(self, event):
        """Permite scroll con la rueda del mouse."""
        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)), 'units'
        )

    def mostrar_resultado(self, problema, resultado):
        """
        Muestra los resultados del solver.

        Args:
            problema (dict): Datos del problema resuelto.
            resultado (dict): Resultado del solver.
        """
        self.problema = problema
        self.resultado = resultado

        for w in self.frame_scroll.winfo_children():
            w.destroy()

        self.canvas_grafica = None

        estado = resultado.get('estado')
        if estado is None:
            estado = 'no_converge'

        if estado == 'no_factible':
            self._mostrar_error(
                "Problema no factible",
                "No existe solución que satisfaga todas las restricciones."
            )
            return

        if estado == 'no_acotado':
            self._mostrar_error(
                "Problema no acotado",
                "La función objetivo crece indefinidamente."
            )
            return

        if estado == 'no_converge':
            self._mostrar_error(
                "Sin convergencia",
                "Se alcanzó el límite de iteraciones sin certificar optimalidad. "
                "Revise los tableaux o intente reformular el problema."
            )
            self._mostrar_iteraciones()
            return

        if estado != 'optimo':
            self._mostrar_error(
                "Estado desconocido",
                f"El solver devolvió el estado: {estado}"
            )
            return

        self._mostrar_solucion_optima()
        self._mostrar_iteraciones()
        self._mostrar_sensibilidad()

        if problema['n_vars'] == 2 and estado == 'optimo':
            self._mostrar_grafica_2d()
            self._mostrar_vertices()

        self._mostrar_boton_pdf()

    def _mostrar_error(self, titulo, mensaje):
        """Muestra mensaje de error en el panel."""
        ttk.Label(
            self.frame_scroll,
            text=f"⚠ {titulo}",
            foreground='orange',
            font=('Segoe UI', 13, 'bold'),
            background='#f5f5f5'
        ).pack(pady=(40, 5))

        ttk.Label(
            self.frame_scroll,
            text=mensaje,
            foreground='gray',
            font=('Segoe UI', 10),
            background='#f5f5f5'
        ).pack(pady=5)

    def _mostrar_solucion_optima(self):
        """Muestra la solución óptima."""
        frame = ttk.LabelFrame(
            self.frame_scroll, text="Solución óptima", padding=10
        )
        frame.pack(fill='x', pady=(0, 8), padx=8)

        modo = "Maximizar" if self.problema['modo'] == 'max' else "Minimizar"
        metodo = self.problema['metodo']

        ttk.Label(
            frame,
            text=f"{metodo}  —  {modo}",
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor='w', pady=(0, 8))

        solucion = self.resultado['solucion']
        z = self.resultado['z']

        grid = ttk.Frame(frame)
        grid.pack(anchor='w')

        for i, val in enumerate(solucion):
            ttk.Label(
                grid,
                text=f"x{i+1} =",
                font=('Segoe UI', 10, 'bold'),
                width=6
            ).grid(row=i, column=0, sticky='e', pady=2)

            ttk.Label(
                grid,
                text=f"{val:.6f}",
                width=14
            ).grid(row=i, column=1, sticky='w', pady=2, padx=(5, 0))

        ttk.Separator(frame, orient='horizontal').pack(
            fill='x', pady=8
        )

        fila_z = ttk.Frame(frame)
        fila_z.pack(anchor='w')

        ttk.Label(
            fila_z,
            text="Z óptimo =",
            font=('Segoe UI', 12, 'bold')
        ).pack(side='left')

        ttk.Label(
            fila_z,
            text=f"{z:.6f}",
            style='Z.TLabel'
        ).pack(side='left', padx=10)

    def _mostrar_iteraciones(self):
        """Muestra las iteraciones en pestañas con información de pivote."""
        frame = ttk.LabelFrame(
            self.frame_scroll,
            text="Iteraciones del tableau",
            padding=8
        )
        frame.pack(fill='x', pady=(0, 8), padx=8)

        notebook = ttk.Notebook(frame)
        notebook.pack(fill='x', pady=(0, 5))

        iteraciones = self.resultado['iteraciones']
        info_pivotes = self.resultado.get('info_pivotes', [])
        n_vars = self.problema['n_vars']
        nombres_vars = self.resultado.get('nombres_vars', None)

        for idx, tableau in enumerate(iteraciones):
            nombre = "Inicial" if idx == 0 else f"Iteración {idx}"
            tab = ttk.Frame(notebook, padding=5)
            notebook.add(tab, text=nombre)

            # Obtener info del pivote para esta iteración (si existe)
            info = info_pivotes[idx] if idx < len(info_pivotes) else None
            self._construir_tableau(tab, tableau, n_vars, idx, info, nombres_vars)

    def _construir_tableau(self, parent, tableau, n_vars, idx, info_pivote=None, nombres_vars=None):
        """
        Construye la tabla visual de un tableau con resaltado de columna pivote.

        Args:
            parent: Widget contenedor.
            tableau (np.ndarray): Matriz del tableau.
            n_vars (int): Número de variables de decisión.
            idx (int): Índice de la iteración.
            info_pivote (dict): Información del pivote de esta iteración.
            nombres_vars (list): Nombres de todas las variables (para Gran M).
        """
        n_cols = tableau.shape[1]
        n_filas = tableau.shape[0]

        # Generar encabezados
        encabezados = []
        if nombres_vars is not None:
            # Para Gran M, usar los nombres almacenados
            for j in range(n_cols - 1):
                if j < len(nombres_vars):
                    encabezados.append(nombres_vars[j])
                else:
                    encabezados.append(f'v{j+1}')
        else:
            # Para Simplex estándar
            for j in range(n_cols - 1):
                if j < n_vars:
                    encabezados.append(f'x{j+1}')
                else:
                    holgura = j - n_vars + 1
                    encabezados.append(f's{holgura}')
        encabezados.append('b')

        etiquetas = []
        for i in range(n_filas - 1):
            etiquetas.append(f'R{i+1}')
        etiquetas.append('Z')

        # Configuración de colores
        HEADER_BG = '#0f3460'
        CELL_BG = ['#1e3a5f', '#253045']
        PIVOT_COL_BG = '#e6b800'  # Color dorado para resaltar columna pivote
        PIVOT_ROW_BG = '#4a7c59'  # Color verde para resaltar fila pivote
        PIVOT_CELL_BG = '#ffd54f'  # Color para la celda pivote
        Z_BG = '#1a6b3c'
        FG = 'white'
        DARK_FG = '#1a1a1a'

        # Determinar columna y fila pivote
        col_pivote = info_pivote.get('columna_pivote') if info_pivote else None
        fila_pivote = info_pivote.get('fila_pivote') if info_pivote else None

        w = 7

        # Limpiar el parent antes de dibujar
        for widget in parent.winfo_children():
            widget.destroy()

        # Esquina vacía
        tk.Label(
            parent, text="", width=4,
            bg=HEADER_BG, fg=FG,
            font=('Segoe UI', 9, 'bold'),
            relief='flat', padx=3, pady=3
        ).grid(row=0, column=0, padx=1, pady=1)

        # Encabezados columnas
        for j, enc in enumerate(encabezados):
            bg = HEADER_BG
            if col_pivote is not None and j == col_pivote:
                bg = PIVOT_COL_BG  # Resaltar columna pivote en encabezado
            tk.Label(
                parent, text=enc, width=w,
                bg=bg, fg=FG if bg == HEADER_BG else DARK_FG,
                font=('Segoe UI', 9, 'bold'),
                relief='flat', padx=3, pady=3
            ).grid(row=0, column=j+1, padx=1, pady=1)

        # Mostrar información de variable entrante/saliente si existe (solo para iteraciones > 0)
        if info_pivote and info_pivote.get('variable_entrante') and idx > 0:
            info_frame = tk.Frame(parent, bg='#2b2b2b', pady=5, padx=5)
            info_frame.grid(row=n_filas + 1, column=0, columnspan=n_cols + 1,
                            pady=(10, 0), sticky='ew')
            
            tk.Label(
                info_frame,
                text=f"📥 Entra: {info_pivote['variable_entrante']}",
                bg='#2b2b2b', fg='#4fc3f7',
                font=('Segoe UI', 9, 'bold')
            ).pack(side='left', padx=10, expand=True)

            tk.Label(
                info_frame,
                text=f"📤 Sale: {info_pivote['variable_saliente']}",
                bg='#2b2b2b', fg='#ffb74d',
                font=('Segoe UI', 9, 'bold')
            ).pack(side='left', padx=10, expand=True)

        # Filas
        for i in range(n_filas):
            es_z = (i == n_filas - 1)

            # Etiqueta de fila
            row_bg = HEADER_BG
            if fila_pivote is not None and i == fila_pivote and not es_z:
                row_bg = PIVOT_ROW_BG
            tk.Label(
                parent, text=etiquetas[i], width=4,
                bg=row_bg, fg=FG,
                font=('Segoe UI', 9, 'bold'),
                relief='flat', padx=3, pady=3
            ).grid(row=i+1, column=0, padx=1, pady=1)

            for j in range(n_cols):
                val = tableau[i, j]
                es_col_b = (j == n_cols - 1)

                # Determinar color de fondo
                if col_pivote is not None and fila_pivote is not None and i == fila_pivote and j == col_pivote:
                    # Celda pivote: color especial
                    bg = PIVOT_CELL_BG
                    fg_color = DARK_FG
                    bold = True
                elif es_z and es_col_b:
                    bg = Z_BG
                    fg_color = FG
                    bold = True
                elif es_z or es_col_b:
                    bg = HEADER_BG
                    fg_color = FG
                    bold = True
                elif col_pivote is not None and j == col_pivote:
                    bg = PIVOT_COL_BG
                    fg_color = DARK_FG
                    bold = True
                else:
                    bg = CELL_BG[i % 2] if not es_z else HEADER_BG
                    fg_color = FG
                    bold = False

                font = ('Segoe UI', 9, 'bold') if bold else ('Segoe UI', 9)

                # Formatear el valor (mostrar M para valores grandes)
                if abs(val) > 1e5 and val != 0:
                    texto = "M"
                else:
                    texto = f"{val:.3f}"

                tk.Label(
                    parent,
                    text=texto,
                    width=w,
                    bg=bg, fg=fg_color,
                    font=font,
                    relief='flat', padx=3, pady=3
                ).grid(row=i+1, column=j+1, padx=1, pady=1)

    def _mostrar_sensibilidad(self):
        """
        Muestra análisis de sensibilidad: holguras, restricciones activas
        e intervalos de factibilidad (bi) u optimalidad (ci).
        """
        if self.resultado['estado'] != 'optimo':
            return

        frame = ttk.LabelFrame(
            self.frame_scroll,
            text="Análisis de sensibilidad",
            padding=8
        )
        frame.pack(fill='x', pady=(0, 8), padx=8)

        A = np.array(self.problema['A'])
        b = np.array(self.problema['b'])
        tipos = self.problema['tipos']
        x = np.array(self.resultado['solucion'])

        for i, (fila, bi, tipo) in enumerate(zip(A, b, tipos)):

            lhs = np.dot(fila, x)

            if tipo == '<=':
                holgura = bi - lhs
            else:
                holgura = lhs - bi

            activa = abs(holgura) < 1e-6

            estado = (
                "Restricción activa"
                if activa
                else "Restricción no activa"
            )

            color = '#d32f2f' if activa else '#388e3c'

            texto = (
                f"R{i+1} → "
                f"Holgura = {holgura:.4f} → "
                f"{estado}"
            )

            tk.Label(
                frame,
                text=texto,
                anchor='w',
                bg='#f5f5f5',
                fg=color,
                font=('Segoe UI', 10, 'bold')
            ).pack(fill='x', pady=2)

        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=8)

        controles = ttk.Frame(frame)
        controles.pack(fill='x', pady=(0, 6))

        ttk.Label(
            controles,
            text="Tipo de análisis:",
            font=('Segoe UI', 10)
        ).grid(row=0, column=0, sticky='w', padx=(0, 8), pady=4)

        self.tipo_analisis_var = tk.StringVar()
        self._opciones_tipo_analisis = self._obtener_opciones_tipo_analisis()
        self.tipo_analisis_var.set(self._opciones_tipo_analisis[0])
        tipo_combo = ttk.Combobox(
            controles,
            textvariable=self.tipo_analisis_var,
            values=self._opciones_tipo_analisis,
            state='readonly',
            width=42
        )
        tipo_combo.grid(row=0, column=1, sticky='w', pady=4)
        tipo_combo.bind(
            '<<ComboboxSelected>>',
            lambda _e: self._actualizar_opciones_sensibilidad()
        )

        self.label_elemento_sensibilidad = ttk.Label(
            controles,
            text="Elemento:",
            font=('Segoe UI', 10)
        )
        self.label_elemento_sensibilidad.grid(
            row=1, column=0, sticky='w', padx=(0, 8), pady=4
        )

        self.elemento_sensibilidad_var = tk.StringVar()
        self.elemento_sensibilidad_combo = ttk.Combobox(
            controles,
            textvariable=self.elemento_sensibilidad_var,
            state='readonly',
            width=20
        )
        self.elemento_sensibilidad_combo.grid(row=1, column=1, sticky='w', pady=4)

        self.label_info_grafico = ttk.Label(
            controles,
            text="",
            font=('Segoe UI', 9),
            foreground='gray',
            wraplength=420
        )
        self.label_info_grafico.grid(
            row=1, column=1, sticky='w', pady=4
        )

        ttk.Button(
            controles,
            text="Calcular",
            command=self._calcular_sensibilidad
        ).grid(row=2, column=0, columnspan=2, sticky='w', pady=(8, 4))

        self.label_resultado_sensibilidad = tk.Label(
            frame,
            text="",
            anchor='w',
            bg='#f5f5f5',
            fg='#1565c0',
            font=('Segoe UI', 10, 'bold'),
            wraplength=520,
            justify='left'
        )
        self.label_resultado_sensibilidad.pack(fill='x', pady=(4, 0))

        self._actualizar_opciones_sensibilidad()

    def _obtener_opciones_tipo_analisis(self):
        """Construye las opciones del tipo de análisis según el problema."""
        opciones = [
            'Análisis de recursos o requerimientos (bi)',
            'Análisis de coeficientes de costo (ci)',
        ]
        if self.problema['n_vars'] == 2:
            opciones.append(
                'Análisis gráfico de coeficientes (pendientes)'
            )
        return opciones

    def _tipo_analisis_es_bi(self):
        """Indica si el tipo de análisis seleccionado es para recursos (bi)."""
        return self.tipo_analisis_var.get().startswith('Análisis de recursos')

    def _tipo_analisis_es_grafico(self):
        """Indica si el análisis seleccionado es el método gráfico 2D."""
        return self.tipo_analisis_var.get().startswith('Análisis gráfico')

    def _actualizar_opciones_sensibilidad(self):
        """Actualiza la segunda lista según el tipo de análisis elegido."""
        if self._tipo_analisis_es_grafico():
            self.label_elemento_sensibilidad.grid_remove()
            self.elemento_sensibilidad_combo.grid_remove()
            self.label_info_grafico.grid()
            self.label_info_grafico.config(
                text=(
                    "Usa las pendientes de las restricciones activas "
                    "en el óptimo para calcular los intervalos de c₁ y c₂."
                )
            )
        else:
            self.label_info_grafico.grid_remove()
            self.label_elemento_sensibilidad.grid()
            self.elemento_sensibilidad_combo.grid()

            if self._tipo_analisis_es_bi():
                opciones = obtener_restricciones_disponibles(
                    self.problema['n_restricciones']
                )
            else:
                opciones = obtener_variables_basicas(
                    self.resultado['variables_base'],
                    self.problema['n_vars']
                )

            self.elemento_sensibilidad_combo['values'] = opciones
            if opciones:
                self.elemento_sensibilidad_var.set(opciones[0])
            else:
                self.elemento_sensibilidad_var.set('')

        self.label_resultado_sensibilidad.config(text='')

    def _calcular_sensibilidad(self):
        """Calcula y muestra el intervalo de sensibilidad seleccionado."""
        if self.resultado['estado'] != 'optimo':
            messagebox.showwarning(
                "Análisis no disponible",
                "El análisis de sensibilidad solo está disponible "
                "cuando existe una solución óptima."
            )
            return

        elemento = self.elemento_sensibilidad_var.get().strip()
        if not self._tipo_analisis_es_grafico() and not elemento:
            messagebox.showwarning(
                "Selección requerida",
                "Seleccione una restricción o variable básica."
            )
            return

        tableau_final = self.resultado['iteraciones'][-1]
        variables_base = self.resultado['variables_base']

        if self._tipo_analisis_es_grafico():
            if self.problema['n_vars'] != 2:
                messagebox.showwarning(
                    "Análisis no disponible",
                    "El análisis gráfico solo está disponible "
                    "para problemas con 2 variables."
                )
                return

            resultado_intervalo = calcular_intervalos_ci_grafico(
                self.problema['c'],
                self.resultado['solucion'],
                self.problema['A'],
                self.problema['b'],
                self.problema['tipos'],
                self.problema['modo'],
            )
        elif self._tipo_analisis_es_bi():
            indice = int(elemento[1:]) - 1
            resultado_intervalo = calcular_intervalo_bi(
                tableau_final,
                variables_base,
                indice,
                self.problema['A'],
                self.problema['b'],
                self.problema['tipos'],
            )
        else:
            indice = int(elemento[1:]) - 1
            resultado_intervalo = calcular_intervalo_ci(
                tableau_final,
                variables_base,
                indice,
                self.problema['c'],
                self.problema['n_vars'],
                self.problema['modo'],
            )

        self.label_resultado_sensibilidad.config(
            text=resultado_intervalo['mensaje']
        )

    def _mostrar_vertices(self):
        """Muestra los vértices factibles encontrados."""
        if not hasattr(self, 'vertices_factibles'):
            return

        frame = ttk.LabelFrame(
            self.frame_scroll,
            text="Vértices factibles",
            padding=8
        )
        frame.pack(fill='x', pady=(0, 8), padx=8)

        vertices = []

        for punto in self.vertices_factibles:
            px = round(float(punto[0]), 6)
            py = round(float(punto[1]), 6)

            if (px, py) not in vertices:
                vertices.append((px, py))

        vertices.sort()

        solucion = self.resultado['solucion']

        for i, (px, py) in enumerate(vertices):
            es_optimo = (
                abs(px - solucion[0]) < 1e-6
                and abs(py - solucion[1]) < 1e-6
            )

            texto = f"V{i+1} = ({px:.3f}, {py:.3f})"

            if es_optimo:
                texto += "   ★ Óptimo"

            color = '#d4af37' if es_optimo else '#1565c0'

            tk.Label(
                frame,
                text=texto,
                anchor='w',
                bg='#f5f5f5',
                fg=color,
                font=('Segoe UI', 10, 'bold')
            ).pack(fill='x', pady=2)

    def _mostrar_grafica_2d(self):
        """
        Muestra gráfica 2D de la región factible.
        Solo para problemas con 2 variables.
        """
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        frame = ttk.LabelFrame(
            self.frame_scroll,
            text="Región factible (2D)",
            padding=8
        )
        frame.pack(fill='x', pady=(0, 8), padx=8)

        A = np.array(self.problema['A'])
        b = np.array(self.problema['b'])
        solucion = self.resultado['solucion']
        tipos = self.problema['tipos']
        c = np.array(self.problema['c'])

        fig, ax = plt.subplots(figsize=(5, 4))
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#1e1e1e')

        x_max = max(
            max(b) * 1.2,
            solucion[0] * 1.5 + 2,
            solucion[1] * 1.5 + 2,
            10
        )

        x = np.linspace(0, x_max, 400)

        # Todos los vértices: intersecciones x₁=0, x₂=0 y cada frontera de restricción
        vertices = enumerar_vertices_factibles_2d(A, b, tipos)
        self.vertices_factibles = vertices

        puntos_poligono = ordenar_vertices_poligono(vertices)
        if puntos_poligono is not None:
            ax.fill(
                puntos_poligono[:, 0],
                puntos_poligono[:, 1],
                color='#4caf50',
                alpha=0.30,
                label='Región factible'
            )
        

        colores = ['#4fc3f7', '#81c784', '#ffb74d', '#e57373', '#ce93d8']

        for i, (fila, bi, tipo) in enumerate(zip(A, b, tipos)):
            a1, a2 = fila[0], fila[1]
            color = colores[i % len(colores)]

            if abs(a2) > 1e-9:
                y = (bi - a1 * x) / a2
                ax.plot(x, y, color=color, linewidth=1.5,
                        label=f'R{i+1}: {a1:.1f}x₁+{a2:.1f}x₂{tipo}{bi:.1f}')
            elif abs(a1) > 1e-9:
                xi = bi / a1
                ax.axvline(x=xi, color=color, linewidth=1.5,
                           label=f'R{i+1}: x₁{tipo}{xi:.1f}')

        # =====================================================
        # RECTA DE ISOUTILIDAD
        # =====================================================

        z_opt = self.resultado['z']

        if abs(c[1]) > 1e-9:

            y_z = (z_opt - c[0] * x) / c[1]

            ax.plot(
                x,
                y_z,
                '--',
                color='#ff4081',
                linewidth=2,
                label=f'Isoutilidad Z={z_opt:.2f}'
            )

        # Vértices factibles (morado; óptimo en dorado)
        vertice_morado_en_leyenda = False
        for px, py in vertices:
            es_optimo = (
                abs(px - solucion[0]) < 1e-6
                and abs(py - solucion[1]) < 1e-6
            )

            if es_optimo:
                ax.plot(
                    px, py, 'o',
                    color='#ffd54f', markersize=10, zorder=5,
                    label=f'Óptimo ({px:.2f},{py:.2f})'
                )
            else:
                etiqueta = 'Vértices' if not vertice_morado_en_leyenda else None
                ax.plot(
                    px, py, 'o',
                    color='#ab47bc', markersize=8, zorder=4,
                    markeredgecolor='#e1bee7', markeredgewidth=0.8,
                    label=etiqueta
                )
                vertice_morado_en_leyenda = True

            ax.annotate(
                f'({px:.2f}, {py:.2f})',
                (px, py),
                textcoords='offset points',
                xytext=(5, 5),
                fontsize=7,
                color='#f5f5f5',
                zorder=6,
            )

        # Pendientes extremas del análisis gráfico de sensibilidad
        sens_grafico = calcular_intervalos_ci_grafico(
            c, solucion, A, b, tipos, self.problema['modo']
        )
        if (
            sens_grafico['pendiente_min'] is not None
            and sens_grafico['pendiente_max'] is not None
        ):
            x0, y0 = solucion[0], solucion[1]
            for pendiente, etiqueta, color in (
                (sens_grafico['pendiente_min'], 'Pend. mín.', '#ff9800'),
                (sens_grafico['pendiente_max'], 'Pend. máx.', '#ff5722'),
            ):
                y_pend = y0 + pendiente * (x - x0)
                ax.plot(
                    x,
                    y_pend,
                    ':',
                    color=color,
                    linewidth=1.5,
                    alpha=0.85,
                    label=etiqueta,
                    zorder=3,
                )

        ax.set_xlim(0, x_max)
        ax.set_ylim(0, x_max)
        ax.set_xlabel('x₁', color='white')
        ax.set_ylabel('x₂', color='white')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('gray')
        ax.legend(fontsize=8, facecolor='#2b2b2b',
                  labelcolor='white', loc='upper right')
        ax.grid(True, color='gray', alpha=0.3)
        plt.tight_layout()

        self.canvas_grafica = FigureCanvasTkAgg(fig, master=frame)
        self.canvas_grafica.draw()
        self.canvas_grafica.get_tk_widget().pack(fill='x', padx=5, pady=5)
        plt.close(fig)

    def _mostrar_boton_pdf(self):
        """Botón para exportar PDF."""
        frame = ttk.Frame(self.frame_scroll)
        frame.pack(fill='x', pady=(0, 10), padx=8)

        ttk.Button(
            frame,
            text="📄  Exportar reporte PDF",
            command=self._exportar_pdf,
            style='Purple.TButton'
        ).pack(fill='x')

    def _exportar_pdf(self):
        """Diálogo para guardar y generar el PDF."""
        if not self.resultado:
            return

        ruta = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Guardar reporte PDF",
            initialfile="reporte_simplex.pdf"
        )

        if not ruta:
            return

        try:
            exportar_reporte(ruta, self.problema, self.resultado)
            messagebox.showinfo("Éxito", f"Reporte guardado en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error al exportar", str(e))