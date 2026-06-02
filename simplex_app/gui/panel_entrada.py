"""
gui/panel_entrada.py
====================
Panel izquierdo con formulario dinámico para ingresar
el problema de programación lineal.

Autor: JD Puerta
Versión: 1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
from solver.simplex import Simplex
from solver.gran_m import GranM
from utils.validaciones import validar_problema_completo


TIPOS = ['<=', '>=', '=']


class PanelEntrada(ttk.Frame):
    """
    Panel de entrada con formulario dinámico.

    Attributes:
        callback_resolver (callable): Función llamada al resolver.
        n_vars (int): Número de variables actual.
        n_rest (int): Número de restricciones actual.
        entradas_fo (list): Campos de la función objetivo.
        filas_restricciones (list): Filas de coeficientes.
        selectores_tipo (list): Variables de tipo por restricción.
        entradas_b (list): Campos de términos independientes.
    """

    def __init__(self, parent, callback_resolver):
        super().__init__(parent, relief='flat', borderwidth=1)

        self.callback_resolver = callback_resolver
        self.n_vars = 2
        self.n_rest = 2
        self.entradas_fo = []
        self.filas_restricciones = []
        self.selectores_tipo = []
        self.entradas_b = []

        self._construir_panel()

    def _construir_panel(self):
        """Construye todos los elementos del panel."""
        self.columnconfigure(0, weight=1)

        ttk.Label(
            self,
            text="Configuración del problema",
            style='Header.TLabel'
        ).pack(pady=(10, 5), padx=10, anchor='w')

        self._seccion_dimensiones()
        self._seccion_metodo()
        self._seccion_objetivo()
        self._seccion_tabla()
        self._seccion_botones()

    def _seccion_dimensiones(self):
        """Sección para número de variables y restricciones."""
        frame = ttk.LabelFrame(self, text="Dimensiones", padding=8)
        frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame, text="Variables:").grid(
            row=0, column=0, padx=(0, 5), pady=3, sticky='w'
        )
        self.entry_vars = ttk.Entry(frame, width=5)
        self.entry_vars.insert(0, "2")
        self.entry_vars.grid(row=0, column=1, padx=5, pady=3)

        ttk.Label(frame, text="Restricciones:").grid(
            row=0, column=2, padx=5, pady=3, sticky='w'
        )
        self.entry_rest = ttk.Entry(frame, width=5)
        self.entry_rest.insert(0, "2")
        self.entry_rest.grid(row=0, column=3, padx=5, pady=3)

        ttk.Button(
            frame,
            text="Generar tabla",
            command=self._generar_tabla
        ).grid(row=1, column=0, columnspan=4, pady=(8, 0), sticky='ew')

    def _seccion_metodo(self):
        """Sección para seleccionar el método."""
        frame = ttk.LabelFrame(self, text="Método", padding=8)
        frame.pack(fill='x', padx=10, pady=5)

        self.metodo_var = tk.StringVar(value="simplex")

        self.radio_simplex = ttk.Radiobutton(
            frame,
            text="Simplex",
            variable=self.metodo_var,
            value="simplex"
        )
        self.radio_simplex.pack(side='left', padx=(0, 20))

        self.radio_gran_m = ttk.Radiobutton(
            frame,
            text="Gran M",
            variable=self.metodo_var,
            value="gran_m"
        )
        self.radio_gran_m.pack(side='left')

        self.label_aviso = ttk.Label(
            frame,
            text="⚠ Simplex solo acepta restricciones <=",
            style='Warn.TLabel'
        )

    def _seccion_objetivo(self):
        """Sección para maximizar o minimizar."""
        frame = ttk.LabelFrame(self, text="Objetivo", padding=8)
        frame.pack(fill='x', padx=10, pady=5)

        self.objetivo_var = tk.StringVar(value="max")

        ttk.Radiobutton(
            frame,
            text="Maximizar",
            variable=self.objetivo_var,
            value="max"
        ).pack(side='left', padx=(0, 20))

        ttk.Radiobutton(
            frame,
            text="Minimizar",
            variable=self.objetivo_var,
            value="min"
        ).pack(side='left')

    def _seccion_tabla(self):
        """Contenedor para la tabla dinámica."""
        self.frame_tabla = ttk.LabelFrame(
            self, text="Coeficientes", padding=8
        )
        self.frame_tabla.pack(fill='x', padx=10, pady=5)

        self.contenedor_tabla = ttk.Frame(self.frame_tabla)
        self.contenedor_tabla.pack(fill='x')

        self._generar_tabla()

    def _seccion_botones(self):
        """Botones de acción."""
        frame = ttk.Frame(self)
        frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(
            frame,
            text="▶  Resolver",
            command=self._resolver,
            style='Green.TButton'
        ).pack(fill='x', pady=(0, 5))

        ttk.Button(
            frame,
            text="🗑  Limpiar",
            command=self._limpiar
        ).pack(fill='x')

    def _generar_tabla(self):
        """Genera la tabla dinámica de coeficientes."""
        try:
            n_vars = int(self.entry_vars.get())
            n_rest = int(self.entry_rest.get())
            if n_vars < 1 or n_rest < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Error", "Ingresa números enteros positivos."
            )
            return

        self.n_vars = n_vars
        self.n_rest = n_rest

        for w in self.contenedor_tabla.winfo_children():
            w.destroy()

        self.entradas_fo = []
        self.filas_restricciones = []
        self.selectores_tipo = []
        self.entradas_b = []

        ew = 55

        # Encabezados
        ttk.Label(
            self.contenedor_tabla, text="", width=3
        ).grid(row=0, column=0)

        for j in range(n_vars):
            ttk.Label(
                self.contenedor_tabla,
                text=f"x{j+1}",
                width=6,
                anchor='center',
                font=('Segoe UI', 9, 'bold')
            ).grid(row=0, column=j+1, padx=2, pady=2)

        ttk.Label(
            self.contenedor_tabla,
            text="Tipo",
            width=6,
            anchor='center',
            font=('Segoe UI', 9, 'bold')
        ).grid(row=0, column=n_vars+1, padx=2)

        ttk.Label(
            self.contenedor_tabla,
            text="b",
            width=6,
            anchor='center',
            font=('Segoe UI', 9, 'bold')
        ).grid(row=0, column=n_vars+2, padx=2)

        # Fila función objetivo
        ttk.Label(
            self.contenedor_tabla,
            text="Z",
            font=('Segoe UI', 9, 'bold')
        ).grid(row=1, column=0, padx=2, pady=3)

        for j in range(n_vars):
            e = ttk.Entry(self.contenedor_tabla, width=6)
            e.insert(0, "0")
            e.grid(row=1, column=j+1, padx=2, pady=3)
            self.entradas_fo.append(e)

        # Filas de restricciones
        for i in range(n_rest):
            ttk.Label(
                self.contenedor_tabla,
                text=f"R{i+1}",
                font=('Segoe UI', 9, 'bold')
            ).grid(row=i+2, column=0, padx=2, pady=3)

            fila = []
            for j in range(n_vars):
                e = ttk.Entry(self.contenedor_tabla, width=6)
                e.insert(0, "0")
                e.grid(row=i+2, column=j+1, padx=2, pady=3)
                fila.append(e)
            self.filas_restricciones.append(fila)

            tipo_var = tk.StringVar(value="<=")
            selector = ttk.Combobox(
                self.contenedor_tabla,
                textvariable=tipo_var,
                values=TIPOS,
                width=4,
                state='readonly'
            )
            selector.grid(row=i+2, column=n_vars+1, padx=2, pady=3)
            selector.bind(
                '<<ComboboxSelected>>',
                lambda e: self._actualizar_metodos()
            )
            self.selectores_tipo.append(tipo_var)

            e_b = ttk.Entry(self.contenedor_tabla, width=6)
            e_b.insert(0, "0")
            e_b.grid(row=i+2, column=n_vars+2, padx=2, pady=3)
            self.entradas_b.append(e_b)

        self._actualizar_metodos()

    def _actualizar_metodos(self):
        """
        Activa o desactiva Simplex según los tipos de restricciones.
        Si hay >= o =, Simplex no aplica.
        """
        tipos = [v.get() for v in self.selectores_tipo]
        solo_menor_igual = all(t == '<=' for t in tipos)

        if solo_menor_igual:
            self.radio_simplex.configure(state='normal')
            self.label_aviso.pack_forget()
        else:
            self.radio_simplex.configure(state='disabled')
            self.metodo_var.set("gran_m")
            self.label_aviso.pack(anchor='w', pady=(5, 0))

    def _leer_datos(self):
        """Lee y convierte todos los valores del formulario."""
        c = [float(e.get().strip()) for e in self.entradas_fo]
        A = [
            [float(e.get().strip()) for e in fila]
            for fila in self.filas_restricciones
        ]
        b = [float(e.get().strip()) for e in self.entradas_b]
        tipos = [v.get() for v in self.selectores_tipo]
        return c, A, b, tipos

    def _resolver(self):
        """Valida, ejecuta el solver y llama al callback."""
        try:
            c_str = [e.get() for e in self.entradas_fo]
            A_str = [[e.get() for e in f] for f in self.filas_restricciones]
            b_str = [e.get() for e in self.entradas_b]
            tipos = [v.get() for v in self.selectores_tipo]

            ok, msg = validar_problema_completo(c_str, A_str, b_str, tipos)
            if not ok:
                messagebox.showerror("Error de validación", msg)
                return

            c, A, b, tipos = self._leer_datos()
            metodo = self.metodo_var.get()
            modo = self.objetivo_var.get()

            if metodo == 'simplex':
                solver = Simplex(c, A, b, modo=modo)
            else:
                solver = GranM(c, A, b, tipos, modo=modo)

            resultado = solver.resolver()

            problema = {
                'metodo': 'Simplex' if metodo == 'simplex' else 'Gran M',
                'modo': modo,
                'c': c,
                'n_vars': self.n_vars,
                'n_restricciones': self.n_rest,
                'A': A,
                'b': b,
                'tipos': tipos
            }

            self.callback_resolver(problema, resultado)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _limpiar(self):
        """Limpia todos los campos de la tabla."""
        for e in self.entradas_fo:
            e.delete(0, 'end')
            e.insert(0, "0")
        for fila in self.filas_restricciones:
            for e in fila:
                e.delete(0, 'end')
                e.insert(0, "0")
        for e in self.entradas_b:
            e.delete(0, 'end')
            e.insert(0, "0")
