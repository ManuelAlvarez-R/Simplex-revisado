"""
solver/simplex.py
=================
Implementación del método Simplex estándar para problemas
de programación lineal (maximización y minimización).

Autor: JD Puerta
Versión: 1.1 - Agregada información de pivote
"""

import numpy as np


class Simplex:
    """
    Resuelve problemas de programación lineal usando el método Simplex.

    El problema debe estar en forma estándar:
        Maximizar o minimizar: Z = c^T * x
        Sujeto a: Ax <= b (restricciones de tipo <=)

    Para minimizar se convierte a maximización multiplicando c por -1.

    Attributes:
        c (np.ndarray): Coeficientes de la función objetivo.
        A (np.ndarray): Matriz de coeficientes de restricciones.
        b (np.ndarray): Vector de términos independientes.
        modo (str): 'max' o 'min'.
        tableau (np.ndarray): Tableau simplex aumentado.
        iteraciones (list): Lista de dicts con info de cada iteración.
        variables_base (list): Índices de variables básicas actuales.
        n_vars (int): Número de variables de decisión.
        n_restricciones (int): Número de restricciones.
        info_pivotes (list): Lista con info de pivote de cada iteración.
    """

    def __init__(self, c, A, b, modo='max'):
        """
        Inicializa el solver Simplex.

        Args:
            c (list): Coeficientes de la función objetivo.
            A (list): Matriz de restricciones (lista de listas).
            b (list): Términos independientes.
            modo (str): 'max' para maximizar, 'min' para minimizar.
        """
        self.c = np.array(c, dtype=float)
        self.A = np.array(A, dtype=float)
        self.b = np.array(b, dtype=float)
        self.modo = modo
        self.iteraciones = []
        self.info_pivotes = []  # Lista para guardar info de cada pivote
        self.estado = None  # 'optimo', 'no_acotado', 'no_converge'

        self.n_vars = len(c)
        self.n_restricciones = len(b)

        # Si es minimización, convertimos a maximización
        if modo == 'min':
            self.c = -self.c

        self._construir_tableau()

    def _construir_tableau(self):
        """
        Construye el tableau inicial agregando variables de holgura.

        Para cada restricción Ax <= b se agrega una variable de holgura s_i >= 0,
        de modo que Ax + s = b. La base inicial son las variables de holgura.
        """
        n = self.n_vars
        m = self.n_restricciones

        # Matriz identidad para variables de holgura
        holgura = np.eye(m)

        # Tableau: [A | I | b]
        tableau = np.hstack([self.A, holgura, self.b.reshape(-1, 1)])

        # Fila objetivo: [-c | 0...0 | 0]
        fila_z = np.hstack([-self.c, np.zeros(m), [0]])

        self.tableau = np.vstack([tableau, fila_z])

        # Las variables básicas iniciales son las de holgura
        # Sus índices van de n_vars hasta n_vars + n_restricciones - 1
        self.variables_base = list(range(n, n + m))

    def _columna_pivote(self):
        """
        Encuentra la columna pivote (variable entrante).

        Criterio: columna con el coeficiente más negativo en la fila Z.

        Returns:
            int: Índice de la columna pivote, o -1 si no hay negativos (óptimo).
        """
        fila_z = self.tableau[-1, :-1]
        col = int(np.argmin(fila_z))
        if fila_z[col] >= -1e-9:
            return -1  # Solución óptima alcanzada
        return col

    def _fila_pivote(self, col):
        """
        Encuentra la fila pivote usando la prueba de la razón mínima.

        Args:
            col (int): Índice de la columna pivote.

        Returns:
            int: Índice de la fila pivote, o -1 si el problema es no acotado.
        """
        m = self.n_restricciones
        columna = self.tableau[:-1, col]
        b_col = self.tableau[:-1, -1]

        razones = []
        for i in range(m):
            if columna[i] > 1e-9:
                razones.append((b_col[i] / columna[i], i))
            else:
                razones.append((np.inf, i))

        min_razon = min(razones, key=lambda x: x[0])

        if min_razon[0] == np.inf:
            return -1  # Problema no acotado

        return min_razon[1]

    def _obtener_nombre_variable(self, indice):
        """
        Obtiene el nombre de una variable según su índice.

        Args:
            indice (int): Índice de la variable.

        Returns:
            str: Nombre de la variable.
        """
        if indice < self.n_vars:
            return f"x{indice + 1}"
        else:
            holgura = indice - self.n_vars
            return f"s{holgura + 1}"

    def _pivotear(self, fila, col):
        """
        Realiza la operación de pivoteo sobre el tableau.

        Args:
            fila (int): Índice de la fila pivote.
            col (int): Índice de la columna pivote.
        """
        # Normalizar la fila pivote
        self.tableau[fila] = self.tableau[fila] / self.tableau[fila, col]

        # Eliminar en las demás filas
        for i in range(len(self.tableau)):
            if i != fila:
                self.tableau[i] = (
                    self.tableau[i]
                    - self.tableau[i, col] * self.tableau[fila]
                )

        # Actualizar variable básica
        self.variables_base[fila] = col

    def resolver(self):
        """
        Ejecuta el algoritmo Simplex completo.

        Returns:
            dict: Diccionario con:
                - 'estado': 'optimo', 'no_acotado'
                - 'solucion': valores de las variables de decisión
                - 'z': valor óptimo de la función objetivo
                - 'iteraciones': lista de tableaux por iteración
                - 'info_pivotes': lista con info de pivotes por iteración
        """
        # Guardamos el tableau inicial
        self.iteraciones.append(self.tableau.copy())
        self.info_pivotes.append({
            'iteracion': 0,
            'variable_entrante': None,
            'variable_saliente': None,
            'columna_pivote': None,
            'fila_pivote': None
        })

        max_iter = 100  # Límite de seguridad para evitar ciclos
        iteracion = 1

        for _ in range(max_iter):
            col = self._columna_pivote()

            if col == -1:
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

        # Si era minimización, el valor de Z hay que invertirlo
        if self.modo == 'min':
            z = -z

        return {
            'estado': self.estado,
            'solucion': solucion,
            'z': z,
            'iteraciones': self.iteraciones,
            'variables_base': self.variables_base,
            'info_pivotes': self.info_pivotes
        }