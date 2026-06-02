# pyrefly: ignore [missing-import]
"""
solver/gran_m.py
================
Implementación del método de la Gran M para problemas
de programación lineal con restricciones >= e =.

La Gran M penaliza las variables artificiales con un coeficiente
M muy grande, forzando al algoritmo a sacarlas de la base.

Autor: JD Puerta
Versión: 1.1 - Agregada información de pivote
"""

import numpy as np


M = 1e6  # Valor de la penalización (Gran M)


class GranM:
    """
    Resuelve problemas de programación lineal usando el método Gran M.

    Maneja los tres tipos de restricciones:
        - Tipo <= : se agrega variable de holgura (+s)
        - Tipo >= : se agrega variable de exceso (-s) y artificial (+a)
        - Tipo =  : se agrega solo variable artificial (+a)

    Attributes:
        c (np.ndarray): Coeficientes originales de la función objetivo.
        A (np.ndarray): Matriz de coeficientes de restricciones.
        b (np.ndarray): Vector de términos independientes.
        tipos (list): Lista de tipos de restricción ('<=', '>=', '=').
        modo (str): 'max' o 'min'.
        tableau (np.ndarray): Tableau aumentado con todas las variables.
        iteraciones (list): Tableaux guardados por iteración.
        info_pivotes (list): Lista con info de pivote de cada iteración.
        variables_base (list): Índices de variables básicas actuales.
        nombres_vars (list): Nombres de todas las variables del tableau.
        n_vars (int): Número de variables de decisión.
        n_restricciones (int): Número de restricciones.
        indices_artificiales (list): Índices de variables artificiales.
    """

    def __init__(self, c, A, b, tipos, modo='max'):
        """
        Inicializa el solver Gran M.

        Args:
            c (list): Coeficientes de la función objetivo.
            A (list): Matriz de restricciones (lista de listas).
            b (list): Términos independientes.
            tipos (list): Tipos de restricción por fila ('<=', '>=', '=').
            modo (str): 'max' para maximizar, 'min' para minimizar.
        """
        self.c_original = np.array(c, dtype=float)
        self.A = np.array(A, dtype=float)
        self.b = np.array(b, dtype=float)
        self.tipos = tipos
        self.modo = modo
        self.iteraciones = []
        self.info_pivotes = []  # Lista para guardar info de cada pivote
        self.estado = None
        self.indices_artificiales = []

        self.n_vars = len(c)
        self.n_restricciones = len(b)

        # Si es minimización convertimos a maximización
        self.signo = -1 if modo == 'min' else 1

        self._construir_tableau()

    def _construir_tableau(self):
        """
        Construye el tableau inicial con variables de holgura,
        exceso y artificiales según el tipo de cada restricción.

        Convención de columnas:
            [variables originales | holgura/exceso | artificiales | b]
        """
        n = self.n_vars
        m = self.n_restricciones

        # Contamos cuántas variables artificiales necesitamos
        n_artificiales = sum(1 for t in self.tipos if t in ('>=', '='))

        # Total de columnas: originales + holgura/exceso + artificiales + b
        total_vars = n + m + n_artificiales

        # Construimos la matriz del tableau fila por fila
        tableau = np.zeros((m, total_vars + 1))
        tableau[:, :n] = self.A
        tableau[:, -1] = self.b

        # Índice actual para holgura/exceso y artificiales
        idx_holgura = n
        idx_artificial = n + m
        self.variables_base = []
        self.nombres_vars = [f'x{i+1}' for i in range(n)]

        for i, tipo in enumerate(self.tipos):
            if tipo == '<=':
                # Variable de holgura: +s
                tableau[i, idx_holgura] = 1
                self.variables_base.append(idx_holgura)
                self.nombres_vars.append(f's{i+1}')

            elif tipo == '>=':
                # Variable de exceso: -s, y artificial: +a
                tableau[i, idx_holgura] = -1
                tableau[i, idx_artificial] = 1
                self.variables_base.append(idx_artificial)
                self.indices_artificiales.append(idx_artificial)
                self.nombres_vars.append(f's{i+1}')
                self.nombres_vars.append(f'a{i+1}')
                idx_artificial += 1

            elif tipo == '=':
                # Solo variable artificial: +a
                tableau[i, idx_artificial] = 1
                self.variables_base.append(idx_artificial)
                self.indices_artificiales.append(idx_artificial)
                self.nombres_vars.append(f'a{i+1}')
                idx_artificial += 1

            idx_holgura += 1

        # Construir fila objetivo con penalización M
        # Para maximizar: c original, artificiales con -M
        # Para minimizar: -c original, artificiales con -M
        fila_z = np.zeros(total_vars + 1)
        fila_z[:n] = -self.signo * self.c_original

        for idx in self.indices_artificiales:
            fila_z[idx] = M  # Penalización positiva en fila -Z

        self.tableau = np.vstack([tableau, fila_z])
        self.nombres_vars.append('Z')

        # Eliminar M de las filas donde hay artificiales en la base
        for i, var in enumerate(self.variables_base):
            if var in self.indices_artificiales:
                self.tableau[-1] -= M * self.tableau[i]

    def _columna_pivote(self):
        """
        Encuentra la columna pivote (coeficiente más negativo en fila Z).

        Returns:
            int: Índice de columna pivote, o -1 si es óptimo.
        """
        fila_z = self.tableau[-1, :-1]
        col = int(np.argmin(fila_z))
        if fila_z[col] >= -1e-9:
            return -1
        return col

    def _fila_pivote(self, col):
        """
        Encuentra la fila pivote por la prueba de razón mínima.

        Args:
            col (int): Índice de columna pivote.

        Returns:
            int: Índice de fila pivote, o -1 si no acotado.
        """
        m = self.n_restricciones
        columna = self.tableau[:-1, col]
        b_col = self.tableau[:-1, -1]

        min_razon = np.inf
        fila = -1

        for i in range(m):
            if columna[i] > 1e-9:
                razon = b_col[i] / columna[i]
                if razon < min_razon:
                    min_razon = razon
                    fila = i

        return fila

    def _obtener_nombre_variable(self, indice):
        """
        Obtiene el nombre de una variable según su índice.

        Args:
            indice (int): Índice de la variable.

        Returns:
            str: Nombre de la variable.
        """
        if indice < len(self.nombres_vars):
            return self.nombres_vars[indice]
        return f"v{indice}"

    def _pivotear(self, fila, col):
        """
        Realiza el pivoteo sobre el tableau.

        Args:
            fila (int): Fila pivote.
            col (int): Columna pivote.
        """
        self.tableau[fila] /= self.tableau[fila, col]

        for i in range(len(self.tableau)):
            if i != fila:
                self.tableau[i] -= self.tableau[i, col] * self.tableau[fila]

        self.variables_base[fila] = col

    def _verificar_factibilidad(self):
        """
        Verifica si alguna variable artificial quedó en la base
        con valor distinto de cero (problema no factible).

        Returns:
            bool: True si es factible, False si no lo es.
        """
        for i, var in enumerate(self.variables_base):
            if var in self.indices_artificiales:
                if abs(self.tableau[i, -1]) > 1e-6:
                    return False
        return True

    def resolver(self):
        """
        Ejecuta el algoritmo Gran M completo.

        Returns:
            dict: Diccionario con:
                - 'estado': 'optimo', 'no_acotado', 'no_factible'
                - 'solucion': valores de las variables de decisión
                - 'z': valor óptimo de la función objetivo
                - 'iteraciones': lista de tableaux por iteración
                - 'info_pivotes': lista con info de pivotes por iteración
                - 'nombres_vars': nombres de todas las variables
        """
        # Guardar tableau inicial
        self.iteraciones.append(self.tableau.copy())
        self.info_pivotes.append({
            'iteracion': 0,
            'variable_entrante': None,
            'variable_saliente': None,
            'columna_pivote': None,
            'fila_pivote': None
        })

        max_iter = 200
        iteracion = 1

        for _ in range(max_iter):
            col = self._columna_pivote()

            if col == -1:
                if not self._verificar_factibilidad():
                    self.estado = 'no_factible'
                else:
                    self.estado = 'optimo'
                break

            fila = self._fila_pivote(col)

            if fila == -1:
                self.estado = 'no_acotado'
                break

            # Guardar información del pivote antes de pivotear
            var_entrante = self._obtener_nombre_variable(col)
            var_saliente = self._obtener_nombre_variable(self.variables_base[fila])

            self._pivotear(fila, col)

            # Guardar información de esta iteración
            self.iteraciones.append(self.tableau.copy())
            self.info_pivotes.append({
                'iteracion': iteracion,
                'variable_entrante': var_entrante,
                'variable_saliente': var_saliente,
                'columna_pivote': col,
                'fila_pivote': fila
            })
            iteracion += 1
        else:
            if self.estado is None:
                self.estado = 'no_converge'

        # Extraer solución
        solucion = np.zeros(self.n_vars)
        for i, var in enumerate(self.variables_base):
            if var < self.n_vars:
                solucion[var] = self.tableau[i, -1]

        z = self.tableau[-1, -1]
        if self.modo == 'min':
            z = -z

        return {
            'estado': self.estado,
            'solucion': solucion,
            'z': z,
            'iteraciones': self.iteraciones,
            'nombres_vars': self.nombres_vars,
            'variables_base': self.variables_base,
            'info_pivotes': self.info_pivotes
        }